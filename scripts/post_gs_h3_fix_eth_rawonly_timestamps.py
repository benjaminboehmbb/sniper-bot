#!/usr/bin/env python3
# scripts/post_gs_h3_fix_eth_rawonly_timestamps.py
#
# Fix ETH RAWONLY CSV timestamps:
# - Ensure timestamp_utc is parseable for all rows
# - Force minute alignment (floor to minute)
# - Drop duplicates created by flooring (keep first)
# - Ensure monotonic increasing
#
# Input:
#   data/ethusdt_1m_postGS/normalized/ethusdt_1m_price_2017_2025_POSTGS_RAWONLY_2026-01-10_13-17-26.csv
#
# Output:
#   data/ethusdt_1m_postGS/normalized/ethusdt_1m_price_2017_2025_POSTGS_RAWONLY_FIXED_UTC_MINUTE_<runid>.csv
#
# ASCII-only.

import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

IN_CSV = REPO_ROOT / "data" / "ethusdt_1m_postGS" / "normalized" / \
    "ethusdt_1m_price_2017_2025_POSTGS_RAWONLY_2026-01-10_13-17-26.csv"

OUT_DIR = REPO_ROOT / "data" / "ethusdt_1m_postGS" / "normalized"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

def die(msg: str, code: int = 2) -> None:
    print(f"[FATAL] {msg}")
    sys.exit(code)

def main() -> None:
    if not IN_CSV.exists():
        die(f"Missing input: {IN_CSV}")

    print(f"[load] {IN_CSV}")
    df = pd.read_csv(IN_CSV)
    if "timestamp_utc" not in df.columns:
        die("Missing column: timestamp_utc")

    # Robust parse: handles mixed formats (with/without fractional seconds)
    ts = pd.to_datetime(df["timestamp_utc"], utc=True, errors="coerce", format="mixed")

    bad = ts.isna().sum()
    if bad:
        # Save a small sample to stdout
        sample = df.loc[ts.isna(), "timestamp_utc"].head(10).tolist()
        die(f"Unparseable timestamp_utc rows: {bad}. sample={sample}")

    # Force minute alignment
    ts_floor = ts.dt.floor("min")
    changed = (ts_floor != ts).sum()

    df["timestamp_utc"] = ts_floor.dt.strftime("%Y-%m-%d %H:%M:%S%z")

    # Sort + drop duplicates on timestamp
    df = df.sort_values("timestamp_utc")
    before = len(df)
    df = df.drop_duplicates(subset=["timestamp_utc"], keep="first")
    dropped = before - len(df)

    # Monotonic check
    ts2 = pd.to_datetime(df["timestamp_utc"], utc=True, errors="raise", format="mixed")
    if not ts2.is_monotonic_increasing:
        die("timestamp_utc not monotonic after fix")

    out_name = f"ethusdt_1m_price_2017_2025_POSTGS_RAWONLY_FIXED_UTC_MINUTE_{now_ts()}.csv"
    out_path = OUT_DIR / out_name
    df.to_csv(out_path, index=False)

    print(f"[ok] wrote: {out_path}")
    print(f"[ok] rows: {len(df)} (dropped_dups={dropped})")
    print(f"[ok] timestamps_floored: {int(changed)}")

if __name__ == "__main__":
    main()
