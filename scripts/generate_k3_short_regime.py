#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate K3 (3-of-12) short strategies with weights 0.1..1.0 (step=0.1).
Keys are WITHOUT '_signal' suffix (SimTrader maps them).
Output CSV has a single column 'Combination' (JSON dict per row).
Filename includes UTC timestamp.

Signals (12): rsi, macd, bollinger, ma200, stoch, atr, ema50, adx, cci, mfi, obv, roc
Expected count: C(12,3)=220 triples * 10^3 weights = 220,000 strategies.
"""

import argparse
import csv
import itertools as it
import json
from datetime import datetime, timezone
from pathlib import Path

SIGNALS = [
    "rsi", "macd", "bollinger", "ma200", "stoch", "atr",
    "ema50", "adx", "cci", "mfi", "obv", "roc"
]

def frange(start: float, stop: float, step: float):
    x = start
    while x <= stop + 1e-12:
        # round to avoid 0.30000000004 artifacts
        yield round(x, 10)
        x += step

def main():
    ap = argparse.ArgumentParser(description="Generate K3 short strategies (3-of-12) with weights.")
    ap.add_argument("--outdir", default="data", help="Output directory (default: data)")
    ap.add_argument("--wmin", type=float, default=0.1, help="Min weight (default: 0.1)")
    ap.add_argument("--wmax", type=float, default=1.0, help="Max weight (default: 1.0)")
    ap.add_argument("--wstep", type=float, default=0.1, help="Weight step (default: 0.1)")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    outpath = outdir / f"strategies_k3_short_regime_12sig_{ts}.csv"

    weights = list(frange(args.wmin, args.wmax, args.wstep))   # 0.1..1.0
    triples = list(it.combinations(SIGNALS, 3))                # C(12,3)=220

    total_rows = 0
    with outpath.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Combination"])
        for s1, s2, s3 in triples:
            for w1, w2, w3 in it.product(weights, repeat=3):
                combo = {s1: float(w1), s2: float(w2), s3: float(w3)}
                writer.writerow([json.dumps(combo, separators=(",", ":"))])
                total_rows += 1

    print(f"[INFO] Wrote {total_rows} strategies to {outpath}")

if __name__ == "__main__":
    main()

