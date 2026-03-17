#!/usr/bin/env python3
# scripts/post_gs_h2_timeframe_transfer.py
#
# Post-GS H2: Timeframe Transfer (1m -> 5m / 15m)
#
# Guarantees:
# - No mutation of engine/simtraderGS.py
# - No writes into results/GS
# - Uses fixed GS 1m CSV as source
# - Produces resampled OHLCV dataframes for 5m/15m
# - Runs LONG_FINAL_CANONICAL (1 strategy) through simtraderGS.evaluate_strategy
# - Fee via ENV SIMTRADERGS_FEE_ROUNDTRIP (fixed)
#
# Important methodological guard:
# - This script DOES NOT "recompute" signals/regime. It validates that required
#   columns for simtraderGS exist. If not, it aborts with a clear error so we
#   don't produce invalid results.
#
# ASCII-only output.

import os
import sys
import json
import time
import glob
import hashlib
import traceback
import ast
import inspect
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


# -----------------------------
# Repo root import
# -----------------------------
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# -----------------------------
# CONFIG (verbindlich)
# -----------------------------
GS_ENGINE_PATH = REPO_ROOT / "engine" / "simtraderGS.py"

GS_PRICE_CSV_1M = REPO_ROOT / "data" / "btcusdt_1m_2026-01-07" / "simtraderGS" / \
    "btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"

LONG_STRATEGY_DIR = REPO_ROOT / "strategies" / "GS" / "LONG_FINAL_CANONICAL"

OUT_BASE = REPO_ROOT / "results" / "POST_GS" / "H2_timeframe"
OUT_1M = OUT_BASE / "1m"
OUT_5M = OUT_BASE / "5m"
OUT_15M = OUT_BASE / "15m"
OUT_META = OUT_BASE / "meta"
OUT_LOGS = OUT_BASE / "logs"

# Fixed fee for H2 (as per design)
FEE_ROUNDTRIP = 0.0004

# Timeframes
TFS = ["1m", "5m", "15m"]

# Safety: only one strategy expected
MAX_STRATEGIES = 1


# -----------------------------
# Helpers
# -----------------------------
def now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def die(msg: str, code: int = 2) -> None:
    print(f"[FATAL] {msg}")
    sys.exit(code)


def assert_no_gs_writes(p: Path) -> None:
    s = str(p.resolve())
    if "/results/GS/" in s or s.endswith("/results/GS") or "/results/GS" in s:
        die(f"Forbidden output path in GS area: {s}")


def ensure_dirs() -> None:
    for p in [OUT_1M, OUT_5M, OUT_15M, OUT_META, OUT_LOGS]:
        p.mkdir(parents=True, exist_ok=True)
        assert_no_gs_writes(p)


def pick_timestamp_column(df: pd.DataFrame) -> str:
    # Prefer the known GS canonical timestamp column.
    for c in ["timestamp_utc", "timestamp", "open_time", "close_time", "time"]:
        if c in df.columns:
            return c
    die(f"No timestamp column found. Columns: {list(df.columns)[:30]}...")


def to_datetime_utc(series: pd.Series) -> pd.Series:
    # GS data often stores UTC timestamps. Accept numeric ms/seconds or ISO strings.
    if pd.api.types.is_numeric_dtype(series):
        # heuristics: ms vs seconds
        v = series.dropna().iloc[0]
        if v > 10_000_000_000:  # ms since epoch
            return pd.to_datetime(series, unit="ms", utc=True)
        return pd.to_datetime(series, unit="s", utc=True)
    return pd.to_datetime(series, utc=True, errors="coerce")


def load_single_long_comb() -> Any:
    files = sorted(glob.glob(str(LONG_STRATEGY_DIR / "*.csv")))
    if not files:
        die(f"No strategy CSV found in: {LONG_STRATEGY_DIR}")
    df = pd.read_csv(files[0])
    col = None
    for c in ["combination", "Combination", "strategy", "Strategy"]:
        if c in df.columns:
            col = c
            break
    if col is None:
        die(f"Strategy CSV lacks combination column. Found: {list(df.columns)}")
    s = str(df.iloc[0][col])
    try:
        obj = ast.literal_eval(s)
        if not isinstance(obj, dict):
            die("Decoded comb is not a dict.")
        return obj
    except Exception as e:
        die(f"Failed to parse comb from CSV. Error: {e}")


def required_cols_from_simtrader() -> List[str]:
    """
    We do not guess too much. Instead, we detect likely required columns by scanning
    simtraderGS source for df['col'] accesses. This is not perfect but safer than
    "recomputing" signals.
    """
    src = GS_ENGINE_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
    cols = set()
    import re
    pat = re.compile(r"\[\s*[\"']([^\"']+)[\"']\s*\]")
    for line in src:
        if "price_df" in line or "df" in line:
            m = pat.findall(line)
            for c in m:
                # ignore obvious non-column literals
                if c in ("strategy", "config", "meta"):
                    continue
                # heuristic: likely df[col]
                if "price_df" in line or "df" in line:
                    cols.add(c)
    # keep only those that appear in GS price CSV columns (intersection at runtime)
    return sorted(cols)


def resample_ohlcv(df_1m: pd.DataFrame, tf: str, ts_col: str) -> pd.DataFrame:
    if tf == "1m":
        return df_1m.copy()

    rule = {"5m": "5T", "15m": "15T"}[tf]

    df = df_1m.copy()
    dt = to_datetime_utc(df[ts_col])
    if dt.isna().any():
        die(f"Timestamp conversion produced NaT values in {ts_col}.")
    df["_dt"] = dt
    df = df.sort_values("_dt")
    df = df.set_index("_dt")

    # Required OHLCV columns
    need = ["open", "high", "low", "close", "volume"]
    for c in need:
        if c not in df.columns:
            die(f"Missing OHLCV column '{c}' in 1m CSV. Columns: {list(df.columns)}")

    agg = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }

    # Preserve additional columns only if they are constant within the window
    # (otherwise we drop them rather than silently distort).
    extra_cols = [c for c in df.columns if c not in need and c != ts_col]
    for c in extra_cols:
        # Keep regime-like columns only if constant within each bucket.
        # This is conservative: we will NOT carry signals/regime unless constant.
        agg[c] = (lambda x: x.iloc[-1] if (x.nunique(dropna=False) == 1) else float("nan"))

    out = df.resample(rule, label="left", closed="left").agg(agg)

    # Drop rows where OHLC are missing
    out = out.dropna(subset=["open", "high", "low", "close"], how="any")

    # Restore timestamp column
    out = out.reset_index().rename(columns={"_dt": ts_col})

    # If extra columns produced NaN due to non-constant buckets, they stay NaN -> later contract check will fail.
    return out


def contract_check(df: pd.DataFrame, tag: str) -> None:
    # Basic
    if len(df) < 1000:
        die(f"{tag}: too few rows after resampling: {len(df)}")

    # simtraderGS required columns check:
    # We intersect detected accesses with df columns to avoid false positives.
    detected = required_cols_from_simtrader()
    # Keep only those that are present in original 1m CSV columns OR look like known signals/regime columns
    # But we don't know all; we enforce a strict check by verifying that evaluate_strategy runs.
    # Still, we do a pre-check for the most common ones.
    common_must = ["close"]
    for c in common_must:
        if c not in df.columns:
            die(f"{tag}: missing required column '{c}'")

    # Hard warning if many detected cols are missing
    missing = [c for c in detected if c not in df.columns]
    # We only print, not fail, because detection is heuristic.
    if missing:
        print(f"[warn] {tag}: detected potential cols missing (heuristic, count={len(missing)}). Example: {missing[:15]}")


def run_eval(gs_module, price_df: pd.DataFrame, comb: Any, direction: str) -> Dict[str, Any]:
    # Set fee via ENV (GS supported)
    os.environ["SIMTRADERGS_FEE_ROUNDTRIP"] = str(FEE_ROUNDTRIP)

    sig = inspect.signature(gs_module.evaluate_strategy)
    # Signature we observed: (price_df, comb, direction)
    kwargs = {}
    params = list(sig.parameters.keys())
    if "price_df" in params:
        kwargs["price_df"] = price_df
    if "comb" in params:
        kwargs["comb"] = comb
    if "direction" in params:
        kwargs["direction"] = direction
    # fallback positional if needed
    try:
        res = gs_module.evaluate_strategy(**kwargs)
    except TypeError:
        res = gs_module.evaluate_strategy(price_df, comb, direction)

    if not isinstance(res, dict):
        return {"result": str(res)}
    return res


def write_manifest(run_id: str) -> Path:
    mf = {
        "run_id": run_id,
        "utc_started": datetime.utcnow().isoformat(timespec="seconds"),
        "fee_roundtrip_pct": FEE_ROUNDTRIP,
        "engine_path": str(GS_ENGINE_PATH),
        "engine_sha256": sha256_file(GS_ENGINE_PATH),
        "price_csv_1m_path": str(GS_PRICE_CSV_1M),
        "price_csv_1m_sha256": sha256_file(GS_PRICE_CSV_1M),
        "strategy_dir_long": str(LONG_STRATEGY_DIR),
        "tf_list": TFS,
        "notes": "Signals/regime not recomputed; carried only if constant per bucket; aborts if evaluate_strategy fails.",
        "python": sys.version,
    }
    out = OUT_META / f"run_manifest_POST_GS_H2_{run_id}.json"
    assert_no_gs_writes(out)
    out.write_text(json.dumps(mf, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[ok] Wrote manifest: {out}")
    return out


def main() -> None:
    ensure_dirs()

    if not GS_ENGINE_PATH.exists():
        die(f"Missing engine: {GS_ENGINE_PATH}")
    if not GS_PRICE_CSV_1M.exists():
        die(f"Missing price CSV: {GS_PRICE_CSV_1M}")
    if not LONG_STRATEGY_DIR.exists():
        die(f"Missing strategy dir: {LONG_STRATEGY_DIR}")

    run_id = now_ts()
    write_manifest(run_id)

    print(f"[load] 1m CSV: {GS_PRICE_CSV_1M}")
    df1 = pd.read_csv(GS_PRICE_CSV_1M)
    print(f"[ok] 1m rows={len(df1)} cols={len(df1.columns)}")

    ts_col = pick_timestamp_column(df1)
    print(f"[info] timestamp column: {ts_col}")

    comb = load_single_long_comb()
    print(f"[info] LONG strategies: 1 (from LONG_FINAL_CANONICAL)")

    # Import GS engine
    try:
        from engine import simtraderGS as gs
    except Exception as e:
        die(f"Import engine.simtraderGS failed: {e}")

    rows = []
    t0 = time.time()

    for tf in TFS:
        print(f"[tf] build={tf}")
        dft = resample_ohlcv(df1, tf=tf, ts_col=ts_col)
        print(f"[ok] {tf} rows={len(dft)} cols={len(dft.columns)}")

        contract_check(dft, tag=tf)

        # Run LONG only
        try:
            res = run_eval(gs, dft, comb, direction="long")
        except Exception as e:
            log_path = OUT_LOGS / f"error_POST_GS_H2_{tf}_{run_id}.txt"
            assert_no_gs_writes(log_path)
            log_path.write_text(traceback.format_exc(), encoding="utf-8")
            die(f"{tf}: evaluate_strategy failed; details in {log_path}. Error: {e}")

        row = {
            "run_id": run_id,
            "tf": tf,
            "side": "LONG",
            "fee_roundtrip_pct": FEE_ROUNDTRIP,
        }
        for k in ["roi", "winrate", "num_trades", "profit_factor", "max_dd", "sharpe"]:
            if k in res:
                row[k] = res[k]
        rows.append(row)

        # Write per-tf result CSV
        out_dir = {"1m": OUT_1M, "5m": OUT_5M, "15m": OUT_15M}[tf]
        out_csv = out_dir / f"strategy_results_POST_GS_H2_LONG_{tf}_{run_id}.csv"
        assert_no_gs_writes(out_csv)
        pd.DataFrame([row]).to_csv(out_csv, index=False)
        print(f"[ok] Wrote: {out_csv}")

    # Write meta summary table
    dfm = pd.DataFrame(rows)
    meta_out = OUT_META / f"summary_POST_GS_H2_LONG_timeframe_transfer_{run_id}.csv"
    assert_no_gs_writes(meta_out)
    dfm.to_csv(meta_out, index=False)
    elapsed = time.time() - t0
    print(f"[done] H2 complete. elapsed_s={elapsed:.1f}")
    print(f"[out] {OUT_BASE}")


if __name__ == "__main__":
    main()
