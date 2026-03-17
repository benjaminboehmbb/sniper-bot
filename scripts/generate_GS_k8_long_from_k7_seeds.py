#!/usr/bin/env python3
# scripts/generate_GS_k8_long_from_k7_seeds.py
#
# Input: K8 LONG seeds derived from K7 LONG results (contains 'combination' JSON).
# Output: K8 LONG candidate strategies (unweighted expansion): add 1 missing signal with weight 1.0.
# Dedup globally via sorted JSON key.

from __future__ import annotations

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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k8_seeds_csv", required=True)
    ap.add_argument("--out_dir", default="strategies/GS/k8_long")
    args = ap.parse_args()

    df = pd.read_csv(args.k8_seeds_csv)
    if "combination" not in df.columns:
        raise RuntimeError("Seed CSV must contain column 'combination'")

    out_rows: List[Dict[str, object]] = []
    seen: Set[str] = set()

    for r in df.itertuples(index=False):
        comb7 = json.loads(getattr(r, "combination"))
        used = set(comb7.keys())
        remaining = [s for s in ALL_SIGNALS if s not in used]

        for s8 in remaining:
            comb8 = dict(comb7)
            comb8[s8] = 1.0  # unweighted structure expansion
            key = json.dumps(comb8, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            out_rows.append(
                {
                    "k": 8,
                    "direction": "long",
                    "source": "k8_from_k7_long_top250_unweighted",
                    "combination": key,
                }
            )

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(
        args.out_dir,
        f"strategies_GS_k8_long_from_k7_top250_unweighted_{ts()}.csv"
    )
    pd.DataFrame(out_rows).to_csv(out_path, index=False)

    print("OK WROTE:", out_path)
    print("K8_ROWS:", len(out_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
