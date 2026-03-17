import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def frange_01(start: float, stop: float, step: float) -> List[float]:
    # inclusive grid with stable rounding
    vals = []
    x = start
    while x <= stop + 1e-12:
        vals.append(round(x, 1))
        x += step
    return vals


def parse_signals(s: str) -> Tuple[str, str, str]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) != 3:
        raise ValueError(f"signals must be 3 comma-separated names, got: {s}")
    return parts[0], parts[1], parts[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k3_full_csv", required=True, help="K3 LONG FULL results CSV (GS)")
    ap.add_argument("--top_n", type=int, default=25)
    ap.add_argument("--min_trades_sum", type=int, default=1500, help="filter seeds: trades_sum >= this")
    ap.add_argument("--w_min", type=float, default=0.1)
    ap.add_argument("--w_max", type=float, default=1.0)
    ap.add_argument("--w_step", type=float, default=0.1)
    ap.add_argument("--out_dir", default="strategies/GS/k3_long")
    args = ap.parse_args()

    df = pd.read_csv(args.k3_full_csv)

    # basic sanity
    need_cols = ["roi_fee_mean", "trades_sum", "signals"]
    for c in need_cols:
        if c not in df.columns:
            raise RuntimeError(f"Missing required column in K3 results CSV: {c}")

    # seed filter
    df2 = df[df["trades_sum"] >= int(args.min_trades_sum)].copy()
    if df2.empty:
        raise RuntimeError("No seeds left after min_trades_sum filter. Lower --min_trades_sum.")

    # top seeds by roi_fee_mean
    df2 = df2.sort_values("roi_fee_mean", ascending=False).head(int(args.top_n)).copy()

    wgrid = frange_01(float(args.w_min), float(args.w_max), float(args.w_step))

    rows: List[Dict[str, object]] = []
    for _, r in df2.iterrows():
        s1, s2, s3 = parse_signals(str(r["signals"]))
        base_seed_roi = float(r["roi_fee_mean"])
        base_seed_trades = int(r["trades_sum"])

        for w1 in wgrid:
            for w2 in wgrid:
                for w3 in wgrid:
                    comb = {s1: float(w1), s2: float(w2), s3: float(w3)}
                    rows.append(
                        {
                            "k": 3,
                            "direction": "long",
                            "signals": f"{s1},{s2},{s3}",
                            "w1": float(w1),
                            "w2": float(w2),
                            "w3": float(w3),
                            "combination": json.dumps(comb, sort_keys=True),
                            "seed_roi_fee_mean": base_seed_roi,
                            "seed_trades_sum": base_seed_trades,
                            "source": "k3_long_top_seed_weight_grid",
                        }
                    )

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(
        args.out_dir,
        f"strategies_GS_k3_long_weightgrid_top{int(args.top_n)}_w{args.w_min}-{args.w_max}_step{args.w_step}_{ts()}.csv",
    )
    pd.DataFrame(rows).to_csv(out_path, index=False)

    print("OK WROTE:", out_path)
    print("SEEDS_USED:", len(df2))
    print("WEIGHTS_PER_SIGNAL:", len(wgrid))
    print("TOTAL_ROWS:", len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
