#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Trade Inspector V9F

Experiment Portfolio Optimizer

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


def fnum(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--v9d-csv", required=True)
    parser.add_argument("--v9e-csv", required=True)
    parser.add_argument("--out-dir", required=True)

    args = parser.parse_args()

    consistency = read_csv(Path(args.v9d_csv))
    conflicts = read_csv(Path(args.v9e_csv))

    penalty = {}

    for row in conflicts:

        rel = row["relationship_class"]

        if rel in (
            "MUTUALLY_EXCLUSIVE_CONTEXT",
            "POTENTIAL_CONFLICT",
        ):
            p = 20

        elif rel == "REDUNDANT_PARENT_CHILD":
            p = 10

        else:
            p = 0

        a = row["hypothesis_a_id"]
        b = row["hypothesis_b_id"]

        penalty[a] = penalty.get(a, 0) + p
        penalty[b] = penalty.get(b, 0) + p

    portfolio = []

    for i, row in enumerate(consistency, start=1):

        hid = f"H{i:03d}"

        score = (
            fnum(row.get("consistency_score"))
            - penalty.get(hid, 0)
        )

        if score >= 80:
            cls = "PRIORITY_1"

        elif score >= 60:
            cls = "PRIORITY_2"

        elif score >= 40:
            cls = "WATCHLIST"

        else:
            cls = "REJECT"

        portfolio.append(
            {
                "hypothesis_id": hid,
                "group": row.get("group"),
                "consistency_score": row.get("consistency_score"),
                "conflict_penalty": penalty.get(hid, 0),
                "portfolio_score": round(score, 2),
                "portfolio_class": cls,
            }
        )

    portfolio.sort(
        key=lambda r: r["portfolio_score"],
        reverse=True,
    )

    outdir = Path(args.out_dir)

    csv_out = outdir / "v9f_experiment_portfolio.csv"

    report = outdir / "V9F_EXPERIMENT_PORTFOLIO_REPORT_2026-06-18.md"

    write_csv(csv_out, portfolio)

    counts = {}

    for r in portfolio:
        counts[r["portfolio_class"]] = counts.get(
            r["portfolio_class"], 0
        ) + 1

    with report.open("w", encoding="utf-8") as fh:

        fh.write("# V9F EXPERIMENT PORTFOLIO REPORT\n\n")

        fh.write("## Portfolio Summary\n\n")

        for k in (
            "PRIORITY_1",
            "PRIORITY_2",
            "WATCHLIST",
            "REJECT",
        ):
            fh.write(f"- {k}: {counts.get(k,0)}\n")

        fh.write("\n## Top Portfolio\n\n")

        fh.write("|Rank|Hypothesis|Score|Class|\n")
        fh.write("|---:|---|---:|---|\n")

        for i, r in enumerate(portfolio[:20], 1):

            fh.write(
                f"|{i}|{r['group']}|{r['portfolio_score']}|{r['portfolio_class']}|\n"
            )

    print("V9F portfolio optimizer completed")
    print("input:", len(consistency))
    print("portfolio:", len(portfolio))
    print("report:", report)
    print("csv:", csv_out)


if __name__ == "__main__":
    main()

