#!/usr/bin/env python3
# tools/build_gs_5m_from_1m.py
#
# Purpose:
#   Build a GS-compatible 5-minute CSV from an existing GS-compatible 1-minute CSV
#   by resampling OHLCV and "carrying" signal/regime/gate columns via LAST value
#   within each 5-minute bucket.
#
# Why this approach:
#   - Deterministic and simple (no indicator recomputation, no parameter drift)
#   - Preserves the semantics of already-built 1m signals/regime/gates
#   - Produces clean 5m-aligned rows for GS-style backtests
#
# Input contract (expected columns):
#   timestamp_utc, open, high, low, close, volume
#   plus optional: *_signal, regime_v1, allow_long_old, allow_short_old, allow_long, allow_short
#
# Output:
#   timestamp_utc is 5-minute aligned (minute%5==0) and monotonic increasing.
#
# Usage (example):
#   python3 -m tools.build_gs_5m_from_1m --in <1m_csv> --out <5m_csv>
#
# Notes:
#   - ASCII-only output/logging (Windows cp1252 safe)
#   - No web, no external deps beyond pandas/numpy

import argparse
import os
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd


REQUIRED_BASE_COLS = ["timestamp_utc", "open", "high", "low", "close", "volume"]

# Known GS-related optional columns we prefer to keep if present
KNOWN_OPTIONAL_COLS = [
    # signals
    "rsi_signal", "macd_signal", "bollinger_signal", "ma200_signal", "stoch_signal",
    "atr_signal", "ema50_signal", "adx_signal", "cci_signal", "mfi_signal", "obv_signal", "roc_signal",
    # regime + gates
    "regime_v1", "allow_long_old", "allow_short_old", "allow_long", "allow_short",
]


def die(msg: str, code: int = 2) -> None:
    print(f"[fatal] {msg}")
    raise SystemExit(code)


def info(msg: str) -> None:
    print(f"[info] {msg}")


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def _is_5m_aligned(ts: pd.Series) -> bool:
    # ts must be UTC-aware datetime64[ns, UTC]
    mins = ts.dt.minute
    secs = ts.dt.second
    return bool(((mins % 5) == 0).all() and (secs == 0).all())


def _default_out_path(inp: str) -> str:
    p = Path(inp)
    stem = p.name
    # conservative rename: just append marker
    out_name = stem.replace("_1m_", "_5m_")
    if out_name == stem:
        out_name = stem.replace("1m", "5m")
    out_name = out_name.rsplit(".", 1)[0] + "_RESAMPLED_5m.csv"
    return str(p.parent / out_name)


def _last_non_nan(x: pd.Series):
    # Return last non-NaN if any, else NaN
    if x is None or len(x) == 0:
        return np.nan
    # faster: find last valid index
    idx = x.last_valid_index()
    if idx is None:
        return np.nan
    return x.loc[idx]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input 1m GS-compatible CSV path")
    ap.add_argument("--out", dest="out", default="", help="Output 5m CSV path (default derived from input)")
    ap.add_argument("--rule", default="5T", help="Pandas resample rule (default: 5T)")
    ap.add_argument("--dropna", action="store_true",
                    help="Drop rows with any NaN in REQUIRED_BASE_COLS (recommended)")
    args = ap.parse_args()

    inp = args.inp
    out = args.out.strip() or _default_out_path(inp)

    if not os.path.isfile(inp):
        die(f"input not found: {inp}")

    info(f"read: {inp}")
    df = pd.read_csv(inp)

    missing = [c for c in REQUIRED_BASE_COLS if c not in df.columns]
    if missing:
        die(f"missing required cols: {missing}. cols={list(df.columns)}")

    # Parse timestamp_utc
    ts = pd.to_datetime(df["timestamp_utc"], utc=True, errors="raise", format="mixed")
    if (ts.dt.second != 0).any():
        die("timestamp_utc has non-zero seconds (not minute-aligned). Fix upstream first.")
    if not ts.is_monotonic_increasing:
        die("timestamp_utc is not monotonic increasing. Fix upstream first.")

    df["timestamp_utc"] = ts
    df = df.set_index("timestamp_utc", drop=True)

    # Ensure numeric base columns
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Decide which optional columns to keep
    keep_optional: List[str] = []
    for c in KNOWN_OPTIONAL_COLS:
        if c in df.columns:
            keep_optional.append(c)

    # Also keep any other *_signal columns not listed explicitly
    for c in df.columns:
        if c.endswith("_signal") and c not in keep_optional:
            keep_optional.append(c)

    # Resample aggregations:
    # - OHLCV: open=first, high=max, low=min, close=last, volume=sum
    # - signals/regime/gates: last non-NaN in bucket
    info(f"resample rule: {args.rule}")
    ohlc = df[["open", "high", "low", "close"]].resample(args.rule).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    vol = df[["volume"]].resample(args.rule).sum()

    out_df = pd.concat([ohlc, vol], axis=1)

    if keep_optional:
        opt = df[keep_optional].resample(args.rule).apply(_last_non_nan)
        out_df = pd.concat([out_df, opt], axis=1)

    # Drop completely empty buckets
    out_df = out_df.dropna(subset=["open", "high", "low", "close"], how="any")

    # Restore timestamp_utc column
    out_df = out_df.reset_index()
    out_df.rename(columns={"timestamp_utc": "timestamp_utc"}, inplace=True)

    # Validate 5m alignment and monotonicity
    ts2 = pd.to_datetime(out_df["timestamp_utc"], utc=True, errors="raise", format="mixed")
    if not ts2.is_monotonic_increasing:
        die("output timestamp_utc not monotonic increasing (unexpected).")
    if not _is_5m_aligned(ts2):
        die("output timestamp_utc not 5-minute aligned (unexpected).")

    # Optional dropna gate
    if args.dropna:
        before = len(out_df)
        out_df = out_df.dropna(subset=["open", "high", "low", "close", "volume"])
        after = len(out_df)
        info(f"dropna base cols: {before} -> {after}")

    # Column order: keep base first, then the rest (stable)
    base = ["timestamp_utc", "open", "high", "low", "close", "volume"]
    rest = [c for c in out_df.columns if c not in base]
    out_df = out_df[base + rest]

    # Write
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    info(f"write: {out}")
    out_df.to_csv(out, index=False)
    ok(f"wrote 5m CSV rows={len(out_df)} cols={len(out_df.columns)}")

    # Small summary (signals/gates presence)
    for c in ["allow_long", "allow_short", "regime_v1"]:
        if c in out_df.columns:
            ones = int((pd.to_numeric(out_df[c], errors="coerce").fillna(0).astype(int) != 0).sum())
            info(f"col {c} present; nonzero_rows={ones}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
