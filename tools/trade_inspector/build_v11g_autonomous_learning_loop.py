#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_step(name: str, command: list[str]) -> dict[str, object]:
    started = now_utc()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        rc = result.returncode
        status = "PASS" if rc == 0 else "FAIL"
        stdout_tail = result.stdout[-3000:].replace("\n", "\\n")
        stderr_tail = result.stderr[-3000:].replace("\n", "\\n")
    except Exception as exc:
        rc = -1
        status = "FAIL"
        stdout_tail = ""
        stderr_tail = f"{type(exc).__name__}: {exc}"

    finished = now_utc()

    return {
        "step": name,
        "status": status,
        "return_code": rc,
        "started_at_utc": started,
        "finished_at_utc": finished,
        "command": " ".join(command),
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v10f-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    root_out = Path(args.out_dir)
    root_out.mkdir(parents=True, exist_ok=True)

    v10f_csv = Path(args.v10f_csv)

    out_v11a = root_out / "v11a"
    out_v11b = root_out / "v11b"
    out_v11c = root_out / "v11c"
    out_v11d = root_out / "v11d"
    out_v11e = root_out / "v11e"
    out_v11f = root_out / "v11f"

    steps = [
        (
            "V11A",
            [
                sys.executable,
                "tools/trade_inspector/build_v11a_replay_result_evaluator.py",
                "--v10f-csv",
                str(v10f_csv),
                "--out-dir",
                str(out_v11a),
            ],
            out_v11a / "v11a_replay_result_evaluation.csv",
        ),
        (
            "V11B",
            [
                sys.executable,
                "tools/trade_inspector/build_v11b_validation_evidence_updater.py",
                "--v11a-csv",
                str(out_v11a / "v11a_replay_result_evaluation.csv"),
                "--out-dir",
                str(out_v11b),
            ],
            out_v11b / "v11b_validation_evidence_updates.csv",
        ),
        (
            "V11C",
            [
                sys.executable,
                "tools/trade_inspector/build_v11c_research_knowledge_base.py",
                "--v11b-csv",
                str(out_v11b / "v11b_validation_evidence_updates.csv"),
                "--out-dir",
                str(out_v11c),
            ],
            out_v11c / "v11c_research_knowledge_base.csv",
        ),
        (
            "V11D",
            [
                sys.executable,
                "tools/trade_inspector/build_v11d_knowledge_consistency_engine.py",
                "--v11c-csv",
                str(out_v11c / "v11c_research_knowledge_base.csv"),
                "--out-dir",
                str(out_v11d),
            ],
            out_v11d / "v11d_knowledge_consistency.csv",
        ),
        (
            "V11E",
            [
                sys.executable,
                "tools/trade_inspector/build_v11e_knowledge_evolution_tracker.py",
                "--v11c-csv",
                str(out_v11c / "v11c_research_knowledge_base.csv"),
                "--out-dir",
                str(out_v11e),
            ],
            out_v11e / "v11e_knowledge_evolution.csv",
        ),
        (
            "V11F",
            [
                sys.executable,
                "tools/trade_inspector/build_v11f_hypothesis_prioritization_engine.py",
                "--v11d-csv",
                str(out_v11d / "v11d_knowledge_consistency.csv"),
                "--v11e-csv",
                str(out_v11e / "v11e_knowledge_evolution.csv"),
                "--out-dir",
                str(out_v11f),
            ],
            out_v11f / "v11f_hypothesis_priorities.csv",
        ),
    ]

    manifest: list[dict[str, object]] = []
    loop_status = "PASS"

    for name, command, expected_output in steps:
        row = run_step(name, command)

        if row["status"] == "PASS" and not expected_output.exists():
            row["status"] = "FAIL"
            row["stderr_tail"] = f"expected_output_missing:{expected_output}"

        manifest.append(row)

        if row["status"] != "PASS":
            loop_status = "FAIL"
            break

    manifest_csv = root_out / "v11g_autonomous_learning_loop_manifest.csv"
    write_csv(manifest_csv, manifest)

    report = root_out / "V11G_AUTONOMOUS_LEARNING_LOOP_REPORT_2026-06-19.md"

    lines: list[str] = []
    lines.append("# V11G AUTONOMOUS LEARNING LOOP REPORT")
    lines.append("")
    lines.append("Date: 2026-06-19")
    lines.append("Scope: Trade Inspector V11G")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append("Coordinate the complete V11 learning pipeline from replay execution results to hypothesis priorities.")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- Source file: {v10f_csv}")
    lines.append("")
    lines.append("## Loop Status")
    lines.append("")
    lines.append(f"- Status: {loop_status}")
    lines.append(f"- Steps attempted: {len(manifest)}")
    lines.append("")
    lines.append("## Step Summary")
    lines.append("")
    lines.append("| step | status | return_code |")
    lines.append("|---|---|---:|")
    for row in manifest:
        lines.append(f"| {row['step']} | {row['status']} | {row['return_code']} |")
    lines.append("")
    lines.append("## Guardrail")
    lines.append("")
    lines.append("V11G only coordinates the V11 learning pipeline. It does not execute replay and does not modify strategy logic.")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- v11g_autonomous_learning_loop_manifest.csv")
    lines.append("- V11G_AUTONOMOUS_LEARNING_LOOP_REPORT_2026-06-19.md")
    lines.append("")

    report.write_text("\n".join(lines), encoding="utf-8")

    print("V11G autonomous learning loop completed")
    print("loop_status:", loop_status)
    print("steps_attempted:", len(manifest))
    print("report:", report)
    print("manifest:", manifest_csv)

    return 0 if loop_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
