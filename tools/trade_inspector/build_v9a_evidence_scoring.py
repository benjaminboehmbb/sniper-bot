#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fnum(value: object, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def support_score(count: float) -> float:
    if count >= 400:
        return 100.0
    if count >= 200:
        return 85.0
    if count >= 100:
        return 70.0
    if count >= 50:
        return 55.0
    if count >= 30:
        return 40.0
    if count >= 10:
        return 20.0
    return 5.0


def reliability_score(label: str) -> float:
    return {
        "ACTIONABLE_CANDIDATE": 85.0,
        "WATCH_ONLY": 55.0,
        "NOT_ACTIONABLE": 15.0,
    }.get(label, 25.0)


def warning_penalty(label: str) -> float:
    return {
        "LOW": 0.0,
        "MEDIUM": 15.0,
        "HIGH": 35.0,
    }.get(label, 20.0)


def status_score(label: str) -> float:
    return {
        "PROMISING": 100.0,
        "WATCH": 65.0,
        "LOW_SUPPORT": 25.0,
        "REJECT": 0.0,
    }.get(label, 30.0)


def edge_score(winrate_edge: float, pnl_edge: float) -> float:
    win_component = clamp(winrate_edge * 250.0, 0.0, 50.0)
    pnl_component = clamp(pnl_edge * 10000.0, 0.0, 50.0)
    return win_component + pnl_component


def classify(score: float) -> str:
    if score >= 80:
        return "STRONG_EVIDENCE"
    if score >= 65:
        return "MODERATE_EVIDENCE"
    if score >= 45:
        return "WEAK_EVIDENCE"
    return "INSUFFICIENT_EVIDENCE"


def actionability(score_class: str, warning: str, count: float) -> str:
    if score_class == "STRONG_EVIDENCE" and warning == "LOW" and count >= 100:
        return "VALIDATION_PRIORITY_HIGH"
    if score_class in {"STRONG_EVIDENCE", "MODERATE_EVIDENCE"} and warning in {"LOW", "MEDIUM"} and count >= 30:
        return "VALIDATION_PRIORITY_MEDIUM"
    if score_class == "WEAK_EVIDENCE":
        return "WATCHLIST_ONLY"
    return "DO_NOT_ACT"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v8-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v8_dir = Path(args.v8_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(v8_dir / "v8_top_signal_groups.csv")

    scored = []
    seen = set()

    for row in rows:
        key = (row.get("group_key", ""), row.get("group", ""))
        if key in seen:
            continue
        seen.add(key)

        count = fnum(row.get("count"))
        winrate_edge = fnum(row.get("winrate_edge"))
        pnl_edge = fnum(row.get("pnl_edge"))
        discovery = fnum(row.get("discovery_score"))

        rel = row.get("reliability_class", "")
        warn = row.get("warning_level", "")
        status = row.get("discovery_status", "")

        s_support = support_score(count)
        s_rel = reliability_score(rel)
        s_edge = edge_score(winrate_edge, pnl_edge)
        s_status = status_score(status)
        s_discovery = clamp(discovery)
        penalty = warning_penalty(warn)

        evidence = clamp(
            0.25 * s_support
            + 0.25 * s_rel
            + 0.20 * s_edge
            + 0.15 * s_discovery
            + 0.15 * s_status
            - penalty
        )

        evidence_class = classify(evidence)
        recommended_action = actionability(evidence_class, warn, count)

        scored.append({
            "group_key": row.get("group_key", ""),
            "group": row.get("group", ""),
            "count": int(count),
            "winrate": row.get("winrate", ""),
            "winrate_edge": winrate_edge,
            "pnl_edge": pnl_edge,
            "discovery_score": discovery,
            "discovery_status": status,
            "reliability_class": rel,
            "warning_level": warn,
            "support_score": round(s_support, 4),
            "reliability_score": round(s_rel, 4),
            "edge_score": round(s_edge, 4),
            "status_score": round(s_status, 4),
            "discovery_component": round(s_discovery, 4),
            "warning_penalty": round(penalty, 4),
            "evidence_score": round(evidence, 4),
            "evidence_class": evidence_class,
            "recommended_action": recommended_action,
        })

    scored.sort(key=lambda r: float(r["evidence_score"]), reverse=True)

    high = [r for r in scored if r["recommended_action"] == "VALIDATION_PRIORITY_HIGH"]
    medium = [r for r in scored if r["recommended_action"] == "VALIDATION_PRIORITY_MEDIUM"]
    watch = [r for r in scored if r["recommended_action"] == "WATCHLIST_ONLY"]
    reject = [r for r in scored if r["recommended_action"] == "DO_NOT_ACT"]

    out_csv = out_dir / "v9a_evidence_scores.csv"
    write_csv(out_csv, scored)

    report = out_dir / "V9A_EVIDENCE_SCORING_REPORT_2026-06-18.md"

    lines = []
    lines.append("# V9A EVIDENCE SCORING REPORT")
    lines.append("")
    lines.append("Date: 2026-06-18")
    lines.append("Device: Workstation")
    lines.append("Environment: WSL")
    lines.append("Scope: Trade Inspector V9A")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("V9A converts V8 signal hypotheses into ranked evidence scores.")
    lines.append("The purpose is prioritization for controlled validation, not direct live strategy modification.")
    lines.append("")
    lines.append("## Action Summary")
    lines.append("")
    lines.append(f"- Hypotheses scored: {len(scored)}")
    lines.append(f"- VALIDATION_PRIORITY_HIGH: {len(high)}")
    lines.append(f"- VALIDATION_PRIORITY_MEDIUM: {len(medium)}")
    lines.append(f"- WATCHLIST_ONLY: {len(watch)}")
    lines.append(f"- DO_NOT_ACT: {len(reject)}")
    lines.append("")
    lines.append("## Top Evidence-Ranked Hypotheses")
    lines.append("")
    lines.append("| rank | group_key | group | count | evidence_score | evidence_class | recommended_action | warning |")
    lines.append("|---:|---|---|---:|---:|---|---|---|")

    for i, row in enumerate(scored[:20], 1):
        lines.append(
            f"| {i} | {row['group_key']} | {row['group']} | {row['count']} | "
            f"{row['evidence_score']} | {row['evidence_class']} | "
            f"{row['recommended_action']} | {row['warning_level']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- V9A provides prioritization, not approval.")
    lines.append("- High or medium priority hypotheses should be tested by controlled validation.")
    lines.append("- No live strategy logic should be changed from V9A alone.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V9A evidence scoring completed")
    print("input_rows:", len(rows))
    print("scored_hypotheses:", len(scored))
    print("validation_priority_high:", len(high))
    print("validation_priority_medium:", len(medium))
    print("watchlist_only:", len(watch))
    print("do_not_act:", len(reject))
    print("top_score:", scored[0]["evidence_score"] if scored else "NA")
    print("report:", report)
    print("csv:", out_csv)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
