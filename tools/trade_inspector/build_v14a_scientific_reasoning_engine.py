#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V14A

Scientific Reasoning Engine.

Creates explicit scientific conclusions from V13A intelligence artifacts.

ASCII only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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


REASONING_FIELDS = [
    "reasoning_id",
    "reasoning_type",
    "hypothesis_id",
    "premise_ids",
    "premise_count",
    "inference_rule",
    "conclusion",
    "confidence",
    "reasoning_strength",
    "uncertainty",
    "supporting_evidence",
    "conflicting_evidence",
    "recommended_action",
    "reasoning_status",
    "reasoning_chain",
    "explainability",
    "created_at_utc",
]

FUSED_CONCLUSION_FIELDS = [
    "fused_conclusion_id",
    "hypothesis_id",
    "reasoning_ids",
    "reasoning_count",
    "dominant_reasoning_type",
    "final_conclusion",
    "final_recommendation",
    "combined_confidence",
    "combined_uncertainty",
    "combined_reasoning_strength",
    "fusion_status",
    "supporting_reasoning",
    "limiting_reasoning",
    "fusion_chain",
    "created_at_utc",
]

SUMMARY_FIELDS = ["metric", "value"]
MANIFEST_FIELDS = ["artifact", "path", "rows", "status"]


@dataclass(frozen=True)
class ReasoningObject:
    reasoning_type: str
    hypothesis_id: str
    premise_ids: list[str]
    inference_rule: str
    conclusion: str
    confidence: float
    reasoning_strength: float
    uncertainty: float
    supporting_evidence: str
    conflicting_evidence: str
    recommended_action: str
    reasoning_status: str
    reasoning_chain: str
    explainability: str

    def to_row(self) -> dict[str, Any]:
        return {
            "reasoning_id": stable_hash_id(
                "RSN-",
                [self.hypothesis_id, self.inference_rule, self.conclusion, self.premise_ids],
            ),
            "reasoning_type": self.reasoning_type,
            "hypothesis_id": self.hypothesis_id,
            "premise_ids": ";".join(self.premise_ids),
            "premise_count": len(self.premise_ids),
            "inference_rule": self.inference_rule,
            "conclusion": self.conclusion,
            "confidence": round(self.confidence, 4),
            "reasoning_strength": round(self.reasoning_strength, 4),
            "uncertainty": round(self.uncertainty, 4),
            "supporting_evidence": self.supporting_evidence,
            "conflicting_evidence": self.conflicting_evidence,
            "recommended_action": self.recommended_action,
            "reasoning_status": self.reasoning_status,
            "reasoning_chain": self.reasoning_chain,
            "explainability": self.explainability,
            "created_at_utc": now_utc(),
        }


def group_by(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        value = row.get(key, "")
        if value:
            out.setdefault(value, []).append(row)
    return out


def opportunity_by_hypothesis(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        hid = row.get("hypothesis_id", "")
        if not hid:
            continue
        current = out.get(hid)
        if current is None or to_float(row.get("opportunity_score")) > to_float(current.get("opportunity_score")):
            out[hid] = row
    return out


def knowledge_state_label(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "UNKNOWN"
    return rows[0].get("overall_knowledge_state", "UNKNOWN")


def high_uncertainty_rule(
    row: dict[str, str],
    opportunity: dict[str, str] | None,
    knowledge_state: str,
) -> ReasoningObject | None:
    uncertainty = to_float(row.get("scientific_uncertainty"))
    coverage = to_float(row.get("research_coverage_score"))

    if uncertainty < 45 and coverage >= 35:
        return None

    hid = row.get("hypothesis_id", "")
    opp_id = opportunity.get("opportunity_id", "") if opportunity else ""

    confidence = clamp(100.0 - uncertainty)
    strength = clamp((100.0 - coverage) * 0.55 + uncertainty * 0.45)

    return ReasoningObject(
        reasoning_type="INSUFFICIENT_EVIDENCE",
        hypothesis_id=hid,
        premise_ids=[x for x in [hid, opp_id, f"knowledge_state:{knowledge_state}"] if x],
        inference_rule="HIGH_UNCERTAINTY_REQUIRES_MORE_EVIDENCE",
        conclusion="Additional evidence is required before strong scientific conclusions are justified.",
        confidence=confidence,
        reasoning_strength=strength,
        uncertainty=uncertainty,
        supporting_evidence=f"uncertainty={uncertainty};coverage={coverage};knowledge_state={knowledge_state}",
        conflicting_evidence="none",
        recommended_action="collect_more_archives",
        reasoning_status="ACTIVE",
        reasoning_chain=f"Uncertainty({uncertainty}) -> Coverage({coverage}) -> Rule(HIGH_UNCERTAINTY_REQUIRES_MORE_EVIDENCE) -> Conclusion(COLLECT_MORE_ARCHIVES)",
        explainability="low_coverage_or_meaningful_uncertainty_prevents_strong_conclusion",
    )


def high_opportunity_rule(row: dict[str, str], opportunity: dict[str, str] | None) -> ReasoningObject | None:
    if opportunity is None:
        return None

    score = to_float(opportunity.get("opportunity_score"))
    priority = opportunity.get("scientific_priority", "")

    if score < 60:
        return None

    hid = row.get("hypothesis_id", "")
    uncertainty = to_float(row.get("scientific_uncertainty"))
    confidence = to_float(row.get("scientific_confidence"))

    return ReasoningObject(
        reasoning_type="HIGH_VALUE_NEXT_STEP",
        hypothesis_id=hid,
        premise_ids=[hid, opportunity.get("opportunity_id", "")],
        inference_rule="HIGH_OPPORTUNITY_PRIORITY",
        conclusion="This hypothesis has a high-value next research opportunity.",
        confidence=clamp(confidence + score * 0.10),
        reasoning_strength=clamp(score),
        uncertainty=uncertainty,
        supporting_evidence=f"opportunity_score={score};scientific_priority={priority}",
        conflicting_evidence="none",
        recommended_action=opportunity.get("recommended_experiment", "manual_review"),
        reasoning_status="ACTIVE",
        reasoning_chain=f"OpportunityScore({score}) -> Priority({priority}) -> Rule(HIGH_OPPORTUNITY_PRIORITY) -> Conclusion(PRIORITIZE_RESEARCH)",
        explainability=opportunity.get("positive_drivers", "high_opportunity_score"),
    )


def conflict_rule(row: dict[str, str], conflicts: list[dict[str, str]]) -> ReasoningObject | None:
    if not conflicts:
        return None

    hid = row.get("hypothesis_id", "")
    severity = max(to_float(c.get("conflict_severity_score")) for c in conflicts)
    uncertainty = to_float(row.get("scientific_uncertainty"))

    return ReasoningObject(
        reasoning_type="CONTRADICTED",
        hypothesis_id=hid,
        premise_ids=[hid] + [c.get("conflict_id", "") for c in conflicts],
        inference_rule="CONFLICT_PREVENTS_STRONG_CONCLUSION",
        conclusion="Existing conflicts prevent a strong scientific conclusion.",
        confidence=clamp(100.0 - severity),
        reasoning_strength=clamp(severity),
        uncertainty=clamp(max(uncertainty, severity)),
        supporting_evidence=f"conflict_count={len(conflicts)}",
        conflicting_evidence=";".join(c.get("conflict_reason", "") for c in conflicts),
        recommended_action="resolve_conflict_first",
        reasoning_status="BLOCKED",
        reasoning_chain=f"Conflicts({len(conflicts)}) -> Severity({severity}) -> Rule(CONFLICT_PREVENTS_STRONG_CONCLUSION) -> Conclusion(RESOLVE_CONFLICT)",
        explainability="conflicting_evidence_must_be_resolved_before_stronger_claims",
    )


def dependency_rule(row: dict[str, str], dependencies: list[dict[str, str]]) -> ReasoningObject | None:
    if not dependencies:
        return None

    hid = row.get("hypothesis_id", "")
    risk = max(to_float(d.get("dependency_risk_score")) for d in dependencies)
    uncertainty = to_float(row.get("scientific_uncertainty"))

    return ReasoningObject(
        reasoning_type="DEPENDENCY_BLOCKED",
        hypothesis_id=hid,
        premise_ids=[hid] + [d.get("dependency_id", "") for d in dependencies],
        inference_rule="DEPENDENCY_BLOCKS_PROGRESS",
        conclusion="A dependency must be resolved before this research path can progress.",
        confidence=clamp(100.0 - uncertainty),
        reasoning_strength=clamp(risk),
        uncertainty=uncertainty,
        supporting_evidence=f"dependency_count={len(dependencies)};max_dependency_risk={risk}",
        conflicting_evidence="none",
        recommended_action="resolve_dependency_first",
        reasoning_status="BLOCKED",
        reasoning_chain=f"Dependencies({len(dependencies)}) -> Risk({risk}) -> Rule(DEPENDENCY_BLOCKS_PROGRESS) -> Conclusion(RESOLVE_DEPENDENCY)",
        explainability="research_progress_is_blocked_by_unresolved_dependency",
    )


def consistency_rule(row: dict[str, str]) -> ReasoningObject | None:
    stability = to_float(row.get("evidence_stability"))
    confidence = to_float(row.get("scientific_confidence"))
    uncertainty = to_float(row.get("scientific_uncertainty"))
    coverage = to_float(row.get("research_coverage_score"))

    if stability < 70 or confidence < 60 or uncertainty > 40 or coverage < 50:
        return None

    hid = row.get("hypothesis_id", "")

    return ReasoningObject(
        reasoning_type="SUPPORTED",
        hypothesis_id=hid,
        premise_ids=[hid],
        inference_rule="CONSISTENT_EVIDENCE_SUPPORTS_HYPOTHESIS",
        conclusion="Current evidence supports increasing scientific confidence in this hypothesis.",
        confidence=confidence,
        reasoning_strength=clamp((stability + confidence + coverage + (100.0 - uncertainty)) / 4.0),
        uncertainty=uncertainty,
        supporting_evidence=f"stability={stability};confidence={confidence};coverage={coverage};uncertainty={uncertainty}",
        conflicting_evidence="none",
        recommended_action="prepare_validation_or_keep_priority",
        reasoning_status="ACTIVE",
        reasoning_chain=f"Stability({stability}) -> Confidence({confidence}) -> Coverage({coverage}) -> Rule(CONSISTENT_EVIDENCE_SUPPORTS_HYPOTHESIS) -> Conclusion(INCREASE_CONFIDENCE)",
        explainability="stable_confident_and_sufficiently_covered_evidence_supports_hypothesis",
    )


def build_reasoning(
    intelligence_rows: list[dict[str, str]],
    knowledge_state_rows: list[dict[str, str]],
    opportunity_rows: list[dict[str, str]],
    dependency_rows: list[dict[str, str]],
    conflict_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    knowledge_state = knowledge_state_label(knowledge_state_rows)
    opportunities = opportunity_by_hypothesis(opportunity_rows)
    deps = group_by(dependency_rows, "hypothesis_id")
    conflicts = group_by(conflict_rows, "hypothesis_id")

    objects: list[ReasoningObject] = []

    for row in intelligence_rows:
        hid = row.get("hypothesis_id", "")
        opportunity = opportunities.get(hid)

        for obj in [
            high_uncertainty_rule(row, opportunity, knowledge_state),
            high_opportunity_rule(row, opportunity),
            conflict_rule(row, conflicts.get(hid, [])),
            dependency_rule(row, deps.get(hid, [])),
            consistency_rule(row),
        ]:
            if obj is not None:
                objects.append(obj)

    rows = [obj.to_row() for obj in objects]
    rows.sort(key=lambda r: (-to_float(r["reasoning_strength"]), r["reasoning_id"]))
    return rows



def fuse_reasoning(reasoning_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for row in reasoning_rows:
        hid = str(row.get("hypothesis_id", ""))
        if hid:
            grouped.setdefault(hid, []).append(row)

    fused_rows: list[dict[str, Any]] = []

    for hid, rows in grouped.items():
        reasoning_ids = [str(r.get("reasoning_id", "")) for r in rows if r.get("reasoning_id")]
        types = [str(r.get("reasoning_type", "")) for r in rows]
        rules = [str(r.get("inference_rule", "")) for r in rows]

        avg_confidence = (
            sum(to_float(r.get("confidence")) for r in rows) / len(rows)
            if rows
            else 0.0
        )
        avg_uncertainty = (
            sum(to_float(r.get("uncertainty")) for r in rows) / len(rows)
            if rows
            else 0.0
        )
        max_strength = max((to_float(r.get("reasoning_strength")) for r in rows), default=0.0)

        has_insufficient = "INSUFFICIENT_EVIDENCE" in types
        has_high_value = "HIGH_VALUE_NEXT_STEP" in types
        has_conflict = "CONTRADICTED" in types
        has_dependency = "DEPENDENCY_BLOCKED" in types
        has_supported = "SUPPORTED" in types

        if has_conflict:
            dominant = "CONTRADICTED"
            conclusion = "Conflicts must be resolved before a strong scientific conclusion is justified."
            recommendation = "resolve_conflict_first"
            status = "BLOCKED_BY_CONFLICT"
            limiting = "conflict_prevents_strong_conclusion"
        elif has_dependency:
            dominant = "DEPENDENCY_BLOCKED"
            conclusion = "Dependencies must be resolved before this research path can progress."
            recommendation = "resolve_dependency_first"
            status = "BLOCKED_BY_DEPENDENCY"
            limiting = "dependency_blocks_progress"
        elif has_high_value and has_insufficient:
            dominant = "HIGH_VALUE_BUT_EVIDENCE_LIMITED"
            conclusion = "This is a high-value research path, but additional evidence is required before strong conclusions."
            recommendation = "collect_more_archives_then_recompute_v13a"
            status = "RESEARCH_READY_AFTER_EVIDENCE_EXPANSION"
            limiting = "insufficient_evidence_limits_immediate_conclusion"
        elif has_high_value:
            dominant = "HIGH_VALUE_NEXT_STEP"
            conclusion = "This hypothesis has a high-value next research opportunity."
            recommendation = "prioritize_research"
            status = "RESEARCH_READY"
            limiting = "none"
        elif has_supported:
            dominant = "SUPPORTED"
            conclusion = "Current evidence supports increasing scientific confidence in this hypothesis."
            recommendation = "prepare_validation_or_keep_priority"
            status = "SUPPORTED"
            limiting = "none"
        elif has_insufficient:
            dominant = "INSUFFICIENT_EVIDENCE"
            conclusion = "Additional evidence is required before strong scientific conclusions are justified."
            recommendation = "collect_more_archives"
            status = "NEEDS_MORE_EVIDENCE"
            limiting = "insufficient_evidence"
        else:
            dominant = "UNRESOLVED"
            conclusion = "No strong fused conclusion is available."
            recommendation = "manual_review"
            status = "UNRESOLVED"
            limiting = "no_dominant_reasoning"

        supporting = ";".join(sorted(set(types)))
        fusion_chain = (
            f"ReasoningTypes({','.join(sorted(set(types)))})"
            f" -> Rules({','.join(sorted(set(rules)))})"
            f" -> Dominant({dominant})"
            f" -> Recommendation({recommendation})"
        )

        fused_rows.append(
            {
                "fused_conclusion_id": stable_hash_id("FCON-", [hid, reasoning_ids, dominant, recommendation]),
                "hypothesis_id": hid,
                "reasoning_ids": ";".join(reasoning_ids),
                "reasoning_count": len(rows),
                "dominant_reasoning_type": dominant,
                "final_conclusion": conclusion,
                "final_recommendation": recommendation,
                "combined_confidence": round(clamp(avg_confidence), 4),
                "combined_uncertainty": round(clamp(avg_uncertainty), 4),
                "combined_reasoning_strength": round(clamp(max_strength), 4),
                "fusion_status": status,
                "supporting_reasoning": supporting,
                "limiting_reasoning": limiting,
                "fusion_chain": fusion_chain,
                "created_at_utc": now_utc(),
            }
        )

    fused_rows.sort(
        key=lambda r: (
            str(r["fusion_status"]),
            -to_float(r["combined_reasoning_strength"]),
            str(r["fused_conclusion_id"]),
        )
    )

    return fused_rows


def build_summary(rows: list[dict[str, Any]], fused_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = [
        {"metric": "reasoning_rows", "value": len(rows)},
        {"metric": "fused_conclusion_rows", "value": len(fused_rows)},
    ]

    type_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    rule_counts: dict[str, int] = {}

    for row in rows:
        type_counts[str(row["reasoning_type"])] = type_counts.get(str(row["reasoning_type"]), 0) + 1
        status_counts[str(row["reasoning_status"])] = status_counts.get(str(row["reasoning_status"]), 0) + 1
        rule_counts[str(row["inference_rule"])] = rule_counts.get(str(row["inference_rule"]), 0) + 1

    for key in sorted(type_counts):
        summary.append({"metric": f"reasoning_type_{key}", "value": type_counts[key]})
    for key in sorted(status_counts):
        summary.append({"metric": f"reasoning_status_{key}", "value": status_counts[key]})
    for key in sorted(rule_counts):
        summary.append({"metric": f"inference_rule_{key}", "value": rule_counts[key]})

    fusion_status_counts: dict[str, int] = {}
    for row in fused_rows:
        fusion_status_counts[str(row["fusion_status"])] = fusion_status_counts.get(str(row["fusion_status"]), 0) + 1

    for key in sorted(fusion_status_counts):
        summary.append({"metric": f"fusion_status_{key}", "value": fusion_status_counts[key]})

    return summary


def write_report(
    path: Path,
    reasoning_rows: list[dict[str, Any]],
    fused_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
) -> None:
    lines: list[str] = []
    lines.append("# V14A SCIENTIFIC REASONING ENGINE REPORT")
    lines.append("")
    lines.append(f"Date: {date.today().isoformat()}")
    lines.append("Scope: Trade Inspector V14A")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Create explicit scientific conclusions from V13A intelligence artifacts.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    for row in summary_rows:
        lines.append(f"| {row['metric']} | {row['value']} |")
    lines.append("")
    lines.append("## Fused Scientific Conclusions")
    lines.append("")
    lines.append("| rank | fused_conclusion_id | hypothesis | status | strength | recommendation |")
    lines.append("|---:|---|---|---|---:|---|")
    for i, row in enumerate(fused_rows[:20], 1):
        lines.append(
            f"| {i} | {row['fused_conclusion_id']} | {row['hypothesis_id']} | "
            f"{row['fusion_status']} | {row['combined_reasoning_strength']} | "
            f"{row['final_recommendation']} |"
        )
    lines.append("")

    lines.append("## Top Reasoning Objects")
    lines.append("")
    lines.append("| rank | reasoning_id | type | rule | hypothesis | strength | action |")
    lines.append("|---:|---|---|---|---|---:|---|")
    for i, row in enumerate(reasoning_rows[:20], 1):
        lines.append(
            f"| {i} | {row['reasoning_id']} | {row['reasoning_type']} | "
            f"{row['inference_rule']} | {row['hypothesis_id']} | "
            f"{row['reasoning_strength']} | {row['recommended_action']} |"
        )
    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- V14A does not execute experiments.")
    lines.append("- V14A does not modify strategy logic.")
    lines.append("- V14A only derives explicit scientific conclusions.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypothesis-intelligence", required=True)
    parser.add_argument("--knowledge-state", required=True)
    parser.add_argument("--research-opportunities", required=True)
    parser.add_argument("--relationship-graph", required=True)
    parser.add_argument("--dependency-graph", required=True)
    parser.add_argument("--conflict-network", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    intelligence_rows = read_csv(args.hypothesis_intelligence)
    knowledge_state_rows = read_csv(args.knowledge_state)
    opportunity_rows = read_csv(args.research_opportunities)
    relationship_rows = read_csv(args.relationship_graph)
    dependency_rows = read_csv(args.dependency_graph)
    conflict_rows = read_csv(args.conflict_network)

    reasoning_rows = build_reasoning(
        intelligence_rows,
        knowledge_state_rows,
        opportunity_rows,
        dependency_rows,
        conflict_rows,
    )
    fused_rows = fuse_reasoning(reasoning_rows)

    summary_rows = build_summary(reasoning_rows, fused_rows)

    reasoning_path = out_dir / "v14a_scientific_reasoning.csv"
    fused_path = out_dir / "v14a_fused_scientific_conclusions.csv"
    summary_path = out_dir / "v14a_reasoning_summary.csv"
    manifest_path = out_dir / "v14a_reasoning_manifest.csv"
    report_path = out_dir / f"V14A_SCIENTIFIC_REASONING_ENGINE_REPORT_{date.today().isoformat()}.md"

    write_csv(reasoning_path, reasoning_rows, REASONING_FIELDS)
    write_csv(fused_path, fused_rows, FUSED_CONCLUSION_FIELDS)
    write_csv(summary_path, summary_rows, SUMMARY_FIELDS)

    manifest_rows = [
        {"artifact": "v14a_scientific_reasoning.csv", "path": str(reasoning_path), "rows": len(reasoning_rows), "status": "created"},
        {"artifact": "v14a_fused_scientific_conclusions.csv", "path": str(fused_path), "rows": len(fused_rows), "status": "created"},
        {"artifact": "v14a_reasoning_summary.csv", "path": str(summary_path), "rows": len(summary_rows), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest_rows, MANIFEST_FIELDS)
    write_report(report_path, reasoning_rows, fused_rows, summary_rows)

    print("V14A scientific reasoning engine completed")
    print("hypothesis_intelligence_rows:", len(intelligence_rows))
    print("knowledge_state_rows:", len(knowledge_state_rows))
    print("research_opportunity_rows:", len(opportunity_rows))
    print("relationship_rows:", len(relationship_rows))
    print("dependency_rows:", len(dependency_rows))
    print("conflict_rows:", len(conflict_rows))
    print("reasoning_rows:", len(reasoning_rows))
    print("fused_conclusion_rows:", len(fused_rows))
    print("report:", report_path)
    print("csv:", reasoning_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
