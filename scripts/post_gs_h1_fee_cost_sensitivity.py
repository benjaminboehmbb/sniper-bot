#!/usr/bin/env python3
# scripts/post_gs_h1_fee_cost_sensitivity.py
#
# Post-GS H1 (correct): Fee sensitivity via SIMTRADERGS_FEE_ROUNDTRIP sweep.
# - No GS mutation
# - No writes into results/GS
# - Slippage NOT modeled in GS -> excluded here
#
# Output: results/POST_GS/H1_fee_cost/{long,short,meta}/...

import sys, json, time, glob, hashlib, traceback, ast
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

GS_ENGINE_PATH = REPO_ROOT / "engine" / "simtraderGS.py"
GS_PRICE_CSV = REPO_ROOT / "data" / "btcusdt_1m_2026-01-07" / "simtraderGS" / \
    "btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"

LONG_DIR = REPO_ROOT / "strategies" / "GS" / "LONG_FINAL_CANONICAL"
SHORT_DIR = REPO_ROOT / "strategies" / "GS" / "SHORT_FINAL"

OUT_BASE = REPO_ROOT / "results" / "POST_GS" / "H1_fee_cost"
OUT_LONG = OUT_BASE / "long"
OUT_SHORT = OUT_BASE / "short"
OUT_META = OUT_BASE / "meta"
OUT_LOGS = OUT_BASE / "logs"

# Fee sweep in ROUNDTRIP pct (e.g. 0.0004 = 0.04% roundtrip)
FEE_RT_LIST = [0.0, 0.0001, 0.0002, 0.0004, 0.0006, 0.0010]  # adjust later if needed
MAX_STRATEGIES_PER_SIDE = None  # None=all; or int for smoke
FAIL_FAST = True

def now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def die(msg: str, code: int = 2) -> None:
    print(f"[FATAL] {msg}")
    sys.exit(code)

def assert_no_gs_writes(p: Path) -> None:
    s = str(p.resolve())
    if "/results/GS/" in s or s.endswith("/results/GS") or "/results/GS" in s:
        die(f"Forbidden output path in GS area: {s}")

def ensure_dirs():
    for p in [OUT_LONG, OUT_SHORT, OUT_META, OUT_LOGS]:
        p.mkdir(parents=True, exist_ok=True)
        assert_no_gs_writes(p)

def list_strategy_files(dir_path: Path) -> List[Path]:
    files = sorted([Path(p) for p in glob.glob(str(dir_path / "*")) if Path(p).is_file()])
    csvs = [p for p in files if p.suffix.lower() == ".csv"]
    jsons = [p for p in files if p.suffix.lower() == ".json"]
    chosen = csvs if csvs else jsons
    if not chosen:
        die(f"No .csv/.json strategy files found in: {dir_path}")
    return chosen

def load_strategies(dir_path: Path) -> List[Dict[str, Any]]:
    files = list_strategy_files(dir_path)
    out: List[Dict[str, Any]] = []
    for f in files:
        if f.suffix.lower() == ".csv":
            df = pd.read_csv(f)
            col = None
            for c in ["combination","Combination","strategy","Strategy"]:
                if c in df.columns:
                    col = c
                    break
            if col is None:
                die(f"CSV {f} lacks strategy column. Found: {list(df.columns)}")
            out.extend([{"raw": str(x)} for x in df[col].tolist()])
        else:
            with open(f, "r", encoding="utf-8") as h:
                obj = json.load(h)
            if isinstance(obj, list):
                out.extend(obj)
            elif isinstance(obj, dict) and isinstance(obj.get("strategies"), list):
                out.extend(obj["strategies"])
            else:
                die(f"Unsupported JSON structure in {f}")
    if MAX_STRATEGIES_PER_SIDE is not None:
        out = out[:MAX_STRATEGIES_PER_SIDE]
    return out

def decode_comb(st: Dict[str, Any]) -> Any:
    if "raw" in st and isinstance(st["raw"], str):
        s = st["raw"].strip()
        try:
            obj = ast.literal_eval(s)
            return obj if isinstance(obj, dict) else {"combination": obj}
        except Exception:
            return {"combination_raw": s}
    return st

def preflight_manifest(run_id: str) -> Dict[str, Any]:
    if not GS_ENGINE_PATH.exists(): die(f"Missing: {GS_ENGINE_PATH}")
    if not GS_PRICE_CSV.exists(): die(f"Missing: {GS_PRICE_CSV}")
    if not LONG_DIR.exists(): die(f"Missing: {LONG_DIR}")
    if not SHORT_DIR.exists(): die(f"Missing: {SHORT_DIR}")
    return {
        "run_id": run_id,
        "utc_started": datetime.utcnow().isoformat(timespec="seconds"),
        "repo_root": str(REPO_ROOT),
        "engine_path": str(GS_ENGINE_PATH),
        "engine_sha256": sha256_file(GS_ENGINE_PATH),
        "price_csv_path": str(GS_PRICE_CSV),
        "price_csv_sha256": sha256_file(GS_PRICE_CSV),
        "fee_rt_list": FEE_RT_LIST,
        "max_strategies_per_side": MAX_STRATEGIES_PER_SIDE,
        "python": sys.version,
    }

def run_side(side_name: str, dir_path: Path, out_dir: Path, price_df: pd.DataFrame, run_id: str) -> pd.DataFrame:
    from engine import simtraderGS as gs

    strategies = load_strategies(dir_path)
    if not strategies:
        die(f"No strategies for {side_name}")

    print(f"[info] {side_name}: strategies={len(strategies)} dir={dir_path}")

    rows = []
    for fee_rt in FEE_RT_LIST:
        # set ENV so gs._fee_roundtrip() reads it on each call (GS design)
        import os
        os.environ["SIMTRADERGS_FEE_ROUNDTRIP"] = str(fee_rt)

        for idx, st in enumerate(strategies, start=1):
            comb = decode_comb(st)
            try:
                res = gs.evaluate_strategy(price_df=price_df, comb=comb, direction=side_name.lower())
                row = {
                    "run_id": run_id,
                    "side": side_name,
                    "fee_roundtrip_pct": fee_rt,
                    "status": "OK",
                }
                if isinstance(res, dict):
                    for k in ["roi","winrate","num_trades","sharpe","profit_factor","max_dd"]:
                        if k in res:
                            row[k] = res[k]
                else:
                    row["result"] = str(res)
                rows.append(row)
            except Exception as e:
                rows.append({
                    "run_id": run_id,
                    "side": side_name,
                    "fee_roundtrip_pct": fee_rt,
                    "status": "ERR",
                    "error": str(e)[:500],
                })
                if FAIL_FAST:
                    raise

    df = pd.DataFrame(rows)
    out_path = out_dir / f"strategy_results_POST_GS_H1_{side_name}_FEE_SWEEP_{run_id}.csv"
    assert_no_gs_writes(out_path)
    df.to_csv(out_path, index=False)
    print(f"[ok] Wrote: {out_path} rows={len(df)}")
    return df

def main():
    run_id = now_ts()
    ensure_dirs()

    manifest = preflight_manifest(run_id)
    mf_path = OUT_META / f"run_manifest_POST_GS_H1_{run_id}.json"
    assert_no_gs_writes(mf_path)
    with open(mf_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    print(f"[ok] Wrote manifest: {mf_path}")

    print(f"[load] price CSV: {GS_PRICE_CSV}")
    price_df = pd.read_csv(GS_PRICE_CSV)
    print(f"[ok] price rows={len(price_df)} cols={len(price_df.columns)}")

    try:
        run_side("LONG", LONG_DIR, OUT_LONG, price_df, run_id)
        run_side("SHORT", SHORT_DIR, OUT_SHORT, price_df, run_id)
    except Exception as e:
        log_path = OUT_LOGS / f"error_POST_GS_H1_{run_id}.txt"
        assert_no_gs_writes(log_path)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("ERROR\n")
            f.write(str(e) + "\n\n")
            f.write(traceback.format_exc())
        print(f"[fatal] Exception occurred. Details: {log_path}")
        raise

    print("[done] Post-GS H1 completed.")
    print(f"[out] {OUT_BASE}")

if __name__ == "__main__":
    main()



