#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V10B

Validation Specification Generator

ASCII only.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def validation_type(phase: str) -> str:
    return {
        "CONTROLLED_REPLAY_READY": "REPLAY_PLUS_RUNTIME",
        "RUNTIME_VALIDATION_READY": "REPLAY_PLUS_RUNTIME",
        "DESIGN_ONLY": "DESIGN_ONLY",
        "ARCHIVE_EXPANSION_REQUIRED": "ARCHIVE_EXPANSION",
        "REJECTED": "NONE",
    }.get(phase, "DESIGN_ONLY")


def yesno(flag: bool) -> str:
    return "yes" if flag else "no"


def runtime_required(vtype: str) -> bool:
    return vtype == "REPLAY_PLUS_RUNTIME"


def replay_required(vtype: str) -> bool:
    return vtype in (
        "REPLAY_ONLY",
        "REPLAY_PLUS_RUNTIME",
    )


def estimated_runtime(vtype: str) -> str:
    if vtype == "REPLAY_PLUS_RUNTIME":
        return "high"
    if vtype == "ARCHIVE_EXPANSION":
        return "medium"
    if vtype == "DESIGN_ONLY":
        return "low"
    return "none"


def validation_sequence(vtype: str) -> str:
    if vtype == "REPLAY_PLUS_RUNTIME":
        return (
            "Replay -> Metric Verification -> "
            "Cross Archive Comparison -> Runtime -> Acceptance"
        )

    if vtype == "ARCHIVE_EXPANSION":
        return (
            "Collect Archives -> Replay -> "
            "Metric Verification -> Acceptance"
        )

    if vtype == "DESIGN_ONLY":
        return (
            "Specification Review -> Approval"
        )

    return "None"


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--v10a-csv",
        required=True,
    )

    parser.add_argument(
        "--out-dir",
        required=True,
    )

    args = parser.parse_args()

    rows = read_csv(Path(args.v10a_csv))

    out = []

    for row in rows:

        phase = row["validation_phase"]

        vtype = validation_type(phase)

        out.append({

            "validation_id":
                row["validation_id"],

            "hypothesis_id":
                row["hypothesis_id"],

            "hypothesis_group":
                row["group"],

            "validation_phase":
                phase,

            "validation_type":
                vtype,

            "replay_required":
                yesno(replay_required(vtype)),

            "runtime_required":
                yesno(runtime_required(vtype)),

            "required_archives":
                row["required_archives_min"],

            "required_trades":
                row["required_trades_min"],

            "metrics_to_measure":
                row["required_metrics"],

            "acceptance_criteria":
                row["acceptance_criteria"],

            "rejection_criteria":
                row["failure_criteria"],

            "validation_sequence":
                validation_sequence(vtype),

            "execution_environment":
                row["execution_environment"],

            "documentation_required":
                row["documentation_required"],

            "estimated_runtime":
                estimated_runtime(vtype),

            "status":
                "READY_FOR_EXECUTION"
                if vtype != "NONE"
                else "REJECTED",

        })

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "v10b_validation_specifications.csv"

    write_csv(csv_path, out)

    report = out_dir / "V10B_VALIDATION_SPECIFICATION_REPORT_2026-06-19.md"

    report.write_text(
f"""# V10B VALIDATION SPECIFICATION REPORT

## Summary

Validation specifications generated: {len(out)}

Replay required:
{sum(r["replay_required"]=="yes" for r in out)}

Runtime required:
{sum(r["runtime_required"]=="yes" for r in out)}

Ready for execution:
{sum(r["status"]=="READY_FOR_EXECUTION" for r in out)}

Rejected:
{sum(r["status"]=="REJECTED" for r in out)}

Generated files

- v10b_validation_specifications.csv
- V10B_VALIDATION_SPECIFICATION_REPORT_2026-06-19.md
""",
encoding="utf-8"
)

    print("V10B validation specification generator completed")
    print("input:", len(rows))
    print("specifications:", len(out))
    print("report:", report)
    print("csv:", csv_path)


if __name__ == "__main__":
    main()

