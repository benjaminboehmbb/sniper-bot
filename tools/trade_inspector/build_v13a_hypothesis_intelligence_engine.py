#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V13A

Hypothesis Intelligence Engine.

Purpose:
- Convert V11/V12 research artifacts into hypothesis-level research intelligence.
- Separate raw metrics from derived intelligence.
- Estimate evidence, uncertainty, novelty, information gain, coverage, conflicts,
  dependencies, and recommended next action.
- Produce explainable research prioritization.

ASCII only.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
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
    pick,
    read_csv,
    stable_hash_id,
    to_float,
    to_int,
    write_csv,
)


INTELLIGENCE_FIELDS = [
    "hypothesis_id",
    "hypothesis_group",
    "object_type",
    "knowledge_score",
    "priority_score",
    "successful_validations",
    "failed_validations",
    "pending_validations",
    "blocked_events",
    "knowledge_updates",
    "research_status",
    "priority_class",
    "recommended_next_action_v11",
    "consistency_class",
    "maturity_level",
    "evolution_trend",
    "next_learning_need",
    "memory_count",
    "directive_count",
    "avg_memory_roi",
    "avg_director_confidence",
    "evidence_strength",
    "evidence_diversity",
    "evidence_stability",
    "evidence_freshness",
    "scientific_confidence",
    "scientific_uncertainty",
    "novelty_score",
    "information_gain_score",
    "research_coverage_score",
    "relationship_score",
    "dependency_risk_score",
    "conflict_severity_score",
    "research_cost_score",
    "expected_knowledge_gain",
    "global_intelligence_score",
    "research_priority",
    "risk_level",
    "recommended_next_action_v13a",
    "explainability_positive",
    "explainability_negative",
    "created_at_utc",
]

RELATIONSHIP_FIELDS = [
    "relationship_id",
    "source_hypothesis_id",
    "target_hypothesis_id",
    "relationship_class",
    "relationship_strength",
    "relationship_reason",
]

DEPENDENCY_FIELDS = [
    "dependency_id",
    "hypothesis_id",
    "dependency_type",
    "dependency_target",
    "dependency_risk_score",
    "dependency_reason",
]

CONFLICT_FIELDS = [
    "conflict_id",
    "hypothesis_id",
    "conflict_type",
    "conflict_severity_score",
    "conflict_reason",
]

GAP_FIELDS = [
    "gap_id",
    "hypothesis_id",
    "gap_type",
    "gap_score",
    "gap_reason",
    "recommended_resolution",
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
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "")
        if value:
            out[value] = row
    return out


def group_rows_by_source(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        value = row.get(key, "")
        if value:
            grouped[value].append(row)
    return grouped


def tokenize(text: str) -> set[str]:
    cleaned = text.lower()
    for ch in "_-/.,;:()[]{}":
        cleaned = cleaned.replace(ch, " ")
    stop = {
        "the", "and", "or", "for", "with", "good", "bad",
        "aligned", "quality", "filter", "group",
    }
    return {x for x in cleaned.split() if len(x) >= 3 and x not in stop}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def evidence_strength(row: dict[str, str]) -> float:
    knowledge = to_float(row.get("knowledge_score"))
    success = to_float(row.get("successful_validations"))
    failed = to_float(row.get("failed_validations"))
    pending = to_float(row.get("pending_validations"))
    updates = to_float(row.get("knowledge_updates"))

    validation_volume = min((success + failed + pending) * 12.0, 40.0)
    update_component = min(updates * 8.0, 20.0)
    return clamp((knowledge * 0.45) + validation_volume + update_component)


def evidence_stability(row: dict[str, str]) -> float:
    success = to_float(row.get("successful_validations"))
    failed = to_float(row.get("failed_validations"))
    blocked = to_float(row.get("blocked_events"))
    consistency = row.get("consistency_class", "")

    total = success + failed + blocked
    if total <= 0:
        base = 45.0
    else:
        base = 100.0 * (success + 0.5) / (total + 1.0)

    if "STRONG" in consistency:
        base += 15.0
    elif "WATCH" in consistency:
        base += 5.0
    elif "INCONSISTENT" in consistency or "REJECT" in consistency:
        base -= 25.0

    return clamp(base)


def evidence_diversity(memory_rows: list[dict[str, str]], directive_rows: list[dict[str, str]]) -> float:
    memory_types = {r.get("memory_type", "") for r in memory_rows if r.get("memory_type", "")}
    directive_types = {r.get("decision_type", "") for r in directive_rows if r.get("decision_type", "")}
    fields = {r.get("source_field", "") for r in memory_rows if r.get("source_field", "")}

    raw = (len(memory_types) * 20.0) + (len(directive_types) * 15.0) + (len(fields) * 10.0)
    return clamp(raw)


def evidence_freshness(row: dict[str, str]) -> float:
    status = row.get("research_status", "").lower()
    if "active" in status or "ready" in status:
        return 85.0
    if "pending" in status or "watch" in status:
        return 65.0
    if "blocked" in status:
        return 35.0
    return 55.0


def novelty_score(row: dict[str, str], memory_count: int, relationship_count: int) -> float:
    updates = to_float(row.get("knowledge_updates"))
    maturity = row.get("maturity_level", "")
    base = 80.0

    base -= min(updates * 8.0, 35.0)
    base -= min(memory_count * 5.0, 25.0)
    base -= min(relationship_count * 3.0, 20.0)

    if "MATURE" in maturity:
        base -= 20.0
    elif "EARLY" in maturity or "NEW" in maturity:
        base += 10.0

    return clamp(base)


def research_coverage_score(row: dict[str, str], memory_count: int, directive_count: int) -> float:
    updates = to_float(row.get("knowledge_updates"))
    success = to_float(row.get("successful_validations"))
    failed = to_float(row.get("failed_validations"))
    pending = to_float(row.get("pending_validations"))

    raw = (
        min(updates * 12.0, 35.0)
        + min((success + failed + pending) * 12.0, 35.0)
        + min(memory_count * 8.0, 20.0)
        + min(directive_count * 5.0, 10.0)
    )
    return clamp(raw)


def conflict_severity(row: dict[str, str]) -> float:
    failed = to_float(row.get("failed_validations"))
    blocked = to_float(row.get("blocked_events"))
    consistency = row.get("consistency_class", "")
    trend = row.get("evolution_trend", "")

    raw = min(failed * 20.0, 40.0) + min(blocked * 25.0, 35.0)

    if "INCONSISTENT" in consistency or "REJECT" in consistency:
        raw += 25.0
    if "DECLIN" in trend or "NEGATIVE" in trend:
        raw += 15.0

    return clamp(raw)


def dependency_risk(row: dict[str, str]) -> float:
    need = row.get("next_learning_need", "").lower()
    action = row.get("recommended_next_action", "").lower()

    raw = 10.0
    if "archive" in need or "archive" in action:
        raw += 25.0
    if "validation" in need or "validation" in action:
        raw += 15.0
    if "manual" in need or "manual" in action:
        raw += 20.0
    if "blocked" in action:
        raw += 30.0

    return clamp(raw)


def research_cost(memory_rows: list[dict[str, str]], directive_rows: list[dict[str, str]]) -> float:
    minutes = 0.0

    for row in memory_rows:
        minutes += to_float(row.get("total_estimated_runtime_minutes"))

    for row in directive_rows:
        minutes += to_float(row.get("estimated_runtime_minutes"))

    if minutes <= 0:
        return 30.0
    if minutes <= 30:
        return 25.0
    if minutes <= 120:
        return 45.0
    if minutes <= 360:
        return 65.0
    return 85.0


def scientific_confidence(strength: float, stability: float, diversity: float, freshness: float) -> float:
    return clamp(
        0.35 * strength
        + 0.30 * stability
        + 0.20 * diversity
        + 0.15 * freshness
    )


def scientific_uncertainty(
    confidence: float,
    conflict: float,
    dependency: float,
    coverage: float,
) -> float:
    return clamp(
        (100.0 - confidence) * 0.45
        + conflict * 0.25
        + dependency * 0.20
        + (100.0 - coverage) * 0.10
    )


def information_gain(
    novelty: float,
    uncertainty: float,
    coverage: float,
    conflict: float,
    cost: float,
) -> float:
    return clamp(
        novelty * 0.30
        + uncertainty * 0.30
        + (100.0 - coverage) * 0.20
        + conflict * 0.10
        + (100.0 - cost) * 0.10
    )


def relationship_score(relationship_count: int, duplicate_count: int, conflict_count: int) -> float:
    raw = min(relationship_count * 12.0, 70.0)
    raw -= min(duplicate_count * 15.0, 30.0)
    raw -= min(conflict_count * 10.0, 25.0)
    return clamp(raw)


def expected_knowledge_gain(info_gain: float, uncertainty: float, novelty: float, cost: float) -> float:
    return clamp(
        info_gain * 0.45
        + uncertainty * 0.25
        + novelty * 0.20
        + (100.0 - cost) * 0.10
    )


def global_score(
    strength: float,
    stability: float,
    novelty: float,
    info_gain: float,
    coverage: float,
    confidence: float,
    relationship: float,
    conflict: float,
    dependency: float,
    cost: float,
    ekg: float,
) -> float:
    return clamp(
        strength * 0.12
        + stability * 0.10
        + novelty * 0.10
        + info_gain * 0.16
        + coverage * 0.08
        + confidence * 0.14
        + relationship * 0.06
        + (100.0 - conflict) * 0.08
        + (100.0 - dependency) * 0.06
        + (100.0 - cost) * 0.04
        + ekg * 0.16
    )


def classify_priority(score: float, uncertainty: float, conflict: float) -> str:
    if conflict >= 75:
        return "CONFLICT_FIRST"
    if uncertainty >= 70:
        return "HIGH_UNCERTAINTY_RESEARCH"
    if score >= 80:
        return "PRIORITY_1"
    if score >= 65:
        return "PRIORITY_2"
    if score >= 45:
        return "WATCHLIST"
    return "LOW_PRIORITY"


def classify_risk(uncertainty: float, conflict: float, dependency: float) -> str:
    if conflict >= 75 or dependency >= 80:
        return "HIGH"
    if uncertainty >= 65 or conflict >= 45 or dependency >= 55:
        return "MEDIUM"
    return "LOW"


def recommend_action(
    priority: str,
    uncertainty: float,
    conflict: float,
    dependency: float,
    coverage: float,
    novelty: float,
) -> str:
    if conflict >= 75:
        return "resolve_conflict_first"
    if dependency >= 80:
        return "blocked_by_dependency"
    if coverage < 35:
        return "collect_more_archives"
    if uncertainty >= 70 and novelty >= 55:
        return "run_high_information_gain_experiment"
    if priority in {"PRIORITY_1", "PRIORITY_2"}:
        return "prepare_validation"
    if novelty < 25 and coverage >= 70:
        return "merge_or_deprioritize"
    return "watchlist"


def explain_positive(metrics: dict[str, float]) -> str:
    parts: list[str] = []

    if metrics["evidence_strength"] >= 70:
        parts.append("high_evidence_strength")
    if metrics["evidence_stability"] >= 70:
        parts.append("stable_evidence")
    if metrics["novelty_score"] >= 65:
        parts.append("high_novelty")
    if metrics["information_gain_score"] >= 65:
        parts.append("high_information_gain")
    if metrics["scientific_confidence"] >= 70:
        parts.append("high_scientific_confidence")
    if metrics["expected_knowledge_gain"] >= 65:
        parts.append("high_expected_knowledge_gain")

    return ";".join(parts) if parts else "no_strong_positive_driver"


def explain_negative(metrics: dict[str, float]) -> str:
    parts: list[str] = []

    if metrics["scientific_uncertainty"] >= 65:
        parts.append("high_uncertainty")
    if metrics["conflict_severity_score"] >= 45:
        parts.append("conflict_severity")
    if metrics["dependency_risk_score"] >= 55:
        parts.append("dependency_risk")
    if metrics["research_coverage_score"] < 35:
        parts.append("low_research_coverage")
    if metrics["research_cost_score"] >= 70:
        parts.append("high_research_cost")
    if metrics["novelty_score"] < 25:
        parts.append("low_novelty")

    return ";".join(parts) if parts else "no_strong_negative_driver"


def build_relationships(hypotheses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for i, a in enumerate(hypotheses):
        for b in hypotheses[i + 1:]:
            a_id = str(a["hypothesis_id"])
            b_id = str(b["hypothesis_id"])
            a_group = str(a["hypothesis_group"])
            b_group = str(b["hypothesis_group"])

            sim = jaccard(tokenize(a_group), tokenize(b_group))

            if a_group == b_group:
                cls = "duplicate"
                strength = 100.0
                reason = "identical_hypothesis_group"
            elif sim >= 0.65:
                cls = "similar"
                strength = round(sim * 100.0, 4)
                reason = "high_token_overlap"
            elif ("good" in a_group and "bad" in b_group) or ("bad" in a_group and "good" in b_group):
                cls = "contradictory"
                strength = 70.0
                reason = "opposing_quality_terms"
            elif sim >= 0.30:
                cls = "complementary"
                strength = round(sim * 100.0, 4)
                reason = "partial_token_overlap"
            else:
                cls = "independent"
                strength = round(sim * 100.0, 4)
                reason = "low_token_overlap"

            if cls == "independent" and strength == 0:
                continue

            rows.append(
                {
                    "relationship_id": stable_hash_id("REL-", [a_id, b_id, cls]),
                    "source_hypothesis_id": a_id,
                    "target_hypothesis_id": b_id,
                    "relationship_class": cls,
                    "relationship_strength": strength,
                    "relationship_reason": reason,
                }
            )

    return rows


def count_relationships(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for row in rows:
        cls = str(row["relationship_class"])
        for key in (str(row["source_hypothesis_id"]), str(row["target_hypothesis_id"])):
            counts[key]["total"] += 1
            counts[key][cls] += 1

    return counts


def write_report(path: Path, intelligence_rows: list[dict[str, Any]], summary_rows: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("# V13A HYPOTHESIS INTELLIGENCE ENGINE REPORT")
    lines.append("")
    lines.append(f"Date: {date.today().isoformat()}")
    lines.append("Scope: Trade Inspector V13A")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Convert V11/V12 research artifacts into explainable hypothesis intelligence.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    for row in summary_rows:
        lines.append(f"| {row['metric']} | {row['value']} |")
    lines.append("")
    lines.append("## Top Hypotheses")
    lines.append("")
    lines.append("| rank | hypothesis_id | group | global_score | priority | action | risk |")
    lines.append("|---:|---|---|---:|---|---|---|")
    for i, row in enumerate(intelligence_rows[:20], 1):
        lines.append(
            f"| {i} | {row['hypothesis_id']} | {row['hypothesis_group']} | "
            f"{row['global_intelligence_score']} | {row['research_priority']} | "
            f"{row['recommended_next_action_v13a']} | {row['risk_level']} |"
        )
    lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- V13A does not modify strategy logic.")
    lines.append("- V13A does not execute trades.")
    lines.append("- V13A does not execute validation runs.")
    lines.append("- V13A only analyzes, scores, clusters, and recommends.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-base", required=True)
    parser.add_argument("--hypothesis-priorities", required=True)
    parser.add_argument("--research-memory", required=True)
    parser.add_argument("--director-directives", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    knowledge_path = Path(args.knowledge_base)
    priorities_path = Path(args.hypothesis_priorities)
    memory_path = Path(args.research_memory)
    directives_path = Path(args.director_directives)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    knowledge_rows = read_csv(knowledge_path)
    priority_rows = read_csv(priorities_path)
    memory_rows = read_csv(memory_path)
    directive_rows = read_csv(directives_path)

    priority_by_id = index_by(priority_rows, "hypothesis_id")
    memory_by_source = group_rows_by_source(memory_rows, "source_id")
    directives_by_source = group_rows_by_source(directive_rows, "source_id")

    intelligence_rows: list[dict[str, Any]] = []

    for row in knowledge_rows:
        hypothesis_id = row.get("hypothesis_id", "")
        hypothesis_group = row.get("hypothesis_group", "")

        priority_row = priority_by_id.get(hypothesis_id, {})
        related_memory = memory_by_source.get(hypothesis_id, [])
        related_directives = directives_by_source.get(hypothesis_id, [])

        merged = dict(row)
        merged.update(priority_row)

        memory_count = len(related_memory)
        directive_count = len(related_directives)

        avg_memory_roi = (
            sum(to_float(r.get("research_roi_score")) for r in related_memory) / memory_count
            if memory_count
            else 0.0
        )

        avg_director_confidence = (
            sum(to_float(r.get("confidence_score")) for r in related_directives) / directive_count
            if directive_count
            else 0.0
        )

        strength = evidence_strength(merged)
        diversity = evidence_diversity(related_memory, related_directives)
        stability = evidence_stability(merged)
        freshness = evidence_freshness(merged)
        coverage = research_coverage_score(merged, memory_count, directive_count)
        conflict = conflict_severity(merged)
        dependency = dependency_risk(merged)
        cost = research_cost(related_memory, related_directives)

        confidence = scientific_confidence(strength, stability, diversity, freshness)
        uncertainty = scientific_uncertainty(confidence, conflict, dependency, coverage)
        novelty = novelty_score(merged, memory_count, 0)
        info_gain = information_gain(novelty, uncertainty, coverage, conflict, cost)

        rel_score = 0.0
        ekg = expected_knowledge_gain(info_gain, uncertainty, novelty, cost)

        gscore = global_score(
            strength,
            stability,
            novelty,
            info_gain,
            coverage,
            confidence,
            rel_score,
            conflict,
            dependency,
            cost,
            ekg,
        )

        priority = classify_priority(gscore, uncertainty, conflict)
        risk = classify_risk(uncertainty, conflict, dependency)
        action = recommend_action(priority, uncertainty, conflict, dependency, coverage, novelty)

        metrics = {
            "evidence_strength": strength,
            "evidence_diversity": diversity,
            "evidence_stability": stability,
            "evidence_freshness": freshness,
            "scientific_confidence": confidence,
            "scientific_uncertainty": uncertainty,
            "novelty_score": novelty,
            "information_gain_score": info_gain,
            "research_coverage_score": coverage,
            "relationship_score": rel_score,
            "dependency_risk_score": dependency,
            "conflict_severity_score": conflict,
            "research_cost_score": cost,
            "expected_knowledge_gain": ekg,
            "global_intelligence_score": gscore,
        }

        intelligence_rows.append(
            {
                "hypothesis_id": hypothesis_id,
                "hypothesis_group": hypothesis_group,
                "object_type": "hypothesis",
                "knowledge_score": row.get("knowledge_score", ""),
                "priority_score": priority_row.get("priority_score", ""),
                "successful_validations": row.get("successful_validations", ""),
                "failed_validations": row.get("failed_validations", ""),
                "pending_validations": row.get("pending_validations", ""),
                "blocked_events": row.get("blocked_events", ""),
                "knowledge_updates": row.get("knowledge_updates", ""),
                "research_status": row.get("research_status", ""),
                "priority_class": priority_row.get("priority_class", ""),
                "recommended_next_action_v11": priority_row.get("recommended_next_action", ""),
                "consistency_class": priority_row.get("consistency_class", ""),
                "maturity_level": priority_row.get("maturity_level", ""),
                "evolution_trend": priority_row.get("evolution_trend", ""),
                "next_learning_need": priority_row.get("next_learning_need", ""),
                "memory_count": memory_count,
                "directive_count": directive_count,
                "avg_memory_roi": round(avg_memory_roi, 4),
                "avg_director_confidence": round(avg_director_confidence, 4),
                "evidence_strength": round(strength, 4),
                "evidence_diversity": round(diversity, 4),
                "evidence_stability": round(stability, 4),
                "evidence_freshness": round(freshness, 4),
                "scientific_confidence": round(confidence, 4),
                "scientific_uncertainty": round(uncertainty, 4),
                "novelty_score": round(novelty, 4),
                "information_gain_score": round(info_gain, 4),
                "research_coverage_score": round(coverage, 4),
                "relationship_score": round(rel_score, 4),
                "dependency_risk_score": round(dependency, 4),
                "conflict_severity_score": round(conflict, 4),
                "research_cost_score": round(cost, 4),
                "expected_knowledge_gain": round(ekg, 4),
                "global_intelligence_score": round(gscore, 4),
                "research_priority": priority,
                "risk_level": risk,
                "recommended_next_action_v13a": action,
                "explainability_positive": explain_positive(metrics),
                "explainability_negative": explain_negative(metrics),
                "created_at_utc": now_utc(),
            }
        )

    relationship_rows = build_relationships(intelligence_rows)
    relationship_counts = count_relationships(relationship_rows)

    for row in intelligence_rows:
        hid = str(row["hypothesis_id"])
        counts = relationship_counts.get(hid, {})
        rel_score = relationship_score(
            counts.get("total", 0),
            counts.get("duplicate", 0),
            counts.get("contradictory", 0),
        )
        row["relationship_score"] = round(rel_score, 4)

        row["global_intelligence_score"] = round(
            global_score(
                to_float(row["evidence_strength"]),
                to_float(row["evidence_stability"]),
                to_float(row["novelty_score"]),
                to_float(row["information_gain_score"]),
                to_float(row["research_coverage_score"]),
                to_float(row["scientific_confidence"]),
                rel_score,
                to_float(row["conflict_severity_score"]),
                to_float(row["dependency_risk_score"]),
                to_float(row["research_cost_score"]),
                to_float(row["expected_knowledge_gain"]),
            ),
            4,
        )

    intelligence_rows.sort(key=lambda r: -to_float(r.get("global_intelligence_score")))

    dependency_rows: list[dict[str, Any]] = []
    conflict_rows: list[dict[str, Any]] = []
    gap_rows: list[dict[str, Any]] = []

    for row in intelligence_rows:
        hid = str(row["hypothesis_id"])

        dep = to_float(row["dependency_risk_score"])
        if dep >= 45:
            dependency_rows.append(
                {
                    "dependency_id": stable_hash_id("DEP-", [hid, row["next_learning_need"]]),
                    "hypothesis_id": hid,
                    "dependency_type": "learning_or_validation_dependency",
                    "dependency_target": row["next_learning_need"],
                    "dependency_risk_score": row["dependency_risk_score"],
                    "dependency_reason": "next_learning_need_or_action_indicates_dependency",
                }
            )

        conf = to_float(row["conflict_severity_score"])
        if conf >= 35:
            conflict_rows.append(
                {
                    "conflict_id": stable_hash_id("CON-", [hid, row["consistency_class"], row["evolution_trend"]]),
                    "hypothesis_id": hid,
                    "conflict_type": "evidence_or_evolution_conflict",
                    "conflict_severity_score": row["conflict_severity_score"],
                    "conflict_reason": "failed_validations_blocked_events_or_consistency_issue",
                }
            )

        coverage = to_float(row["research_coverage_score"])
        uncertainty = to_float(row["scientific_uncertainty"])
        if coverage < 45 or uncertainty >= 65:
            gap_rows.append(
                {
                    "gap_id": stable_hash_id("GAP-", [hid, coverage, uncertainty]),
                    "hypothesis_id": hid,
                    "gap_type": "coverage_or_uncertainty_gap",
                    "gap_score": round(max(100.0 - coverage, uncertainty), 4),
                    "gap_reason": "low_coverage_or_high_uncertainty",
                    "recommended_resolution": row["recommended_next_action_v13a"],
                }
            )

    summary_rows = [
        {"metric": "knowledge_rows", "value": len(knowledge_rows)},
        {"metric": "priority_rows", "value": len(priority_rows)},
        {"metric": "memory_rows", "value": len(memory_rows)},
        {"metric": "directive_rows", "value": len(directive_rows)},
        {"metric": "hypothesis_intelligence_rows", "value": len(intelligence_rows)},
        {"metric": "relationship_rows", "value": len(relationship_rows)},
        {"metric": "dependency_rows", "value": len(dependency_rows)},
        {"metric": "conflict_rows", "value": len(conflict_rows)},
        {"metric": "research_gap_rows", "value": len(gap_rows)},
    ]

    intelligence_path = out_dir / "v13a_hypothesis_intelligence.csv"
    relationship_path = out_dir / "v13a_relationship_graph.csv"
    dependency_path = out_dir / "v13a_dependency_graph.csv"
    conflict_path = out_dir / "v13a_conflict_network.csv"
    gaps_path = out_dir / "v13a_research_gaps.csv"
    summary_path = out_dir / "v13a_summary.csv"
    manifest_path = out_dir / "v13a_manifest.csv"
    report_path = out_dir / f"V13A_HYPOTHESIS_INTELLIGENCE_ENGINE_REPORT_{date.today().isoformat()}.md"

    write_csv(intelligence_path, intelligence_rows, INTELLIGENCE_FIELDS)
    write_csv(relationship_path, relationship_rows, RELATIONSHIP_FIELDS)
    write_csv(dependency_path, dependency_rows, DEPENDENCY_FIELDS)
    write_csv(conflict_path, conflict_rows, CONFLICT_FIELDS)
    write_csv(gaps_path, gap_rows, GAP_FIELDS)
    write_csv(summary_path, summary_rows, SUMMARY_FIELDS)

    manifest_rows = [
        {"artifact": "v13a_hypothesis_intelligence.csv", "path": str(intelligence_path), "rows": len(intelligence_rows), "status": "created"},
        {"artifact": "v13a_relationship_graph.csv", "path": str(relationship_path), "rows": len(relationship_rows), "status": "created"},
        {"artifact": "v13a_dependency_graph.csv", "path": str(dependency_path), "rows": len(dependency_rows), "status": "created"},
        {"artifact": "v13a_conflict_network.csv", "path": str(conflict_path), "rows": len(conflict_rows), "status": "created"},
        {"artifact": "v13a_research_gaps.csv", "path": str(gaps_path), "rows": len(gap_rows), "status": "created"},
        {"artifact": "v13a_summary.csv", "path": str(summary_path), "rows": len(summary_rows), "status": "created"},
        {"artifact": report_path.name, "path": str(report_path), "rows": 1, "status": "created"},
    ]
    write_csv(manifest_path, manifest_rows, MANIFEST_FIELDS)

    write_report(report_path, intelligence_rows, summary_rows)

    print("V13A hypothesis intelligence engine completed")
    print("knowledge_rows:", len(knowledge_rows))
    print("priority_rows:", len(priority_rows))
    print("memory_rows:", len(memory_rows))
    print("directive_rows:", len(directive_rows))
    print("hypothesis_intelligence_rows:", len(intelligence_rows))
    print("relationship_rows:", len(relationship_rows))
    print("dependency_rows:", len(dependency_rows))
    print("conflict_rows:", len(conflict_rows))
    print("research_gap_rows:", len(gap_rows))
    print("report:", report_path)
    print("csv:", intelligence_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
