#!/usr/bin/env python3
# tools/gs_regime_quality_report.py
#
# Purpose:
#   Quantify regime label quality for GS CSVs (no simtrader changes).
#   Outputs objective metrics:
#     - shares per regime state (-1/0/+1)
#     - run-length distribution per state (min/median/p90/max, mean)
#     - flip rate (transitions per 100k bars)
#     - short-run share (<60/<120/<240 bars)
#     - transition matrix counts
#     - windowed report over multiple offsets
#
# Notes:
#   - ASCII only.
#   - This is a "foundation" tool: measure first, change later.
#
# Examples:
#   python3 tools/gs_regime_quality_report.py \
#     --csv data/...REGIMEV1.csv --regime_col regime_v1 --timestamp_col timestamp_utc \
#     --rows 200000 --offsets "0,500000,1000000,1500000"
#
#   python3 tools/gs_regime_quality_report.py \
#     --csv data/...REGIMEV2.csv --regime_col regime_v2 --timestamp_col timestamp_utc \
#     --rows 500000 --offsets "0,1000000"

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


ALLOWED = {-1, 0, 1}


def die(msg: str) -> None:
    raise SystemExit(f"[FAIL] {msg}")


def qstats(x: np.ndarray) -> Dict[str, float]:
    if x.size == 0:
        return {"n": 0}
    x = np.asarray(x, dtype=float)
    return {
        "n": int(x.size),
        "min": float(np.min(x)),
        "p50": float(np.quantile(x, 0.50)),
        "p90": float(np.quantile(x, 0.90)),
        "mean": float(np.mean(x)),
        "max": float(np.max(x)),
    }


def run_lengths(states: np.ndarray) -> Dict[int, np.ndarray]:
    # states: int array of -1/0/1
    out: Dict[int, List[int]] = {-1: [], 0: [], 1: []}
    n = len(states)
    if n == 0:
        return {-1: np.array([]), 0: np.array([]), 1: np.array([])}

    cur = int(states[0])
    length = 1
    for i in range(1, n):
        v = int(states[i])
        if v == cur:
            length += 1
        else:
            out[cur].append(length)
            cur = v
            length = 1
    out[cur].append(length)

    return {k: np.asarray(v, dtype=int) for k, v in out.items()}


def transition_counts(states: np.ndarray) -> Dict[Tuple[int, int], int]:
    # counts of (from -> to) where from != to
    counts: Dict[Tuple[int, int], int] = {}
    if len(states) < 2:
        return counts
    a = states[:-1]
    b = states[1:]
    mask = a != b
    af = a[mask]
    bf = b[mask]
    for x, y in zip(af.tolist(), bf.tolist()):
        key = (int(x), int(y))
        counts[key] = counts.get(key, 0) + 1
    return counts


def fmt_state(s: int) -> str:
    if s == 1:
        return "bull(+1)"
    if s == -1:
        return "bear(-1)"
    return "side(0)"


def check_timestamp(df: pd.DataFrame, timestamp_col: str) -> None:
    if timestamp_col not in df.columns:
        die(f"timestamp_col missing: {timestamp_col}")
    ts = df[timestamp_col]
    # numeric or datetime-like string
    if pd.api.types.is_numeric_dtype(ts):
        v = pd.to_numeric(ts, errors="coerce")
    else:
        v = pd.to_datetime(ts, errors="coerce", utc=True).view("int64")
    if pd.isna(v).any():
        die(f"timestamp_col has NaN/unparseable values: {timestamp_col}")
    arr = np.asarray(v)
    if np.any(arr[1:] < arr[:-1]):
        die(f"timestamp_col is not monotonic non-decreasing: {timestamp_col}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--regime_col", required=True, help="regime_v1 or regime_v2")
    ap.add_argument("--timestamp_col", default="timestamp_utc")
    ap.add_argument("--rows", type=int, default=200000)
    ap.add_argument("--offsets", default="0", help="Comma list of offsets")
    ap.add_argument("--out_report", default="", help="Optional path to write report txt")
    args = ap.parse_args()

    csv_path = args.csv
    if not os.path.exists(csv_path):
        die(f"csv not found: {csv_path}")

    offsets = []
    for p in (args.offsets or "").split(","):
        p = p.strip()
        if not p:
            continue
        offsets.append(int(p))
    if not offsets:
        offsets = [0]

    # Read header to validate columns early
    head = pd.read_csv(csv_path, nrows=5)
    cols = set(head.columns)

    if args.regime_col not in cols:
        die(f"regime_col missing: {args.regime_col}")

    if args.timestamp_col not in cols:
        die(f"timestamp_col missing: {args.timestamp_col}")

    # Read only needed columns for speed/memory
    usecols = [args.timestamp_col, args.regime_col]
    df_all = pd.read_csv(csv_path, usecols=usecols)

    lines: List[str] = []
    def emit(s: str) -> None:
        print(s)
        lines.append(s)

    emit(f"REPO_ROOT: {os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}")
    emit(f"CSV: {csv_path}")
    emit(f"REGIME_COL: {args.regime_col}")
    emit(f"TIMESTAMP_COL: {args.timestamp_col}")
    emit(f"ROWS(per window): {args.rows}")
    emit(f"OFFSETS: {offsets}")
    emit("=" * 60)

    for off in offsets:
        df = df_all.iloc[off: off + args.rows].copy()
        if len(df) == 0:
            emit(f"[WARN] offset={off}: empty window, skipping")
            emit("-" * 60)
            continue

        # timestamp monotonic
        check_timestamp(df, args.timestamp_col)

        r = pd.to_numeric(df[args.regime_col], errors="coerce")
        if r.isna().any():
            die(f"regime has NaN/unparseable values at offset={off}")
        rv = r.astype(int).to_numpy()
        bad_mask = ~np.isin(rv, list(ALLOWED))
        if bad_mask.any():
            bad = rv[bad_mask][:10].tolist()
            die(f"regime values outside {{-1,0,1}} at offset={off}. Examples: {bad}")

        n = len(rv)
        counts = {k: int((rv == k).sum()) for k in (-1, 0, 1)}
        shares = {k: counts[k] / n for k in (-1, 0, 1)}

        # run lengths
        rl = run_lengths(rv)

        # flips
        trans = transition_counts(rv)
        flips = int(sum(trans.values()))
        flip_per_100k = flips / n * 100000.0

        # short-run shares
        thresholds = [60, 120, 240]
        short = {}
        for state in (-1, 0, 1):
            arr = rl[state]
            if arr.size == 0:
                short[state] = {t: 0.0 for t in thresholds}
                continue
            short[state] = {t: float(np.mean(arr < t)) for t in thresholds}

        emit(f"WINDOW offset={off} rows={n}")
        emit(f"SHARES: bear(-1)={shares[-1]:.6f} side(0)={shares[0]:.6f} bull(+1)={shares[1]:.6f}")
        emit(f"FLIPS: {flips}  flip_rate_per_100k={flip_per_100k:.3f}")

        for state in (-1, 0, 1):
            st = fmt_state(state)
            stats = qstats(rl[state])
            if stats.get("n", 0) == 0:
                emit(f"RUNLEN {st}: n=0")
                continue
            emit(
                f"RUNLEN {st}: n={stats['n']} min={stats['min']:.0f} "
                f"p50={stats['p50']:.1f} p90={stats['p90']:.1f} mean={stats['mean']:.2f} max={stats['max']:.0f}"
            )
            emit(
                f"  short_share(<60/<120/<240) = "
                f"{short[state][60]:.3f}/{short[state][120]:.3f}/{short[state][240]:.3f}"
            )

        # transition matrix (compact)
        emit("TRANSITIONS (from->to) counts (only changes):")
        # order transitions for readability
        order = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]
        parts = []
        for a, b in order:
            c = trans.get((a, b), 0)
            parts.append(f"{a}->{b}:{c}")
        emit("  " + "  ".join(parts))
        emit("-" * 60)

    if args.out_report:
        outp = args.out_report
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        with open(outp, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"[ok] Wrote report: {outp}")


if __name__ == "__main__":
    main()
