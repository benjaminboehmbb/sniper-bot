#!/usr/bin/env python3
# scripts/generate_GS_k3_short.py
#
# Generate ALL unweighted K3 SHORT seed combinations (Gold-Standard)
# - Signals: fixed global list (12)
# - K=3 combinations, weight=1.0
# - Output: strategies/GS/k3_short/strategies_GS_k3_short_ALL_unweighted_<timestamp>.csv
#
# NO analysis. NO direction applied here. Deterministic.

import os
import csv
from itertools import combinations
from datetime import datetime

# ---- FIXED GLOBAL SIGNAL LIST (authoritative) ----
SIGNALS = [
    "rsi", "macd", "bollinger",
    "ma200", "stoch", "atr", "ema50",
    "adx", "cci", "mfi", "obv", "roc",
]

OUT_DIR = "strategies/GS/k3_short"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    combos = list(combinations(SIGNALS, 3))  # C(12,3) = 220
    assert len(combos) == 220, f"Expected 220 combos, got {len(combos)}"

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(
        OUT_DIR,
        f"strategies_GS_k3_short_ALL_unweighted_{ts}.csv"
    )

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["combination"])
        for c in combos:
            comb = {k: 1.0 for k in c}
            w.writerow([str(comb)])

    print("[ok] Wrote:", out_path)
    print("[ok] Rows:", len(combos))
    print("[ok] Signals per combo: 3")
    print("[ok] Weights: all 1.0")
    print("[ok] Deterministic: YES")

if __name__ == "__main__":
    main()
