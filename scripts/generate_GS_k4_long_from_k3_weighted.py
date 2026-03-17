import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Set, Tuple

import pandas as pd


ALL_SIGNALS = [
    "adx", "atr", "bollinger", "cci", "ema50", "ma200",
    "macd", "mfi", "obv", "roc", "rsi", "stoch"
]


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def load_combination(s: str) -> Dict[str, float]:
    return json.loads(s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k3_weighted_full_csv", required=True)
    ap.add_argument("--top_n", type=int, default=1000)
    ap.add_argument("--min_trades_sum", type=int, default=1500)
    ap.add_argument("--min_roi_fee_mean", type=float, default=None)
    ap.add_argument("--out_dir", default="strategies/GS/k4_long")
    args = ap.parse_args()

    df = pd.read_csv(args.k3_weighted_full_csv)

    need = ["roi_fee_mean", "trades_sum", "combination"]
    for c in need:
        if c not in df.columns:
            raise RuntimeError(f"Missing column in K3 weighted results: {c}")

    # Hard quality gates
    df2 = df[df["trades_sum"] >= int(args.min_trades_sum)].copy()
    if args.min_roi_fee_mean is not None:
        df2 = df2[df2["roi_fee_mean"] >= float(args.min_roi_fee_mean)].copy()

    if df2.empty:
        raise RuntimeError("No rows left after gates. Lower thresholds.")

    # Top-N by roi_fee_mean
    df2 = df2.sort_values("roi_fee_mean", ascending=False).head(int(args.top_n)).copy()

    out_rows: List[Dict[str, object]] = []
    seen: Set[str] = set()

    for r in df2.itertuples(index=False):
        comb3 = load_combination(getattr(r, "combination"))  # {sig: weight}
        used = set(comb3.keys())
        remaining = [s for s in ALL_SIGNALS if s not in used]

        # expand with one additional signal at weight 1.0
        for s4 in remaining:
            comb4 = dict(comb3)
            comb4[s4] = 1.0

            comb4_json = json.dumps(comb4, sort_keys=True)
            if comb4_json in seen:
                continue
            seen.add(comb4_json)

            out_rows.append(
                {
                    "k": 4,
                    "direction": "long",
                    "source": "k4_from_k3_weighted_top",
                    "seed_roi_fee_mean": float(getattr(r, "roi_fee_mean")),
                    "seed_trades_sum": int(getattr(r, "trades_sum")),
                    "combination": comb4_json,
                }
            )

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(
        args.out_dir,
        f"strategies_GS_k4_long_from_k3weighted_top{len(df2)}_2026-01-09_{ts()}.csv",
    )
    pd.DataFrame(out_rows).to_csv(out_path, index=False)

    print("OK WROTE:", out_path)
    print("SEEDS_USED:", len(df2))
    print("K4_ROWS:", len(out_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
