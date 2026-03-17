#!/usr/bin/env python3
# tools/gs_build_asymmetric_gate.py
#
# Purpose:
#   Build an asymmetric regime gate as a pure data-layer transform (no GS core change).
#   Rule:
#     allow_long  = (regime == +1)
#     allow_short = (regime == -1)
#     side (0) blocks new entries for both directions.
#
#   Writes a new CSV with updated allow_long/allow_short (and a small report).
#
# Notes:
#   - ASCII only.
#   - Uses chunked processing to handle large CSVs.
#
# Example:
#   python3 tools/gs_build_asymmetric_gate.py \
#     --in_csv data/...REGIMEV1.csv \
#     --out_csv data/...REGIMEV1_ASYMGATE.csv \
#     --regime_col regime_v1
#
from __future__ import annotations

import argparse
import os
import pandas as pd
import numpy as np


def die(msg: str) -> None:
    raise SystemExit(f"[FAIL] {msg}")


def info(msg: str) -> None:
    print(f"[info] {msg}")


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def to_int_series(s: pd.Series, name: str) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    if x.isna().any():
        bad = int(x.isna().sum())
        die(f"{name}: {bad} NaN/unparseable values")
    x = x.astype(int)
    bad_mask = ~x.isin([-1, 0, 1])
    if bad_mask.any():
        ex = x[bad_mask].head(10).tolist()
        die(f"{name}: values outside {{-1,0,1}}. Examples: {ex}")
    return x


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument("--regime_col", required=True)
    ap.add_argument("--timestamp_col", default="timestamp_utc")
    ap.add_argument("--chunksize", type=int, default=500000)
    ap.add_argument(
        "--keep_old",
        action="store_true",
        help="If set, keep old allow_long/allow_short as allow_long_old/allow_short_old.",
    )
    ap.add_argument(
        "--report",
        default="",
        help="Optional report path. Default: <out_csv base>_REPORT.txt",
    )
    args = ap.parse_args()

    if not os.path.exists(args.in_csv):
        die(f"in_csv not found: {args.in_csv}")

    head = pd.read_csv(args.in_csv, nrows=5)
    cols = list(head.columns)
    if args.regime_col not in cols:
        die(f"missing regime_col: {args.regime_col}")
    if args.timestamp_col not in cols:
        die(f"missing timestamp_col: {args.timestamp_col}")

    if args.report:
        report_path = args.report
    else:
        base, _ = os.path.splitext(args.out_csv)
        report_path = base + "_REPORT.txt"

    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    info(f"in_csv: {args.in_csv}")
    info(f"out_csv: {args.out_csv}")
    info(f"regime_col: {args.regime_col}")
    info(f"timestamp_col: {args.timestamp_col}")
    info(f"chunksize: {args.chunksize}")
    info(f"keep_old: {1 if args.keep_old else 0}")

    total_rows = 0
    counts_regime = {-1: 0, 0: 0, 1: 0}
    counts_allow = {"allow_long": 0, "allow_short": 0, "both": 0, "neither": 0}
    ts_prev = None
    wrote_header = False

    reader = pd.read_csv(args.in_csv, chunksize=args.chunksize)
    for chunk_idx, df in enumerate(reader):
        if args.regime_col not in df.columns:
            die(f"chunk missing regime_col (unexpected): {args.regime_col}")
        if args.timestamp_col not in df.columns:
            die(f"chunk missing timestamp_col (unexpected): {args.timestamp_col}")

        ts = df[args.timestamp_col]
        if pd.api.types.is_numeric_dtype(ts):
            ts_num = pd.to_numeric(ts, errors="coerce")
        else:
            ts_num = pd.to_datetime(ts, errors="coerce", utc=True).astype("int64")
        if ts_num.isna().any():
            die(f"timestamp_col has NaN/unparseable values in chunk {chunk_idx}")
        ts_arr = ts_num.to_numpy()
        if (ts_arr[1:] < ts_arr[:-1]).any():
            die(f"timestamp_col not monotonic within chunk {chunk_idx}")
        if ts_prev is not None and ts_arr[0] < ts_prev:
            die(f"timestamp_col not monotonic across chunks at chunk {chunk_idx}")
        ts_prev = ts_arr[-1]

        reg = to_int_series(df[args.regime_col], args.regime_col)

        allow_long = (reg == 1).astype(np.int8)
        allow_short = (reg == -1).astype(np.int8)

        total_rows += len(df)
        for k in (-1, 0, 1):
            counts_regime[k] += int((reg == k).sum())

        both = int(((allow_long == 1) & (allow_short == 1)).sum())
        neither = int(((allow_long == 0) & (allow_short == 0)).sum())
        counts_allow["allow_long"] += int((allow_long == 1).sum())
        counts_allow["allow_short"] += int((allow_short == 1).sum())
        counts_allow["both"] += both
        counts_allow["neither"] += neither

        if args.keep_old:
            if "allow_long" in df.columns and "allow_long_old" not in df.columns:
                df = df.rename(columns={"allow_long": "allow_long_old"})
            if "allow_short" in df.columns and "allow_short_old" not in df.columns:
                df = df.rename(columns={"allow_short": "allow_short_old"})
        else:
            for c in ("allow_long", "allow_short"):
                if c in df.columns:
                    df = df.drop(columns=[c])

        df["allow_long"] = allow_long
        df["allow_short"] = allow_short

        mode = "w" if not wrote_header else "a"
        header = not wrote_header
        df.to_csv(args.out_csv, index=False, mode=mode, header=header)
        wrote_header = True

        if chunk_idx == 0:
            ok(f"wrote first chunk rows={len(df)}")

    if total_rows == 0:
        die("no rows written")

    shares_regime = {k: counts_regime[k] / total_rows for k in (-1, 0, 1)}
    shares_allow_long = counts_allow["allow_long"] / total_rows
    shares_allow_short = counts_allow["allow_short"] / total_rows
    shares_neither = counts_allow["neither"] / total_rows

    lines = []
    lines.append("GS ASYMMETRIC REGIME GATE REPORT")
    lines.append(f"in_csv: {args.in_csv}")
    lines.append(f"out_csv: {args.out_csv}")
    lines.append(f"regime_col: {args.regime_col}")
    lines.append(f"timestamp_col: {args.timestamp_col}")
    lines.append(f"rows_total: {total_rows}")
    lines.append("")
    lines.append("Regime shares:")
    lines.append(
        f"  bear(-1)={shares_regime[-1]:.6f} side(0)={shares_regime[0]:.6f} bull(+1)={shares_regime[1]:.6f}"
    )
    lines.append("")
    lines.append("Allow shares (new entries):")
    lines.append(f"  allow_long = {shares_allow_long:.6f}")
    lines.append(f"  allow_short = {shares_allow_short:.6f}")
    lines.append(f"  neither (blocked) = {shares_neither:.6f}")
    lines.append("")
    lines.append("Rule:")
    lines.append("  allow_long  = (regime == +1)")
    lines.append("  allow_short = (regime == -1)")
    lines.append("  side(0) blocks both")
    lines.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    ok(f"Wrote CSV: {args.out_csv}")
    ok(f"Wrote report: {report_path}")


if __name__ == "__main__":
    main()
