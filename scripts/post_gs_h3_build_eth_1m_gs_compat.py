#!/usr/bin/env python3
# scripts/post_gs_h3_build_eth_1m_gs_compat.py
#
# Post-GS H3 preparation:
# Build a single normalized ETHUSDT 1m CSV from Binance monthly ZIPs.
#
# Robust timestamp handling:
# - Detect seconds vs milliseconds vs microseconds via magnitude
# - Convert to milliseconds epoch
# - Filter out-of-range open_time values to avoid pandas OutOfBoundsDatetime
# - Log anomalies per ZIP into results/POST_GS/H3_asset/logs/
#
# Output (raw-only stage, no signals/regime yet):
#   data/ethusdt_1m_postGS/normalized/ethusdt_1m_price_<start>_<end>_POSTGS_RAWONLY_<runid>.csv
#
# ASCII-only output.

import sys
import glob
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = REPO_ROOT / "data" / "ethusdt_1m_postGS" / "raw" / "monthly"
OUT_DIR = REPO_ROOT / "data" / "ethusdt_1m_postGS" / "normalized"
LOG_DIR = REPO_ROOT / "results" / "POST_GS" / "H3_asset" / "logs"

OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Binance spot monthly klines schema
BINANCE_COLS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "ignore",
]

NUM_COLS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
]


def now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")


def die(msg: str, code: int = 2) -> None:
    print(f"[FATAL] {msg}")
    sys.exit(code)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def list_monthly_zips() -> List[Path]:
    zips = sorted([Path(p) for p in glob.glob(str(RAW_DIR / "ETHUSDT-1m-*.zip"))])
    if not zips:
        die(f"No ZIPs found in {RAW_DIR}")
    return zips


def parse_year_month(name: str) -> Tuple[int, int]:
    # ETHUSDT-1m-YYYY-MM.zip
    base = Path(name).name
    parts = base.replace(".zip", "").split("-")
    y = int(parts[-2])
    m = int(parts[-1])
    return y, m


def read_one_csv_from_zip(zpath: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zpath, "r") as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        if len(names) != 1:
            die(f"ZIP {zpath.name} expected 1 CSV, found {len(names)}: {names[:5]}")
        with zf.open(names[0]) as f:
            df = pd.read_csv(f, header=None, names=BINANCE_COLS)
    return df


def log_anomaly(run_id: str, zip_name: str, info: Dict[str, Any]) -> None:
    p = LOG_DIR / f"eth_rawonly_anomaly_{run_id}_{zip_name.replace('.zip','')}.json"
    p.write_text(pd.Series(info).to_json(indent=2), encoding="utf-8")


def normalize_month(df: pd.DataFrame, y: int, m: int, run_id: str, zip_name: str) -> pd.DataFrame:
    # Coerce numerics
    for c in NUM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df["close_time"] = pd.to_numeric(df["close_time"], errors="coerce")

    # Drop rows missing essentials
    df = df.dropna(subset=["open_time", "open", "high", "low", "close", "volume"])
    if df.empty:
        info = {"year": y, "month": m, "zip": zip_name, "reason": "empty after NaN essential filter"}
        log_anomaly(run_id, zip_name, info)
        die(f"{zip_name}: empty after basic filtering")

    # Detect unit by magnitude:
    # seconds  ~ 1e9
    # millis   ~ 1e12
    # micros   ~ 1e15
    med = float(df["open_time"].median())
    assumed_unit = "ms"
    if med > 1e14:
        assumed_unit = "us"
        df["open_time"] = df["open_time"] / 1000.0
        df["close_time"] = df["close_time"] / 1000.0
    elif med < 1e11:
        assumed_unit = "s"
        df["open_time"] = df["open_time"] * 1000.0
        df["close_time"] = df["close_time"] * 1000.0

    # Hard bounds in ms to avoid OutOfBoundsDatetime and trash rows.
    # 2017-01-01 to 2026-12-31 23:59:59
    min_ms = 1483228800000
    max_ms = 1798675199000

    ot = df["open_time"]
    bad = (ot < min_ms) | (ot > max_ms) | (~ot.notna())
    bad_count = int(bad.sum())

    if bad_count > 0:
        sample_bad = df.loc[bad, "open_time"].head(10).tolist()
        sample_good = df.loc[~bad, "open_time"].head(3).tolist()
        info = {
            "year": y,
            "month": m,
            "zip": zip_name,
            "assumed_unit": assumed_unit,
            "median_open_time": med,
            "bad_count": bad_count,
            "rows_before": int(len(df)),
            "rows_after": int(len(df) - bad_count),
            "sample_bad_open_time_ms": sample_bad,
            "sample_good_open_time_ms": sample_good,
        }
        log_anomaly(run_id, zip_name, info)

    df = df.loc[~bad].copy()
    if df.empty:
        die(f"{zip_name}: all rows filtered by open_time bounds; see logs in {LOG_DIR}")

    # Convert timestamp safely
    df["open_time_i64"] = df["open_time"].astype("int64")
    df["timestamp_utc"] = pd.to_datetime(df["open_time_i64"], unit="ms", utc=True, errors="coerce")

    nat = int(df["timestamp_utc"].isna().sum())
    if nat:
        info = {
            "year": y,
            "month": m,
            "zip": zip_name,
            "assumed_unit": assumed_unit,
            "median_open_time": med,
            "reason": "NaT after to_datetime",
            "nat_count": nat,
        }
        log_anomaly(run_id, zip_name, info)
        df = df.dropna(subset=["timestamp_utc"])
        if df.empty:
            die(f"{zip_name}: empty after dropping NaT timestamps; see logs in {LOG_DIR}")

    out = df[
        [
            "timestamp_utc",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "number_of_trades",
            "quote_asset_volume",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "open_time_i64",
        ]
    ].rename(columns={"open_time_i64": "open_time"}).copy()

    out = out.sort_values("timestamp_utc")
    return out


def main() -> None:
    if not RAW_DIR.exists():
        die(f"Missing RAW_DIR: {RAW_DIR}")

    run_id = now_ts()

    zips = list_monthly_zips()
    y0, m0 = parse_year_month(zips[0].name)
    y1, m1 = parse_year_month(zips[-1].name)

    print(f"[info] RAW_DIR: {RAW_DIR}")
    print(f"[info] ZIP count: {len(zips)} first={y0}-{m0:02d} last={y1}-{m1:02d}")

    parts = []
    for i, zp in enumerate(zips, start=1):
        y, m = parse_year_month(zp.name)
        if i % 10 == 0 or i == 1 or i == len(zips):
            print(f"[read] {i}/{len(zips)} {zp.name}")
        dfm = read_one_csv_from_zip(zp)
        parts.append(normalize_month(dfm, y, m, run_id=run_id, zip_name=zp.name))

    df = pd.concat(parts, ignore_index=True)
    df = df.sort_values("timestamp_utc")

    # Drop duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["timestamp_utc"], keep="first")
    dropped = before - len(df)
    if dropped:
        print(f"[warn] dropped duplicates: {dropped}")

    if not df["timestamp_utc"].is_monotonic_increasing:
        die("timestamp_utc not monotonic after sort (unexpected).")

    out_name = f"ethusdt_1m_price_{y0}_{y1}_POSTGS_RAWONLY_{run_id}.csv"
    out_path = OUT_DIR / out_name
    df.to_csv(out_path, index=False)

    mf = {
        "utc_written": datetime.utcnow().isoformat(timespec="seconds"),
        "raw_dir": str(RAW_DIR),
        "zip_count": len(zips),
        "first_zip": zips[0].name,
        "last_zip": zips[-1].name,
        "out_csv": str(out_path),
        "rows": int(len(df)),
        "cols": list(df.columns),
        "out_sha256": sha256_file(out_path),
        "log_dir": str(LOG_DIR),
        "notes": "Raw-only normalization; unit auto-detect (s/ms/us); bounds filter; anomalies logged per zip.",
    }
    mf_path = OUT_DIR / f"manifest_ethusdt_1m_POSTGS_RAWONLY_{run_id}.json"
    mf_path.write_text(pd.Series(mf).to_json(indent=2), encoding="utf-8")

    print(f"[ok] Wrote: {out_path}")
    print(f"[ok] rows={len(df)} cols={len(df.columns)}")
    print(f"[ok] manifest: {mf_path}")
    print(f"[ok] anomaly logs (if any): {LOG_DIR}")


if __name__ == "__main__":
    main()


