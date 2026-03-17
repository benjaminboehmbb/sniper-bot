#!/usr/bin/env python3
# tools/build_regime_v2_from_v1.py
#
# Purpose:
#   Build Regime v2 labels from an existing Regime v1 column (e.g. regime_v1 in {-1,0,1}).
#   Regime v2 adds stability via:
#     - minimum duration (min_state_bars) before a new regime is accepted
#     - optional transition restriction (e.g. disallow direct bull<->bear flips without going through side)
#
# Design constraints:
#   - Does NOT touch engine/simtraderGS.py
#   - Pure labeling/policy layer
#   - ASCII-only output
#
# Usage (WSL, repo root):
#   python3 tools/build_regime_v2_from_v1.py \
#     --in_csv  data/.../WITH_SIGNALS_REGIMEV1.csv \
#     --out_csv data/.../WITH_SIGNALS_REGIMEV2.csv \
#     --in_col  regime_v1 \
#     --out_col regime_v2 \
#     --min_state_bars 720 \
#     --no_direct_flip
#
# Notes:
#   - min_state_bars is in bars (1 bar = 1 minute for 1m data).
#   - Regime values: bull=+1, bear=-1, side=0.

from __future__ import annotations

import os
import sys
import argparse
from typing import Tuple, Dict

import numpy as np
import pandas as pd


def _fail(msg: str) -> None:
    raise SystemExit(f"[ERROR] {msg}")


def _shares(arr: np.ndarray) -> Dict[int, float]:
    n = int(arr.size)
    if n <= 0:
        return {-1: 0.0, 0: 0.0, 1: 0.0}
    return {
        1: float(np.mean(arr == 1)),
        -1: float(np.mean(arr == -1)),
        0: float(np.mean(arr == 0)),
    }


def _build_v2(
    v1: np.ndarray,
    min_state_bars: int,
    no_direct_flip: bool,
) -> Tuple[np.ndarray, int, int, int]:
    """
    Build v2 from v1 using minimum-duration confirmation.

    Algorithm:
      - Keep a current_state (initially v1[0]).
      - Track a candidate_state and how long it has been consistently observed.
      - Only accept candidate_state after min_state_bars consecutive bars.
      - If no_direct_flip is True, disallow direct bull<->bear switches:
          require side (0) to be accepted in between.
    Returns:
      v2 array and counts: accepted_changes, rejected_flips, rejected_runs
    """
    n = int(v1.size)
    if n == 0:
        return v1.copy(), 0, 0, 0

    # sanitize values into {-1,0,1}
    vv = np.where(v1 > 0, 1, np.where(v1 < 0, -1, 0)).astype(np.int8)

    v2 = np.empty(n, dtype=np.int8)

    current = int(vv[0])
    v2[0] = current

    cand = current
    cand_len = 0

    accepted_changes = 0
    rejected_direct_flips = 0
    rejected_runs = 0

    for i in range(1, n):
        x = int(vv[i])

        if x == current:
            # reset candidate tracking
            cand = current
            cand_len = 0
            v2[i] = current
            continue

        # candidate logic
        if x != cand:
            cand = x
            cand_len = 1
        else:
            cand_len += 1

        # accept candidate only if it persists long enough
        if cand_len >= min_state_bars:
            # transition restriction (optional)
            if no_direct_flip and ((current == 1 and cand == -1) or (current == -1 and cand == 1)):
                # direct flip not allowed; require side in between
                rejected_direct_flips += 1
                # force candidate back to current, keep state
                cand = current
                cand_len = 0
                v2[i] = current
            else:
                current = cand
                accepted_changes += 1
                cand_len = 0
                v2[i] = current
        else:
            v2[i] = current

    # Estimate rejected runs (candidate segments that never reached min_state_bars)
    # We approximate by counting raw v1 segments shorter than min_state_bars that differ from final v2 at same indices.
    # This is informational only.
    # (We keep it simple and robust, no heavy segment extraction.)
    diff = (vv != v2)
    if diff.any():
        # count contiguous diff runs shorter than min_state_bars
        idx = np.where(diff)[0]
        # group contiguous indices
        run_start = idx[0]
        prev = idx[0]
        for j in idx[1:]:
            if j == prev + 1:
                prev = j
            else:
                run_len = prev - run_start + 1
                if run_len < min_state_bars:
                    rejected_runs += 1
                run_start = j
                prev = j
        run_len = prev - run_start + 1
        if run_len < min_state_bars:
            rejected_runs += 1

    return v2, accepted_changes, rejected_direct_flips, rejected_runs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True, help="Input CSV path (relative or absolute). Must contain v1 regime col.")
    ap.add_argument("--out_csv", required=True, help="Output CSV path (relative or absolute).")
    ap.add_argument("--in_col", default="regime_v1", help="Input regime column name (values -1/0/1).")
    ap.add_argument("--out_col", default="regime_v2", help="Output regime column name to create.")
    ap.add_argument("--min_state_bars", type=int, default=720, help="Bars required to confirm a new regime.")
    ap.add_argument("--no_direct_flip", action="store_true", help="Disallow direct bull<->bear flips (force via side).")
    ap.add_argument("--report_txt", default="", help="Optional path to write a short report txt.")
    ap.add_argument("--limit_rows", type=int, default=0, help="Optional: limit rows for quick testing (0=all).")
    args = ap.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    in_csv = args.in_csv
    out_csv = args.out_csv
    if not os.path.isabs(in_csv):
        in_csv = os.path.join(repo_root, in_csv)
    if not os.path.isabs(out_csv):
        out_csv = os.path.join(repo_root, out_csv)

    if not os.path.isfile(in_csv):
        _fail(f"Input CSV not found: {in_csv}")

    if args.min_state_bars <= 0:
        _fail("min_state_bars must be > 0")

    df = pd.read_csv(in_csv)
    if args.limit_rows and args.limit_rows > 0:
        df = df.iloc[: args.limit_rows].copy()

    if args.in_col not in df.columns:
        _fail(f"Input column not found: {args.in_col}")

    v1 = df[args.in_col].to_numpy(dtype=float)
    v2, n_changes, n_rej_flip, n_rej_runs = _build_v2(
        v1=v1,
        min_state_bars=int(args.min_state_bars),
        no_direct_flip=bool(args.no_direct_flip),
    )

    df[args.out_col] = v2.astype(int)

    # Write output
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)

    # Report
    v1i = np.where(v1 > 0, 1, np.where(v1 < 0, -1, 0)).astype(np.int8)
    sh1 = _shares(v1i)
    sh2 = _shares(v2)

    lines = []
    lines.append("[ok] Wrote CSV:")
    lines.append(f"  out_csv: {out_csv}")
    lines.append("")
    lines.append("Params:")
    lines.append(f"  in_col={args.in_col} out_col={args.out_col}")
    lines.append(f"  min_state_bars={int(args.min_state_bars)}")
    lines.append(f"  no_direct_flip={'1' if args.no_direct_flip else '0'}")
    lines.append("")
    lines.append("Shares (v1): bull={:.6f} bear={:.6f} side={:.6f}".format(sh1[1], sh1[-1], sh1[0]))
    lines.append("Shares (v2): bull={:.6f} bear={:.6f} side={:.6f}".format(sh2[1], sh2[-1], sh2[0]))
    lines.append("")
    lines.append("Stability counters:")
    lines.append(f"  accepted_changes: {n_changes}")
    lines.append(f"  rejected_direct_flips: {n_rej_flip}")
    lines.append(f"  rejected_short_runs(approx): {n_rej_runs}")
    lines.append("")

    report = "\n".join(lines)
    print(report)

    if args.report_txt:
        rep = args.report_txt
        if not os.path.isabs(rep):
            rep = os.path.join(repo_root, rep)
        os.makedirs(os.path.dirname(rep), exist_ok=True)
        with open(rep, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[ok] Wrote report: {rep}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
