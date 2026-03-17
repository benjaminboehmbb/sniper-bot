import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Set

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
    ap.add_argument("--k4_seeds_csv", required=True)
    ap.add_argument("--out_dir", default="strategies/GS/k5_long")
    args = ap.parse_args()

    df = pd.read_csv(args.k4_seeds_csv)
    if "combination" not in df.columns:
        raise RuntimeError("Seed CSV must contain column 'combination'")

    out_rows: List[Dict[str, object]] = []
    seen: Set[str] = set()

    for r in df.itertuples(index=False):
        comb4 = load_combination(getattr(r, "combination"))
        used = set(comb4.keys())
        remaining = [s for s in ALL_SIGNALS if s not in used]

        for s5 in remaining:
            comb5 = dict(comb4)
            comb5[s5] = 1.0  # unweighted expansion
            key = json.dumps(comb5, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            out_rows.append({
                "k": 5,
                "direction": "long",
                "source": "k5_from_k4_long_top300_unweighted",
                "combination": key
            })

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(
        args.out_dir,
        f"strategies_GS_k5_long_from_k4_top300_unweighted_{ts()}.csv"
    )
    pd.DataFrame(out_rows).to_csv(out_path, index=False)

    print("OK WROTE:", out_path)
    print("K5_ROWS:", len(out_rows))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
