import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

ENV_FEE_KEY = "SIMTRADERGS_FEE_ROUNDTRIP"


def repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def import_simtrader_gs():
    rr = repo_root()
    if rr not in sys.path:
        sys.path.insert(0, rr)
    try:
        from engine import simtraderGS  # type: ignore
    except Exception as e:
        raise RuntimeError(f"Failed to import engine/simtraderGS.py: {e}")
    return simtraderGS


class EnvVar:
    def __init__(self, key: str, value: Optional[str]):
        self.key = key
        self.value = value
        self.prev: Optional[str] = None

    def __enter__(self):
        self.prev = os.environ.get(self.key)
        if self.value is None:
            os.environ.pop(self.key, None)
        else:
            os.environ[self.key] = str(self.value)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.prev is None:
            os.environ.pop(self.key, None)
        else:
            os.environ[self.key] = self.prev
        return False


def parse_offsets(s: str) -> List[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def read_window(csv_path: str, offset: int, nrows: int) -> pd.DataFrame:
    need_start = offset
    need_end = offset + nrows
    chunks: List[pd.DataFrame] = []
    seen = 0

    for chunk in pd.read_csv(csv_path, chunksize=200_000):
        clen = len(chunk)
        if seen + clen <= need_start:
            seen += clen
            continue

        start = max(0, need_start - seen)
        end = min(clen, need_end - seen)
        if end > start:
            chunks.append(chunk.iloc[start:end].copy())

        seen += clen
        if seen >= need_end:
            break

    if not chunks:
        return pd.DataFrame()
    return pd.concat(chunks, ignore_index=True)


def apply_gate(df: pd.DataFrame, direction: str, apply_regime_gate: bool, regime_col: Optional[str]) -> pd.DataFrame:
    if not apply_regime_gate or df.empty:
        return df

    if "allow_long" in df.columns and "allow_short" in df.columns:
        if direction == "long":
            return df[df["allow_long"] == 1].copy()
        return df[df["allow_short"] == 1].copy()

    col = regime_col or "regime_v1"
    if col not in df.columns:
        return df

    want = 1 if direction == "long" else -1
    return df[df[col] == want].copy()


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--strategies_csv", required=True, help="generated weight-grid strategies CSV")
    ap.add_argument("--rows", type=int, default=200000)
    ap.add_argument("--offsets", default="0")
    ap.add_argument("--direction", choices=["long", "short"], required=True)
    ap.add_argument("--fee", type=float, default=0.0, help="roi_fee = roi - fee * num_trades")
    ap.add_argument("--apply_regime_gate", action="store_true")
    ap.add_argument("--regime_col", default=None)
    ap.add_argument("--limit", type=int, default=0, help="0 = no limit, else first N strategies (deterministic)")
    args = ap.parse_args()

    if args.direction != "long":
        raise RuntimeError("This analyzer is for K3 LONG weighted runs only.")

    rr = repo_root()
    simtraderGS = import_simtrader_gs()

    offsets = parse_offsets(args.offsets)
    fee = float(args.fee)
    apply_rg = bool(args.apply_regime_gate)
    regime_col = args.regime_col

    out_dir = os.path.join(rr, "results", "GS", "k3_long_weighted")
    os.makedirs(out_dir, exist_ok=True)

    print("REPO_ROOT:", rr)
    print("CSV:", args.csv)
    print("STRATEGIES_CSV:", args.strategies_csv)
    print("ROWS(per window):", int(args.rows))
    print("OFFSETS:", offsets)
    print("DIRECTION:", args.direction)
    print("FEE(roundtrip):", fee)
    print("REGIME_GATE:", "ON" if apply_rg else "OFF", "col=" + (regime_col if regime_col else "(auto)"))
    print("OUT_DIR:", out_dir)
    print("")

    strat = pd.read_csv(args.strategies_csv)

    need_cols = ["combination"]
    for c in need_cols:
        if c not in strat.columns:
            raise RuntimeError(f"Missing required column in strategies_csv: {c}")

    # Deterministic ordering: keep file order (it is deterministic from generator)
    if int(args.limit) > 0:
        strat = strat.head(int(args.limit)).copy()

    total = len(strat)
    if total <= 0:
        raise RuntimeError("No strategies to run (empty after limit).")

    # Preload windows once
    windows: List[Tuple[int, pd.DataFrame]] = []
    for off in offsets:
        dfw = read_window(args.csv, int(off), int(args.rows))
        dfw_g = apply_gate(dfw, args.direction, apply_rg, regime_col)
        windows.append((int(off), dfw_g))
        print(f"WINDOW offset={int(off)} post_rows={len(dfw_g)}")

    print("")
    print("STRATEGIES_RUN:", total)
    print("")

    results: List[Dict[str, Any]] = []

    with EnvVar(ENV_FEE_KEY, "0"):
        for i, row in enumerate(strat.itertuples(index=False), start=1):
            comb_str = getattr(row, "combination")
            comb = json.loads(comb_str)

            roi_fee_list: List[float] = []
            trades_list: List[int] = []
            per_win: Dict[str, Any] = {}

            for off, wdf in windows:
                if wdf.empty:
                    roi_fee = 0.0
                    trades = 0
                    roi = 0.0
                else:
                    res = simtraderGS.evaluate_strategy(wdf, comb, args.direction)
                    roi = float(res.get("roi", 0.0))
                    trades = int(res.get("num_trades", 0))
                    roi_fee = roi - fee * trades

                roi_fee_list.append(roi_fee)
                trades_list.append(trades)
                per_win[f"roi_fee_off_{off}"] = roi_fee
                per_win[f"trades_off_{off}"] = trades
                per_win[f"roi_off_{off}"] = roi

            out: Dict[str, Any] = {
                "engine": "simtraderGS",
                "k": 3,
                "direction": "long",
                "roi_fee_mean": sum(roi_fee_list) / float(len(roi_fee_list)),
                "trades_sum": int(sum(trades_list)),
                "combination": json.dumps(comb, sort_keys=True),
            }

            # carry optional metadata if present
            for meta in ["signals", "w1", "w2", "w3", "seed_roi_fee_mean", "seed_trades_sum", "source"]:
                if hasattr(row, meta):
                    out[meta] = getattr(row, meta)

            out.update(per_win)
            results.append(out)

            if i % 200 == 0 or i == total:
                pct = 100.0 * i / float(total)
                print(f"PROGRESS {i}/{total} ({pct:.1f}%)")

    label = "SMOKE" if int(args.limit) > 0 else "FULL"
    out_name = f"strategy_results_GS_k3_long_WEIGHTED_{label}_{ts()}.csv"
    out_path = os.path.join(out_dir, out_name)
    pd.DataFrame(results).to_csv(out_path, index=False)

    print("")
    print("OK WROTE:", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
