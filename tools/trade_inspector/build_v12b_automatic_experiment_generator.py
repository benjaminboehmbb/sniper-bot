#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from tools.trade_inspector.common.io import read_csv, write_csv
from tools.trade_inspector.common.utils import pick





def derive_experiment_type(campaign: dict[str, str]) -> str:
    action = pick(campaign, ["recommended_action"], "").lower()
    goal = pick(campaign, ["campaign_goal", "campaign_title"], "").lower()

    if "replay" in action or "replay" in goal:
        return "replay_readiness_spec"
    if "archive" in action or "cross" in goal or "consistency" in goal:
        return "cross_archive_analysis_spec"
    if "validation" in action or "validate" in action:
        return "validation_spec"
    if "conflict" in goal or "inconsistent" in goal:
        return "conflict_resolution_spec"
    return "research_planning_spec"


def derive_readiness(campaign: dict[str, str]) -> str:
    status = pick(campaign, ["campaign_status"], "planned").lower()
    priority = pick(campaign, ["priority"], "low").lower()

    if status == "blocked":
        return "blocked"
    if priority in {"high", "medium"}:
        return "ready_for_spec_review"
    return "draft"


def build_experiments(campaigns: list[dict[str, str]], max_experiments: int) -> list[dict[str, object]]:
    experiments: list[dict[str, object]] = []

    for i, campaign in enumerate(campaigns[:max_experiments], start=1):
        campaign_id = pick(campaign, ["campaign_id"], f"UNKNOWN-CAMPAIGN-{i:03d}")
        priority = pick(campaign, ["priority"], "low")
        hypothesis_id = pick(campaign, ["source_hypothesis_id"], "")
        goal = pick(campaign, ["campaign_goal", "campaign_title"], "")
        archives = pick(campaign, ["required_archives"], "latest_available_archives")
        experiment_type = derive_experiment_type(campaign)
        readiness = derive_readiness(campaign)

        if readiness == "blocked":
            execution_status = "blocked"
        else:
            execution_status = "generated_not_executable"

        experiments.append(
            {
                "experiment_id": f"V12B-EXP-{i:03d}",
                "campaign_id": campaign_id,
                "source_hypothesis_id": hypothesis_id,
                "experiment_title": f"Experiment spec for {campaign_id}",
                "experiment_goal": goal,
                "experiment_type": experiment_type,
                "priority": priority,
                "required_archives": archives,
                "input_artifacts": "v12a_research_campaigns.csv",
                "planned_outputs": "experiment_review_notes; validation_candidate_spec",
                "execution_mode": "specification_only",
                "runtime_allowed": "false",
                "replay_allowed": "false",
                "strategy_change_allowed": "false",
                "live_trading_allowed": "false",
                "estimated_compute_cost": "none",
                "review_requirement": "manual_review_required_before_execution",
                "readiness": readiness,
                "execution_status": execution_status,
                "guardrails": "no_strategy_change; no_runtime; no_replay; no_live_trading; artifact_only",
            }
        )

    return experiments


def write_report(path: Path, experiments: list[dict[str, object]], campaigns_path: Path) -> None:
    today = date.today().isoformat()
    lines = [
        "# V12B AUTOMATIC EXPERIMENT GENERATOR REPORT",
        "",
        f"Date: {today}",
        "",
        "## Objective",
        "",
        "Generate concrete experiment specifications from V12A research campaigns.",
        "",
        "## Input",
        "",
        f"- {campaigns_path}",
        "",
        "## Outputs",
        "",
        "- v12b_experiment_specs.csv",
        "- v12b_experiment_manifest.csv",
        f"- {path.name}",
        "",
        "## Guardrails",
        "",
        "- No strategy logic changes.",
        "- No runtime execution.",
        "- No replay execution.",
        "- No live trading.",
        "- Specification-only output.",
        "",
        "## Result",
        "",
        f"Generated experiment specifications: {len(experiments)}",
        "",
        "## Experiment Summary",
        "",
        "| experiment_id | campaign_id | type | priority | readiness |",
        "|---|---|---|---|---|",
    ]

    for exp in experiments:
        lines.append(
            f"| {exp['experiment_id']} | {exp['campaign_id']} | {exp['experiment_type']} | {exp['priority']} | {exp['readiness']} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "V12B converts campaign-level research plans into experiment-level specifications.",
        "The output is intentionally non-executable and requires manual review before any future runtime, replay or strategy-related action.",
        "",
        "## Status",
        "",
        "Completed.",
        "",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="V12B Automatic Experiment Generator")
    parser.add_argument("--campaigns", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-experiments", type=int, default=20)
    args = parser.parse_args()

    campaigns_path = Path(args.campaigns)
    output_dir = Path(args.output_dir)

    campaigns = read_csv(campaigns_path)
    experiments = build_experiments(campaigns, args.max_experiments)

    experiment_fields = [
        "experiment_id",
        "campaign_id",
        "source_hypothesis_id",
        "experiment_title",
        "experiment_goal",
        "experiment_type",
        "priority",
        "required_archives",
        "input_artifacts",
        "planned_outputs",
        "execution_mode",
        "runtime_allowed",
        "replay_allowed",
        "strategy_change_allowed",
        "live_trading_allowed",
        "estimated_compute_cost",
        "review_requirement",
        "readiness",
        "execution_status",
        "guardrails",
    ]

    experiment_path = output_dir / "v12b_experiment_specs.csv"
    manifest_path = output_dir / "v12b_experiment_manifest.csv"
    report_path = output_dir / f"V12B_AUTOMATIC_EXPERIMENT_GENERATOR_REPORT_{date.today().isoformat()}.md"

    write_csv(experiment_path, experiments, experiment_fields)

    manifest_rows = [
        {
            "artifact": "v12b_experiment_specs.csv",
            "path": str(experiment_path),
            "rows": len(experiments),
            "status": "created",
        },
        {
            "artifact": "V12B_AUTOMATIC_EXPERIMENT_GENERATOR_REPORT",
            "path": str(report_path),
            "rows": 1,
            "status": "created",
        },
    ]
    write_csv(manifest_path, manifest_rows, ["artifact", "path", "rows", "status"])

    write_report(report_path, experiments, campaigns_path)

    print("PASS: V12B automatic experiment generator completed")
    print(f"experiments: {len(experiments)}")
    print(f"experiment_csv: {experiment_path}")
    print(f"manifest_csv: {manifest_path}")
    print(f"report_md: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
