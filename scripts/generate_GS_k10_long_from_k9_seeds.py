#!/usr/bin/env python3
# scripts/generate_GS_k10_long_from_k9_seeds.py
#
# Gold-Standard structure expansion (UNWEIGHTED) for K10 LONG:
# - Reads K10 LONG seeds CSV (Top-250 selected from K9 FULL results)
# - Expands by adding exactly one new signal (weight=1.0) not already present
# - Produces unique K10 candidate combinations (stringified dict in column "combination")
# - Deterministic: stable sorting + canonical formatting + dedup on canonical key
# - Writes timestamped output CSV in strategies/GS/k10_long/
#
# Candidate-generation only (no evaluation, no engine).

import argparse
import os
from datetime import datetime
import pandas as pd


DEFAULT_SIGNALS = [
    "rsi_signal",
    "macd_signal",
    "bollinger_signal",
    "ma200_signal",
    "stoch_signal",
    "atr_signal",
    "ema50_signal",
]


def parse_args():
    ap = argparse.ArgumentParser(
        description="Generate GS K10 LONG candidates from K9-selected seeds (unweighted structure expansion)."
    )
    ap.add_argument(
        "--seeds_csv",
        default="strategies/GS/k10_long/strategies_GS_k10_long_seeds_top250_minRoiP25-2.60_2026-01-09_14-33-41.csv",
        help="Input seeds CSV (contains column 'combination')",
    )
    ap.add_argument(
        "--signals",
        default=",".join(DEFAULT_SIGNALS),
        help="Comma-separated list of allowed signal keys",
    )
    ap.add_argument(
        "--out_dir",
        default="strategies/GS/k10_long",
        help="Output directory for generated candidates",
    )
    ap.add_argument(
        "--out_k",
        type=int,
        default=10,
        help="K value to write into output column 'k'",
    )
    ap.add_argument(
        "--direction",
        default="long",
        choices=["long", "short"],
        help="Direction to write into output column 'direction'",
    )
    ap.add_argument(
        "--source",
        default="k9_seed_expansion_unweighted",
        help="Value for output column 'source'",
    )
    ap.add_argument(
        "--new_weight",
        type=float,
        default=1.0,
        help="Weight to assign to the newly added signal (default 1.0)",
    )
    return ap.parse_args()


def safe_eval_dict(s: str) -> dict:
    d = eval(s, {"__builtins__": {}}, {})
    if not isinstance(d, dict):
        raise ValueError("combination is not a dict literal")
    out = {}
    for k, v in d.items():
        out[str(k)] = float(v)
    return out


def canonical_dict_str(d: dict) -> str:
    keys = sorted(d.keys())
    parts = []
    for k in keys:
        val = float(d[k])
        if abs(val) < 1e-12:
            val = 0.0
        parts.append(f"'{k}': {val:.10g}")
    return "{" + ", ".join(parts) + "}"


def main():
    args = parse_args()
    signals = [s.strip() for s in args.signals.split(",") if s.strip()]
    signal_set = set(signals)

    if not os.path.exists(args.seeds_csv):
        raise SystemExit(f"[fatal] Seeds file not found: {args.seeds_csv}")

    df = pd.read_csv(args.seeds_csv)
    if "combination" not in df.columns:
        raise SystemExit("[fatal] Seeds CSV must contain column 'combination'")

    # Deterministic seed order:
    # prefer robust ranking columns if present
    sort_cols = []
    if "roi_fee_p25" in df.columns:
        sort_cols.append("roi_fee_p25")
    if "roi_fee_mean" in df.columns:
        sort_cols.append("roi_fee_mean")
    if sort_cols:
        df_sorted = df.sort_values(by=sort_cols, ascending=[False] * len(sort_cols), kind="mergesort")
    else:
        df_sorted = df

    out_rows = []
    seen = set()

    for _, row in df_sorted.iterrows():
        comb_str = str(row["combination"])
        try:
            base = safe_eval_dict(comb_str)
        except Exception:
            continue

        base_keys = set(base.keys())
        base_keys_allowed = base_keys.intersection(signal_set)
        missing = [s for s in signals if s not in base_keys_allowed]

        for new_sig in missing:
            d2 = dict(base)
            d2[new_sig] = float(args.new_weight)

            cstr = canonical_dict_str(d2)
            if cstr in seen:
                continue
            seen.add(cstr)

            out_rows.append(
                {
                    "k": args.out_k,
                    "direction": args.direction,
                    "source": args.source,
                    "signals_key": "+".join(sorted(d2.keys())),
                    "combination": cstr,
                }
            )

    out_df = pd.DataFrame(out_rows)

    os.makedirs(args.out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_name = f"strategies_GS_k10_long_from_k9_top250_unweighted_{ts}.csv"
    out_path = os.path.join(args.out_dir, out_name)

    out_df.to_csv(out_path, index=False)

    print("[ok] Seeds:", args.seeds_csv)
    print("[ok] Seeds rows:", len(df))
    print("[ok] Allowed signals:", ",".join(signals))
    print("[ok] Generated candidates:", len(out_df))
    print("[ok] Output:", out_path)


if __name__ == "__main__":
    main()
