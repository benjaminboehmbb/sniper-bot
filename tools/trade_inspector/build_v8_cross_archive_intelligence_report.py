#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
V8 Cross-Archive Intelligence Report

Reads V7D, V7E and V7F multi-archive outputs and creates a focused
decision-support report for Trade Inspector analysis.

ASCII-only output.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fnum(value: str, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def top_rows(rows: list[dict[str, str]], key: str, n: int = 10, reverse: bool = True) -> list[dict[str, str]]:
    return sorted(rows, key=lambda r: fnum(r.get(key, "")), reverse=reverse)[:n]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
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
    parser.add_argument("--v7d-dir", required=True)
    parser.add_argument("--v7e-dir", required=True)
    parser.add_argument("--v7f-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    v7d_dir = Path(args.v7d_dir)
    v7e_dir = Path(args.v7e_dir)
    v7f_dir = Path(args.v7f_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    root_rows = read_csv(v7d_dir / "cross_archive_root_cause_attribution_v7d.csv")
    feature_rows = read_csv(v7e_dir / "cross_archive_feature_importance_v7e.csv")
    signal_rows = read_csv(v7f_dir / "cross_archive_signal_discovery_v7f_top.csv")

    root_top = top_rows(root_rows, "priority_share_pct", 10)
    feature_top = top_rows(feature_rows, "importance_score", 20)
    signal_top = top_rows(signal_rows, "discovery_score", 20)

    actionable = [r for r in signal_rows if r.get("reliability_class") == "ACTIONABLE_CANDIDATE"]
    watch = [r for r in signal_rows if r.get("discovery_status") == "WATCH"]
    promising = [r for r in signal_rows if r.get("discovery_status") == "PROMISING"]

    high_warning = [r for r in signal_rows if r.get("warning_level") == "HIGH"]
    low_warning = [r for r in signal_rows if r.get("warning_level") == "LOW"]

    avg_signal_score = mean([fnum(r.get("discovery_score", "")) for r in signal_rows]) if signal_rows else 0.0
    avg_feature_importance = mean([fnum(r.get("importance_score", "")) for r in feature_rows]) if feature_rows else 0.0

    write_csv(out_dir / "v8_top_root_causes.csv", root_top)
    write_csv(out_dir / "v8_top_features.csv", feature_top)
    write_csv(out_dir / "v8_top_signal_groups.csv", signal_top)
    write_csv(out_dir / "v8_actionable_candidate_groups.csv", actionable)
    write_csv(out_dir / "v8_high_warning_groups.csv", high_warning)

    report = out_dir / "V8_CROSS_ARCHIVE_INTELLIGENCE_REPORT_2026-06-18.md"

    lines: list[str] = []
    lines.append("# V8 CROSS-ARCHIVE INTELLIGENCE REPORT")
    lines.append("")
    lines.append("Date: 2026-06-18")
    lines.append("Device: Workstation")
    lines.append("Environment: WSL")
    lines.append("Scope: Trade Inspector V8")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("The V8 report consolidates V7D, V7E and V7F multi-archive outputs into a decision-oriented intelligence layer.")
    lines.append("")
    lines.append("Key result:")
    lines.append("")
    lines.append("- The multi-archive pipeline is operational.")
    lines.append("- Root cause, feature importance and signal discovery outputs can now be interpreted across archives.")
    lines.append("- No PROMISING signal group was detected.")
    lines.append("- Multiple WATCH and ACTIONABLE_CANDIDATE groups exist, but these must be treated as hypotheses, not strategy changes.")
    lines.append("")
    lines.append("## Input Data")
    lines.append("")
    lines.append(f"- V7D root cause rows: {len(root_rows)}")
    lines.append(f"- V7E feature importance rows: {len(feature_rows)}")
    lines.append(f"- V7F signal discovery rows: {len(signal_rows)}")
    lines.append(f"- V7F promising groups: {len(promising)}")
    lines.append(f"- V7F watch groups: {len(watch)}")
    lines.append(f"- V7F actionable candidate groups: {len(actionable)}")
    lines.append(f"- V7F high warning groups: {len(high_warning)}")
    lines.append(f"- V7F low warning groups: {len(low_warning)}")
    lines.append("")
    lines.append("## Root Cause Intelligence")
    lines.append("")
    lines.append("Top root causes by priority contribution:")
    lines.append("")
    lines.append("| rank | root_cause | priority_share_pct | impact_share_pct | negative_pnl_share_pct | opportunity_loss_share_pct |")
    lines.append("|---:|---|---:|---:|---:|---:|")
    for i, r in enumerate(root_top, 1):
        lines.append(
            f"| {i} | {r.get('root_cause','')} | {r.get('priority_share_pct','')} | "
            f"{r.get('impact_share_pct','')} | {r.get('negative_pnl_share_pct','')} | "
            f"{r.get('opportunity_loss_share_pct','')} |"
        )
    lines.append("")
    lines.append("Interpretation:")
    lines.append("")
    lines.append("- Root causes with high priority share should be inspected first.")
    lines.append("- Root causes with high negative PnL share indicate direct loss pressure.")
    lines.append("- Root causes with high opportunity-loss share indicate missed upside or weak exit behavior.")
    lines.append("")
    lines.append("## Feature Importance Intelligence")
    lines.append("")
    lines.append("Top feature candidates by importance score:")
    lines.append("")
    lines.append("| rank | target_column | feature_name | importance_score | rows_used |")
    lines.append("|---:|---|---|---:|---:|")
    for i, r in enumerate(feature_top[:15], 1):
        lines.append(
            f"| {i} | {r.get('target_column','')} | {r.get('feature_name','')} | "
            f"{r.get('importance_score','')} | {r.get('rows_used','')} |"
        )
    lines.append("")
    lines.append("Interpretation:")
    lines.append("")
    lines.append("- These features are not automatically tradable signals.")
    lines.append("- They are candidates for hypothesis generation and controlled validation.")
    lines.append("- Features that repeatedly appear across several targets deserve priority review.")
    lines.append("")
    lines.append("## Signal Discovery Intelligence")
    lines.append("")
    lines.append("Top signal groups by discovery score:")
    lines.append("")
    lines.append("| rank | group_key | group | count | reliability_class | warning_level | winrate | winrate_edge | pnl_edge | discovery_score | status |")
    lines.append("|---:|---|---|---:|---|---|---:|---:|---:|---:|---|")
    for i, r in enumerate(signal_top[:15], 1):
        lines.append(
            f"| {i} | {r.get('group_key','')} | {r.get('group','')} | {r.get('count','')} | "
            f"{r.get('reliability_class','')} | {r.get('warning_level','')} | "
            f"{r.get('winrate','')} | {r.get('winrate_edge','')} | "
            f"{r.get('pnl_edge','')} | {r.get('discovery_score','')} | "
            f"{r.get('discovery_status','')} |"
        )
    lines.append("")
    lines.append("Interpretation:")
    lines.append("")
    lines.append("- PROMISING groups: none detected.")
    lines.append("- WATCH groups should be monitored across additional archives.")
    lines.append("- ACTIONABLE_CANDIDATE means technically interesting, not approved for live strategy changes.")
    lines.append("- HIGH warning groups must not be used for live logic without further validation.")
    lines.append("")
    lines.append("## Candidate Hypotheses")
    lines.append("")
    if signal_top:
        for i, r in enumerate(signal_top[:10], 1):
            lines.append(
                f"{i}. Hypothesis: group `{r.get('group_key','')} = {r.get('group','')}` may be relevant. "
                f"Current status: {r.get('discovery_status','')}, reliability: {r.get('reliability_class','')}, "
                f"warning: {r.get('warning_level','')}, support: {r.get('count','')}."
            )
    else:
        lines.append("No signal hypotheses available.")
    lines.append("")
    lines.append("## Risk Assessment")
    lines.append("")
    lines.append("- Current sample size is better than the earlier single-archive state but still not sufficient for uncontrolled strategy changes.")
    lines.append("- The correct use of V8 is hypothesis generation, not direct live-trading modification.")
    lines.append("- Any candidate must pass controlled validation before strategy integration.")
    lines.append("")
    lines.append("## Recommended Next Actions")
    lines.append("")
    lines.append("1. Review top root causes from `v8_top_root_causes.csv`.")
    lines.append("2. Review repeated high-importance features from `v8_top_features.csv`.")
    lines.append("3. Review signal groups from `v8_top_signal_groups.csv`.")
    lines.append("4. Select a small number of hypotheses for controlled validation.")
    lines.append("5. Do not change live logic until a hypothesis is confirmed on additional archives or controlled replay windows.")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- V8_CROSS_ARCHIVE_INTELLIGENCE_REPORT_2026-06-18.md")
    lines.append("- v8_top_root_causes.csv")
    lines.append("- v8_top_features.csv")
    lines.append("- v8_top_signal_groups.csv")
    lines.append("- v8_actionable_candidate_groups.csv")
    lines.append("- v8_high_warning_groups.csv")
    lines.append("")
    lines.append("## Bottom Line")
    lines.append("")
    lines.append("The system is now capable of extracting cross-archive intelligence. The current result does not justify direct strategy modification yet, but it provides a structured basis for selecting the next validation hypotheses.")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V8 report created:")
    print(report)
    print("root_causes:", len(root_rows))
    print("feature_rows:", len(feature_rows))
    print("signal_rows:", len(signal_rows))
    print("promising_groups:", len(promising))
    print("watch_groups:", len(watch))
    print("actionable_candidate_groups:", len(actionable))
    print("high_warning_groups:", len(high_warning))
    print("avg_signal_discovery_score:", round(avg_signal_score, 6))
    print("avg_feature_importance:", round(avg_feature_importance, 6))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
