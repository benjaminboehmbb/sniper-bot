#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


REQUIRED_COLUMNS_ANY = [
    "hypothesis_id",
    "priority_rank",
    "priority_score",
    "recommended_action",
    "status",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def pick(row: dict[str, str], names: list[str], default: str = "") -> str:
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            return str(value)
    return default


def to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def build_campaigns(hypotheses: list[dict[str, str]], max_campaigns: int) -> list[dict[str, object]]:
    scored = []
    for row in hypotheses:
        score = to_float(pick(row, ["priority_score", "combined_score", "score", "research_priority_score"], "0"))
        rank = pick(row, ["priority_rank", "rank"], "")
        hypothesis_id = pick(row, ["hypothesis_id", "id", "candidate_id"], "")
        title = pick(row, ["hypothesis", "hypothesis_title", "description", "research_question"], hypothesis_id)
        action = pick(row, ["recommended_action", "action", "next_action"], "plan_validation")
        status = pick(row, ["status", "readiness", "decision"], "planned")
        scored.append((score, rank, hypothesis_id, title, action, status, row))

    scored.sort(key=lambda x: x[0], reverse=True)

    campaigns = []
    for i, item in enumerate(scored[:max_campaigns], start=1):
        score, rank, hypothesis_id, title, action, status, row = item
        if score >= 0.75:
            priority = "high"
            expected_value = "high"
        elif score >= 0.50:
            priority = "medium"
            expected_value = "medium"
        else:
            priority = "low"
            expected_value = "exploratory"

        if status.lower() in {"blocked", "conflict", "inconsistent"}:
            campaign_status = "blocked"
        else:
            campaign_status = "planned"

        campaigns.append(
            {
                "campaign_id": f"V12A-CAMPAIGN-{i:03d}",
                "campaign_title": f"Research campaign for {hypothesis_id or title}",
                "campaign_goal": title,
                "priority": priority,
                "source_hypothesis_id": hypothesis_id,
                "source_priority_rank": rank,
                "source_priority_score": f"{score:.6f}",
                "recommended_action": action,
                "required_archives": pick(row, ["archive_id", "archives", "required_archives"], "latest_available_archives"),
                "required_inputs": "v11f_hypothesis_priorities.csv; v11c_research_knowledge_base.csv; v9g_research_decisions.csv",
                "runtime_class": "none",
                "execution_mode": "planning_only",
                "estimated_runtime": "none",
                "compute_target": "G15_or_Workstation_planning_only",
                "expected_learning_value": expected_value,
                "dependencies": "V9_to_V11_outputs_available",
                "guardrails": "no_strategy_change; no_runtime; no_replay; no_live_trading; artifact_only",
                "campaign_status": campaign_status,
            }
        )

    return campaigns


def write_report(path: Path, campaigns: list[dict[str, object]], input_files: list[Path]) -> None:
    today = date.today().isoformat()
    lines = [
        "# V12A RESEARCH CAMPAIGN MANAGER REPORT",
        "",
        f"Date: {today}",
        "",
        "## Objective",
        "",
        "Create structured research campaigns from existing V9-V11 research intelligence artifacts.",
        "",
        "## Guardrails",
        "",
        "- No strategy logic changes.",
        "- No runtime execution.",
        "- No replay execution.",
        "- No live trading.",
        "- Artifact-only planning layer.",
        "",
        "## Inputs",
        "",
    ]
    for p in input_files:
        lines.append(f"- {p}")
    lines += [
        "",
        "## Outputs",
        "",
        "- v12a_research_campaigns.csv",
        "- v12a_campaign_manifest.csv",
        f"- {path.name}",
        "",
        "## Result",
        "",
        f"Generated campaigns: {len(campaigns)}",
        "",
        "## Campaign Summary",
        "",
        "| campaign_id | priority | status | source_hypothesis_id |",
        "|---|---|---|---|",
    ]
    for c in campaigns:
        lines.append(
            f"| {c['campaign_id']} | {c['priority']} | {c['campaign_status']} | {c['source_hypothesis_id']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "V12A introduces the first autonomous research-management layer above the V11 learning loop.",
        "The module converts prioritized hypotheses into campaign-level planning artifacts while preserving strict operational guardrails.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="V12A Research Campaign Manager")
    parser.add_argument("--hypotheses", required=True)
    parser.add_argument("--knowledge-base", required=False)
    parser.add_argument("--research-decisions", required=False)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-campaigns", type=int, default=10)
    args = parser.parse_args()

    hypotheses_path = Path(args.hypotheses)
    output_dir = Path(args.output_dir)

    hypotheses = read_csv(hypotheses_path)
    campaigns = build_campaigns(hypotheses, args.max_campaigns)

    campaign_fields = [
        "campaign_id",
        "campaign_title",
        "campaign_goal",
        "priority",
        "source_hypothesis_id",
        "source_priority_rank",
        "source_priority_score",
        "recommended_action",
        "required_archives",
        "required_inputs",
        "runtime_class",
        "execution_mode",
        "estimated_runtime",
        "compute_target",
        "expected_learning_value",
        "dependencies",
        "guardrails",
        "campaign_status",
    ]

    campaign_path = output_dir / "v12a_research_campaigns.csv"
    manifest_path = output_dir / "v12a_campaign_manifest.csv"
    report_path = output_dir / f"V12A_RESEARCH_CAMPAIGN_MANAGER_REPORT_{date.today().isoformat()}.md"

    write_csv(campaign_path, campaigns, campaign_fields)

    manifest_rows = [
        {
            "artifact": "v12a_research_campaigns.csv",
            "path": str(campaign_path),
            "rows": len(campaigns),
            "status": "created",
        },
        {
            "artifact": "V12A_RESEARCH_CAMPAIGN_MANAGER_REPORT",
            "path": str(report_path),
            "rows": 1,
            "status": "created",
        },
    ]
    write_csv(manifest_path, manifest_rows, ["artifact", "path", "rows", "status"])

    input_files = [hypotheses_path]
    if args.knowledge_base:
        input_files.append(Path(args.knowledge_base))
    if args.research_decisions:
        input_files.append(Path(args.research_decisions))

    write_report(report_path, campaigns, input_files)

    print("PASS: V12A research campaign manager completed")
    print(f"campaigns: {len(campaigns)}")
    print(f"campaign_csv: {campaign_path}")
    print(f"manifest_csv: {manifest_path}")
    print(f"report_md: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
