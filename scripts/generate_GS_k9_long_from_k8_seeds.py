#!/usr/bin/env python3
# scripts/generate_GS_k9_long_from_k8_seeds.py
#
# Gold-Standard structure expansion (UNWEIGHTED) for K9 LONG:
# - Reads K9 LONG seeds CSV (Top-250 selected from K8 FULL results)
# - Expands by adding exactly one new signal (weight=1.0) not already present
# - Produces unique K9 candidate combinations (stringified dict in column "combination")
# - Deterministic: stable sorting + canonical formatting + dedup on canonical key
# - Writes timestamped output CSV in strategies/GS/k9_long/
#
# Notes:
# - This is purely candidate generation. No evaluation, no engine.
# - Assumes combination is a stringified dict, e.g. "{'rsi_signal': 0.3, ...}"
# - Output is unweighted structure: existing weights preserved from seeds, new signal added with 1.0.
#   (If seeds are unweighted already, this keeps them unweighted.)

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
    ap = argparse.ArgumentParser(description="Generate GS K9 LONG candidates from K8-selected seeds (unweighted structure expansion).")
    ap.add_argument(
        "--seeds_csv",
        default="strategies/GS/k9_long/strategies_GS_k9_long_seeds_top250_minRoiP25-0.75_2026-01-09_13-29-09.csv",
        help="Input seeds CSV (contains column 'combination')",
    )
    ap.add_argument(
        "--signals",
        default=",".join(DEFAULT_SIGNALS),
        help="Comma-separated list of allowed signal keys",
    )
    ap.add_argument(
        "--out_dir",
        default="strategies/GS/k9_long",
        help="Output directory for generated candidates",
    )
    ap.add_argument(
        "--out_k",
        type=int,
        default=9,
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
        default="k8_seed_expansion_unweighted",
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
    # Accept dict-literal strings only
    d = eval(s, {"__builtins__": {}}, {})
    if not isinstance(d, dict):
        raise ValueError("combination is not a dict literal")
    # normalize keys to str, values to float
    out = {}
    for k, v in d.items():
        out[str(k)] = float(v)
    return out


def canonical_dict_str(d: dict) -> str:
    # Deterministic string form with sorted keys, python-literal dict
    keys = sorted(d.keys())
    parts = []
    for k in keys:
        # keep float formatting stable (repr is ok but can vary); use fixed minimal precision
        val = d[k]
        # trim -0.0
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

    # Build expansions
    out_rows = []
    seen = set()

    # Deterministic seed order:
    # - prefer robust ranking columns if present, else stable file order
    sort_cols = []
    if "roi_fee_p25" in df.columns:
        sort_cols.append("roi_fee_p25")
    if "roi_fee_mean" in df.columns:
        sort_cols.append("roi_fee_mean")
    if sort_cols:
        df_sorted = df.sort_values(by=sort_cols, ascending=[False] * len(sort_cols), kind="mergesort")
    else:
        df_sorted = df

    for _, row in df_sorted.iterrows():
        comb_str = str(row["combination"])
        try:
            base = safe_eval_dict(comb_str)
        except Exception:
            # skip malformed combination
            continue

        base_keys = set(base.keys())
        # Restrict to allowed signals (defensive)
        base_keys_allowed = base_keys.intersection(signal_set)

        # If there are unknown keys, keep them but do not expand with them.
        # Expansion candidates are only within allowed signals.
        missing = [s for s in signals if s not in base_keys_allowed]

        for new_sig in missing:
            d2 = dict(base)
            d2[new_sig] = float(args.new_weight)

            # Canonical + dedup
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
    out_name = f"strategies_GS_k9_long_from_k8_top250_unweighted_{ts}.csv"
    out_path = os.path.join(args.out_dir, out_name)

    out_df.to_csv(out_path, index=False)

    # Summary (ASCII only)
    print("[ok] Seeds:", args.seeds_csv)
    print("[ok] Seeds rows:", len(df))
    print("[ok] Allowed signals:", ",".join(signals))
    print("[ok] Generated candidates:", len(out_df))
    print("[ok] Output:", out_path)


if __name__ == "__main__":
    main()
