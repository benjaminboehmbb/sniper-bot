#!/usr/bin/env python3
# tools/gs_input_preflight.py
#
# Purpose:
#   Fail-fast input validator for simtraderGS CSVs.
#   Enforces Goldstandard schema expectations:
#     - close exists, numeric, finite, no NaN in window
#     - signals are ONLY consumed via *_signal columns (no fallback)
#     - *_signal values are in {-1, 0, +1} (integer-like)
#     - regime cols (optional) in {-1, 0, +1}
#     - timestamp monotonicity if a timestamp column exists
#
# Usage:
#   python3 tools/gs_input_preflight.py --csv data/...REGIMEV1.csv --rows 200000 --offset 0 --regime_cols regime_v1,regime_v2
#   python3 tools/gs_input_preflight.py --csv data/...REGIMEV2.csv --rows 200000 --offset 1500000 --require_signals rsi,macd,ma200 --regime_cols regime_v2
#
# Output:
#   Minimal ASCII report. Exits non-zero on FAIL.

from __future__ import annotations

import argparse
import sys
import os
from typing import List, Dict, Tuple, Optional

import pandas as pd
import numpy as np


ALLOWED_SIGNAL_VALUES = {-1, 0, 1}


def die(msg: str) -> None:
    raise SystemExit(f"[FAIL] {msg}")


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def info(msg: str) -> None:
    print(f"[info] {msg}")


def split_csv_list(s: str) -> List[str]:
    s = (s or "").strip()
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]


def find_timestamp_col(df: pd.DataFrame, preferred: Optional[str]) -> Optional[str]:
    if preferred:
        if preferred in df.columns:
            return preferred
        die(f"timestamp_col specified but missing: {preferred}")

    # common candidates (binance style + typical normalized)
    candidates = [
        "open_time",
        "close_time",
        "timestamp",
        "ts",
        "time",
        "date",
        "datetime",
    ]
    for c in candidates:
        if c in df.columns:
            return c
    return None


def coerce_timestamp_series(s: pd.Series) -> pd.Series:
    # If numeric (ms), keep as int; if string, parse.
    if pd.api.types.is_numeric_dtype(s):
        # treat as integer-like
        return pd.to_numeric(s, errors="coerce")
    # attempt datetime parse
    dt = pd.to_datetime(s, errors="coerce", utc=True)
    # convert to int64 ns for monotonic check
    return dt.view("int64")


def check_monotonic(ts: pd.Series, name: str) -> None:
    if ts.isna().any():
        die(f"timestamp_col '{name}' has NaN/unparseable values in window")
    # strictly increasing is ideal; allow non-decreasing if duplicates exist
    arr = ts.to_numpy()
    if np.any(arr[1:] < arr[:-1]):
        die(f"timestamp_col '{name}' is NOT monotonic non-decreasing in window")
    ok(f"timestamp monotonic PASS ({name})")


def check_close(df: pd.DataFrame) -> None:
    if "close" not in df.columns:
        die("missing required column: close")
    s = pd.to_numeric(df["close"], errors="coerce")
    if s.isna().any():
        die("close has NaN/unparseable values in window")
    if not np.isfinite(s.to_numpy()).all():
        die("close has non-finite values (inf/-inf) in window")
    ok("close numeric+finite PASS")


def is_integer_like(series: pd.Series) -> pd.Series:
    # Accept ints and float values that are exactly -1/0/1
    v = pd.to_numeric(series, errors="coerce")
    return v.isin(list(ALLOWED_SIGNAL_VALUES))


def check_signal_col(df: pd.DataFrame, col: str) -> Tuple[int, int, Dict[int, int]]:
    if col not in df.columns:
        die(f"missing required signal column: {col}")
    s = df[col]
    v = pd.to_numeric(s, errors="coerce")
    if v.isna().any():
        die(f"{col} contains NaN/unparseable values in window")
    if not np.isfinite(v.to_numpy()).all():
        die(f"{col} contains non-finite values in window")

    mask_ok = v.isin(list(ALLOWED_SIGNAL_VALUES))
    if not mask_ok.all():
        bad = v[~mask_ok].head(10).tolist()
        die(f"{col} has values outside {{-1,0,1}}. Examples: {bad}")

    counts = {k: int((v == k).sum()) for k in (-1, 0, 1)}
    zeros = counts[0]
    n = int(len(v))
    return n, zeros, counts


def warn_raw_indicator_columns(df: pd.DataFrame, required_signals: List[str]) -> None:
    # If user requests signals rsi,macd,ma200 we expect rsi_signal etc.
    # We warn (not fail) if raw columns exist, but we DO NOT fall back.
    raw_present = []
    for k in required_signals:
        if k in df.columns:
            raw_present.append(k)
    if raw_present:
        info(f"note: raw indicator columns present (ignored by GS): {raw_present}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV path")
    ap.add_argument("--rows", type=int, default=200000, help="window rows")
    ap.add_argument("--offset", type=int, default=0, help="window offset")
    ap.add_argument("--require_signals", default="", help="Comma list of signal base names, e.g. rsi,macd,ma200")
    ap.add_argument("--regime_cols", default="", help="Comma list of regime columns to validate if present/required")
    ap.add_argument("--timestamp_col", default="", help="Optional explicit timestamp column to check monotonicity")
    ap.add_argument("--require_timestamp", action="store_true", help="Fail if no timestamp column can be found")
    ap.add_argument("--fail_on_all_zero_signals", action="store_true",
                    help="Fail if any required signal is all zeros in the window")
    args = ap.parse_args()

    csv_path = args.csv
    if not os.path.exists(csv_path):
        # allow relative to repo root in common usage
        die(f"csv not found: {csv_path}")

    df_all = pd.read_csv(csv_path)
    df = df_all.iloc[args.offset : args.offset + args.rows].copy()

    info(f"CSV: {csv_path}")
    info(f"WINDOW: offset={args.offset} rows={len(df)} (requested rows={args.rows})")
    if len(df) <= 0:
        die("window is empty")

    # timestamp check (if available)
    ts_col = find_timestamp_col(df, args.timestamp_col.strip() or None)
    if ts_col is None:
        if args.require_timestamp:
            die("no timestamp column found (require_timestamp is set)")
        info("timestamp: not checked (no timestamp column found)")
    else:
        ts = coerce_timestamp_series(df[ts_col])
        check_monotonic(ts, ts_col)

    # close
    check_close(df)

    # required signals
    req = split_csv_list(args.require_signals)
    if not req:
        info("signals: no --require_signals specified (skipping signal checks)")
    else:
        warn_raw_indicator_columns(df, req)

        report_rows: List[str] = []
        for base in req:
            col = f"{base}_signal"
            n, zeros, counts = check_signal_col(df, col)
            zrate = zeros / max(1, n)
            report_rows.append(
                f"{col}: n={n} counts(-1/0/1)={counts[-1]}/{counts[0]}/{counts[1]} zero_rate={zrate:.3f}"
            )
            if args.fail_on_all_zero_signals and zeros == n:
                die(f"{col} is ALL ZERO in window (fail_on_all_zero_signals)")
        ok("signals domain PASS")
        for line in report_rows:
            info(line)

    # regime cols (optional required by user)
    reg_cols = split_csv_list(args.regime_cols)
    if reg_cols:
        for rc in reg_cols:
            if rc not in df.columns:
                die(f"missing regime column: {rc}")
            _n, _zeros, counts = check_signal_col(df, rc)
            info(f"{rc}: n={_n} counts(-1/0/1)={counts[-1]}/{counts[0]}/{counts[1]}")
        ok("regime cols PASS")
    else:
        info("regime cols: not checked (no --regime_cols specified)")

    print("[ok] GS INPUT PREFLIGHT: ALL PASS")


if __name__ == "__main__":
    main()
