import argparse
import json
import os
from datetime import datetime
from typing import List

import pandas as pd


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k4_full_csv", required=True)
    ap.add_argument("--top_n", type=int, default=300)
    ap.add_argument("--min_trades_sum", type=int, default=1500)
    ap.add_argument("--require_min_ge", type=float, default=0.0, help="require roi_fee_min >= this")
    ap.add_argument("--out_dir", default="strategies/GS/k5_long")
    args = ap.parse_args()

    df = pd.read_csv(args.k4_full_csv)

    need = ["roi_fee_mean", "trades_sum", "combination"]
    for c in need:
        if c not in df.columns:
            raise RuntimeError(f"Missing column in K4 results: {c}")

    # Identify per-offset roi_fee columns
    roi_cols: List[str] = [c for c in df.columns if c.startswith("roi_fee_off_")]
    if not roi_cols:
        raise RuntimeError("No roi_fee_off_* columns found. Need per-offset roi_fee columns for robustness gate.")

    # Hard gates
    df2 = df[df["trades_sum"] >= int(args.min_trades_sum)].copy()
    df2["roi_fee_min"] = df2[roi_cols].min(axis=1)

    df2 = df2[df2["roi_fee_min"] >= float(args.require_min_ge)].copy()
    if df2.empty:
        raise RuntimeError("No rows left after gates. Consider lowering --min_trades_sum or --require_min_ge.")

    # Primary ranking by roi_fee_mean (conservative)
    df2 = df2.sort_values("roi_fee_mean", ascending=False).head(int(args.top_n)).copy()

    # Output seed format for K5 generator: keep combination JSON, carry meta
    out = pd.DataFrame(
        {
            "k": 5,
            "direction": "long",
            "source": "k5_long_seeds_from_k4_long_top",
            "roi_fee_mean": df2["roi_fee_mean"].astype(float),
            "roi_fee_min": df2["roi_fee_min"].astype(float),
            "trades_sum": df2["trades_sum"].astype(int),
            "combination": df2["combination"].astype(str),
        }
    )

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(
        args.out_dir,
        f"strategies_GS_k5_long_seeds_top{len(out)}_minTrades{int(args.min_trades_sum)}_minRoiMin{args.require_min_ge}_{ts()}.csv",
    )
    out.to_csv(out_path, index=False)

    print("OK WROTE:", out_path)
    print("SEEDS:", len(out))
    print("ROI_FEE_MEAN range:", float(out["roi_fee_mean"].min()), float(out["roi_fee_mean"].max()))
    print("ROI_FEE_MIN range :", float(out["roi_fee_min"].min()), float(out["roi_fee_min"].max()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
