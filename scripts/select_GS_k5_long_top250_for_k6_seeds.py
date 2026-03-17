import argparse
import os
from datetime import datetime
from typing import List

import pandas as pd


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k5_full_csv", required=True)
    ap.add_argument("--top_n", type=int, default=250)
    ap.add_argument("--require_min_ge", type=float, default=-0.35)
    ap.add_argument("--out_dir", default="strategies/GS/k6_long")
    args = ap.parse_args()

    df = pd.read_csv(args.k5_full_csv)

    need = ["roi_fee_mean", "trades_sum", "combination"]
    for c in need:
        if c not in df.columns:
            raise RuntimeError(f"Missing column in K5 results: {c}")

    roi_cols: List[str] = [c for c in df.columns if c.startswith("roi_fee_off_")]
    if not roi_cols:
        raise RuntimeError("No roi_fee_off_* columns found (need per-offset ROI for robustness gate).")

    df["roi_fee_min"] = df[roi_cols].min(axis=1)

    # Robustness gate
    df2 = df[df["roi_fee_min"] >= float(args.require_min_ge)].copy()
    if df2.empty:
        raise RuntimeError("No rows left after roi_fee_min gate. Lower --require_min_ge.")

    # Select top-N by mean
    df2 = df2.sort_values("roi_fee_mean", ascending=False).head(int(args.top_n)).copy()

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(
        args.out_dir,
        f"strategies_GS_k6_long_seeds_top{len(df2)}_minRoiMin{args.require_min_ge}_{ts()}.csv",
    )

    out = pd.DataFrame(
        {
            "k": 6,
            "direction": "long",
            "source": "k6_long_seeds_from_k5_long_top",
            "roi_fee_mean": df2["roi_fee_mean"].astype(float),
            "roi_fee_min": df2["roi_fee_min"].astype(float),
            "trades_sum": df2["trades_sum"].astype(int),
            "combination": df2["combination"].astype(str),
        }
    )
    out.to_csv(out_path, index=False)

    print("OK WROTE:", out_path)
    print("SEEDS:", len(out))
    print("ROI_FEE_MEAN range:", float(out["roi_fee_mean"].min()), float(out["roi_fee_mean"].max()))
    print("ROI_FEE_MIN range :", float(out["roi_fee_min"].min()), float(out["roi_fee_min"].max()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
