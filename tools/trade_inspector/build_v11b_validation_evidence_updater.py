#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import now_utc



def update_rule(outcome: str) -> tuple[str, float, str]:
    if outcome == "VALIDATION_PASS":
        return "INCREASE_CONFIDENCE", 1.0, "successful_validation_result"
    if outcome == "VALIDATION_FAIL":
        return "DECREASE_CONFIDENCE", -1.0, "failed_validation_result"
    if outcome == "NEEDS_REAL_REPLAY":
        return "KEEP_PENDING", 0.0, "real_replay_required"
    if outcome == "BLOCKED":
        return "TECHNICAL_REMEDIATION_REQUIRED", 0.0, "blocked_validation_result"
    if outcome == "SKIPPED":
        return "NO_UPDATE", 0.0, "skipped_validation_result"
    if outcome == "INVALID":
        return "BLOCK_FROM_LEARNING", 0.0, "invalid_or_guardrail_violation"
    return "MANUAL_REVIEW_REQUIRED", 0.0, "unknown_validation_outcome"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v11a-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    source = Path(args.v11a_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(source)
    created_at = now_utc()

    updates: list[dict[str, object]] = []

    for row in rows:
        outcome = row.get("validation_outcome", "")
        action, delta, reason = update_rule(outcome)

        updates.append(
            {
                "validation_id": row.get("validation_id", ""),
                "hypothesis_id": row.get("hypothesis_id", ""),
                "hypothesis_group": row.get("hypothesis_group", ""),
                "validation_outcome": outcome,
                "learning_action": row.get("learning_action", ""),
                "evidence_update_action": action,
                "confidence_delta": delta,
                "update_reason": reason,
                "use_for_learning": "yes" if action in {"INCREASE_CONFIDENCE", "DECREASE_CONFIDENCE"} else "no",
                "created_at_utc": created_at,
            }
        )

    out_csv = out_dir / "v11b_validation_evidence_updates.csv"
    write_csv(out_csv, updates, ['validation_id', 'hypothesis_id', 'hypothesis_group', 'validation_outcome', 'learning_action', 'evidence_update_action', 'confidence_delta', 'update_reason', 'use_for_learning', 'created_at_utc'])

    counts: dict[str, int] = {}
    for row in updates:
        key = str(row["evidence_update_action"])
        counts[key] = counts.get(key, 0) + 1

    report = out_dir / "V11B_VALIDATION_EVIDENCE_UPDATER_REPORT_2026-06-19.md"

    lines = []
    lines.append("# V11B VALIDATION EVIDENCE UPDATER REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V11B")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Convert V11A replay evaluation outcomes into evidence update records.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {source}")
    lines.append(f"- Rows processed: {len(rows)}")
    lines.append("")
    lines.append("## Evidence Update Summary")
    lines.append("")
    lines.append("| evidence_update_action | count |")
    lines.append("|---|---:|")
    for key in sorted(counts):
        lines.append(f"| {key} | {counts[key]} |")
    lines.append("")
    lines.append("## Updates")
    lines.append("")
    lines.append("| validation_id | group | outcome | update_action | confidence_delta | use_for_learning |")
    lines.append("|---|---|---|---|---:|---|")
    for row in updates[:30]:
        lines.append(
            f"| {row['validation_id']} | {row['hypothesis_group']} | "
            f"{row['validation_outcome']} | {row['evidence_update_action']} | "
            f"{row['confidence_delta']} | {row['use_for_learning']} |"
        )
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V11B creates evidence update artifacts only. It does not overwrite existing evidence databases.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V11B validation evidence updater completed")
    print("input_rows:", len(rows))
    print("update_rows:", len(updates))
    for key in sorted(counts):
        print(f"{key}:", counts[key])
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
