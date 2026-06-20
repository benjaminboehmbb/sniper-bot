#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
V9E Evidence Conflict Engine

Detects conflicts, redundancies and synergies between strategy hypotheses.

ASCII-only.
"""

from __future__ import annotations

import argparse
from itertools import combinations
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import to_float as fnum





def tokens(text: str) -> set[str]:
    clean = (
        text.lower()
        .replace("__", "_")
        .replace("-", "_")
        .replace(" ", "_")
        .replace("=", "_")
    )
    return {part for part in clean.split("_") if part}


def classify_pair(a: dict[str, str], b: dict[str, str]) -> tuple[str, float, str]:
    a_text = f"{a.get('group_key','')} {a.get('group','')} {a.get('experiment_type','')}"
    b_text = f"{b.get('group_key','')} {b.get('group','')} {b.get('experiment_type','')}"

    a_tok = tokens(a_text)
    b_tok = tokens(b_text)

    shared = a_tok & b_tok

    a_group = a.get("group", "")
    b_group = b.get("group", "")
    a_key = a.get("group_key", "")
    b_key = b.get("group_key", "")

    a_score = fnum(a.get("opportunity_score"))
    b_score = fnum(b.get("opportunity_score"))
    avg_score = (a_score + b_score) / 2.0

    a_class = a.get("opportunity_class", "")
    b_class = b.get("opportunity_class", "")

    if a_class == "REJECT" or b_class == "REJECT":
        return "LOW_PRIORITY_IGNORE", 0.0, "one_or_both_hypotheses_rejected"

    if ("bull" in a_tok and "bear" in b_tok) or ("bear" in a_tok and "bull" in b_tok):
        return "MUTUALLY_EXCLUSIVE_CONTEXT", avg_score, "bull_bear_context_conflict"

    if ("long" in a_tok and "short" in b_tok) or ("short" in a_tok and "long" in b_tok):
        return "MUTUALLY_EXCLUSIVE_CONTEXT", avg_score, "long_short_context_conflict"

    if ("early" in a_tok and "hold" in b_tok) or ("hold" in a_tok and "early" in b_tok):
        return "POTENTIAL_CONFLICT", avg_score, "exit_timing_conflict"

    if a_group and b_group and (a_group in b_group or b_group in a_group):
        return "REDUNDANT_PARENT_CHILD", avg_score, "group_text_parent_child_overlap"

    if a_key and b_key and (a_key in b_key or b_key in a_key):
        return "REDUNDANT_PARENT_CHILD", avg_score, "group_key_parent_child_overlap"

    if len(shared) >= 3:
        return "SYNERGY", avg_score + len(shared), "multiple_shared_tokens"

    if len(shared) >= 1:
        return "COMPATIBLE", avg_score, "some_shared_context"

    return "COMPATIBLE", avg_score * 0.5, "no_direct_conflict_detected"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v9c-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v9c_csv = Path(args.v9c_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v9c_csv)

    relationships: list[dict[str, object]] = []
    matrix_rows: list[dict[str, object]] = []

    for i, row in enumerate(rows, 1):
        matrix_rows.append(
            {
                "hypothesis_id": f"H{i:03d}",
                "group_key": row.get("group_key", ""),
                "group": row.get("group", ""),
                "experiment_type": row.get("experiment_type", ""),
                "opportunity_score": row.get("opportunity_score", ""),
                "opportunity_class": row.get("opportunity_class", ""),
            }
        )

    indexed = list(enumerate(rows, 1))

    for (idx_a, a), (idx_b, b) in combinations(indexed, 2):
        relation, score, reason = classify_pair(a, b)

        relationships.append(
            {
                "hypothesis_a_id": f"H{idx_a:03d}",
                "hypothesis_b_id": f"H{idx_b:03d}",
                "hypothesis_a_group_key": a.get("group_key", ""),
                "hypothesis_a_group": a.get("group", ""),
                "hypothesis_b_group_key": b.get("group_key", ""),
                "hypothesis_b_group": b.get("group", ""),
                "relationship_class": relation,
                "relationship_score": round(score, 4),
                "reason": reason,
                "a_opportunity_score": a.get("opportunity_score", ""),
                "b_opportunity_score": b.get("opportunity_score", ""),
                "a_opportunity_class": a.get("opportunity_class", ""),
                "b_opportunity_class": b.get("opportunity_class", ""),
            }
        )

    relationships.sort(
        key=lambda r: (
            str(r["relationship_class"]) not in {"POTENTIAL_CONFLICT", "MUTUALLY_EXCLUSIVE_CONTEXT", "SYNERGY", "REDUNDANT_PARENT_CHILD"},
            -float(r["relationship_score"]),
        )
    )

    out_conflicts = out_dir / "v9e_hypothesis_conflicts.csv"
    out_matrix = out_dir / "v9e_hypothesis_compatibility_matrix.csv"

    write_csv(out_conflicts, relationships, ['hypothesis_a_id', 'hypothesis_b_id', 'hypothesis_a_group_key', 'hypothesis_a_group', 'hypothesis_b_group_key', 'hypothesis_b_group', 'relationship_class', 'relationship_score', 'reason', 'a_opportunity_score', 'b_opportunity_score', 'a_opportunity_class', 'b_opportunity_class'])
    write_csv(out_matrix, matrix_rows, ['hypothesis_id', 'group_key', 'group', 'experiment_type', 'opportunity_score', 'opportunity_class'])

    class_counts: dict[str, int] = {}
    for row in relationships:
        cls = str(row["relationship_class"])
        class_counts[cls] = class_counts.get(cls, 0) + 1

    report = out_dir / "V9E_EVIDENCE_CONFLICT_REPORT_2026-06-18.md"

    lines: list[str] = []
    lines.append("# V9E EVIDENCE CONFLICT REPORT")
    lines.append("")
    lines.append("Date: 2026-06-18")
    lines.append("Device: G15 / AR15")
    lines.append("Environment: WSL")
    lines.append("Scope: Trade Inspector V9E")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Detect conflicts, redundancies and synergies between strategy hypotheses.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v9c_csv}")
    lines.append(f"- Hypotheses evaluated: {len(rows)}")
    lines.append(f"- Pairwise relationships evaluated: {len(relationships)}")
    lines.append("")
    lines.append("## Relationship Summary")
    lines.append("")
    lines.append("| relationship_class | count |")
    lines.append("|---|---:|")
    for key in sorted(class_counts):
        lines.append(f"| {key} | {class_counts[key]} |")
    lines.append("")
    lines.append("## Highest Priority Relationships")
    lines.append("")
    lines.append("| rank | hypothesis_a | hypothesis_b | relationship | score | reason |")
    lines.append("|---:|---|---|---|---:|---|")

    for i, row in enumerate(relationships[:25], 1):
        lines.append(
            f"| {i} | {row['hypothesis_a_id']} {row['hypothesis_a_group']} | "
            f"{row['hypothesis_b_id']} {row['hypothesis_b_group']} | "
            f"{row['relationship_class']} | {row['relationship_score']} | {row['reason']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- SYNERGY pairs may be candidates for combined validation.")
    lines.append("- REDUNDANT_PARENT_CHILD pairs should usually not be validated as separate independent experiments.")
    lines.append("- POTENTIAL_CONFLICT pairs require separate tests or explicit decision rules.")
    lines.append("- MUTUALLY_EXCLUSIVE_CONTEXT pairs should not be combined into one simple rule.")
    lines.append("- LOW_PRIORITY_IGNORE pairs include rejected hypotheses and should not consume effort now.")
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V9E does not approve live strategy changes.")
    lines.append("It only improves experiment design by preventing incompatible hypothesis combinations.")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v9e_hypothesis_conflicts.csv")
    lines.append("- v9e_hypothesis_compatibility_matrix.csv")
    lines.append("- V9E_EVIDENCE_CONFLICT_REPORT_2026-06-18.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V9E evidence conflict engine completed")
    print("input_rows:", len(rows))
    print("relationships:", len(relationships))
    for key in sorted(class_counts):
        print(f"{key}:", class_counts[key])
    print("report:", report)
    print("conflicts_csv:", out_conflicts)
    print("matrix_csv:", out_matrix)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
