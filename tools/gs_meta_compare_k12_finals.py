#!/usr/bin/env python3
# tools/gs_meta_compare_k12_finals.py
#
# Read-only meta comparison:
#   - LONG K12 FINAL CANONICAL (strategy file, N=1) vs SHORT K12 FINAL (strategy file, N=1)
#   - Uses canonical RESULTS files for both sides (auto-detect newest) if present.
#
# Writes:
#   results/GS/meta/
#     meta_compare_GS_k12_LONG_CANONICAL_vs_SHORT_FINAL_<ts>.csv
#     meta_compare_GS_k12_LONG_CANONICAL_vs_SHORT_FINAL_<ts>.md
#
# No FINAL artifacts are modified. ASCII-only logs.

import os
from datetime import datetime
import glob
import pandas as pd


# -----------------------------
# CONFIG (edit only if your paths differ)
# -----------------------------
META_OUT_DIR = "results/GS/meta"

# Strategy (comb) files
LONG_STRAT = "strategies/GS/LONG_FINAL_CANONICAL/strategies_GS_k12_long_FINAL_CANONICAL_2026-01-10_08-35-40.csv"
SHORT_STRAT = "strategies/GS/SHORT_FINAL/strategies_GS_k12_short_FINAL_2026-01-09_18-32-16.csv"

# Canonical results directories (auto-detect newest file)
LONG_RESULTS_DIR = "results/GS/k12_long"
SHORT_RESULTS_DIR = "results/GS/k12_short"

# File name patterns
LONG_RESULTS_GLOB = "strategy_results_GS_k12_long_FULL_CANONICAL_*.csv"
SHORT_RESULTS_GLOB = "strategy_results_GS_k12_short_FULL_CANONICAL_*.csv"

# GS constants (for labeling)
ROWS = 200000
OFFSETS = [0, 500000, 1000000, 1500000]
FEE = 0.0004


# -----------------------------
# Helpers
# -----------------------------
def safe_read_csv(path: str):
    if not path:
        return None
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)


def find_newest_csv(directory: str, pattern: str):
    if not directory or not pattern:
        return ""
    paths = glob.glob(os.path.join(directory, pattern))
    if not paths:
        return ""
    # newest by mtime
    paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return paths[0]


def safe_eval_dict(s: str) -> dict:
    d = eval(s, {"__builtins__": {}}, {})
    if not isinstance(d, dict):
        raise ValueError("combination is not a dict")
    out = {}
    for k, v in d.items():
        out[str(k)] = float(v)
    return out


def comb_signature_from_df(df: pd.DataFrame):
    """
    Returns (signals_key, canonical_comb_str, n_keys)
    """
    if df is None or len(df) == 0:
        return ("", "", 0)

    keys = []
    comb_str = ""
    if "combination" in df.columns:
        comb_raw = str(df.iloc[0]["combination"])
        comb = safe_eval_dict(comb_raw)
        keys = sorted(comb.keys())
        comb_str = "{" + ", ".join(f"'{k}': {float(comb[k]):g}" for k in keys) + "}"
        n_keys = len(keys)
    else:
        n_keys = 0

    if "signals_key" in df.columns:
        sk = str(df.iloc[0]["signals_key"])
    else:
        sk = "+".join(keys) if n_keys > 0 else ""

    return (sk, comb_str, n_keys)


def pick_results_fields(df: pd.DataFrame, prefix: str) -> dict:
    """
    Extract a stable subset of results fields if present.
    """
    out = {}
    if df is None or len(df) == 0:
        return out

    row = df.iloc[0]

    # Normalize trade field name
    if "num_trades_sum" in df.columns:
        out[prefix + "trades_sum"] = int(row["num_trades_sum"])
    elif "trades_sum" in df.columns:
        out[prefix + "trades_sum"] = int(row["trades_sum"])

    for col in ["roi_mean", "roi_fee_mean", "roi_fee_p25"]:
        if col in df.columns:
            out[prefix + col] = float(row[col])

    for off in OFFSETS:
        c_fee = f"roi_fee_off_{off}"
        c_roi = f"roi_off_{off}"
        if c_fee in df.columns:
            out[prefix + c_fee] = float(row[c_fee])
        if c_roi in df.columns:
            out[prefix + c_roi] = float(row[c_roi])

        # trades per offset
        t1 = f"num_trades_off_{off}"
        t2 = f"trades_off_{off}"
        if t1 in df.columns:
            out[prefix + f"trades_off_{off}"] = int(row[t1])
        elif t2 in df.columns:
            out[prefix + f"trades_off_{off}"] = int(row[t2])

        # optional extras
        for extra in ["winrate", "sharpe", "pnl_sum", "avg_trade"]:
            ec = f"{extra}_off_{off}"
            if ec in df.columns:
                out[prefix + ec] = float(row[ec])

    return out


def write_md(path: str, lines):
    with open(path, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(str(ln).rstrip() + "\n")


# -----------------------------
# Main
# -----------------------------
def main():
    os.makedirs(META_OUT_DIR, exist_ok=True)

    # Load strategy files
    df_long_s = safe_read_csv(LONG_STRAT)
    df_short_s = safe_read_csv(SHORT_STRAT)
    if df_long_s is None:
        raise SystemExit(f"[fatal] missing LONG_STRAT: {LONG_STRAT}")
    if df_short_s is None:
        raise SystemExit(f"[fatal] missing SHORT_STRAT: {SHORT_STRAT}")

    long_sk, long_comb_str, long_n = comb_signature_from_df(df_long_s)
    short_sk, short_comb_str, short_n = comb_signature_from_df(df_short_s)

    # Auto-detect newest canonical results
    long_results_path = find_newest_csv(LONG_RESULTS_DIR, LONG_RESULTS_GLOB)
    short_results_path = find_newest_csv(SHORT_RESULTS_DIR, SHORT_RESULTS_GLOB)

    df_long_r = safe_read_csv(long_results_path)
    df_short_r = safe_read_csv(short_results_path)

    # Build one-row comparison table
    row = {
        "gs_rows": ROWS,
        "gs_offsets": ",".join(str(x) for x in OFFSETS),
        "gs_fee_roundtrip": FEE,

        "long_strat_path": LONG_STRAT,
        "short_strat_path": SHORT_STRAT,

        "long_signals_key": long_sk,
        "short_signals_key": short_sk,
        "long_num_keys": long_n,
        "short_num_keys": short_n,
        "signals_key_match": (long_sk == short_sk and long_sk != ""),
        "num_keys_match": (long_n == short_n and long_n > 0),

        "long_combination": long_comb_str,
        "short_combination": short_comb_str,
        "combination_match_exact": (long_comb_str == short_comb_str and long_comb_str != ""),

        "long_results_path": long_results_path if df_long_r is not None else "",
        "short_results_path": short_results_path if df_short_r is not None else "",
    }

    row.update(pick_results_fields(df_long_r, "long_"))
    row.update(pick_results_fields(df_short_r, "short_"))

    # Derived deltas if both sides available
    if "long_roi_fee_p25" in row and "short_roi_fee_p25" in row:
        row["delta_roi_fee_p25_long_minus_short"] = row["long_roi_fee_p25"] - row["short_roi_fee_p25"]
    if "long_roi_fee_mean" in row and "short_roi_fee_mean" in row:
        row["delta_roi_fee_mean_long_minus_short"] = row["long_roi_fee_mean"] - row["short_roi_fee_mean"]
    if "long_trades_sum" in row and "short_trades_sum" in row:
        row["delta_trades_sum_long_minus_short"] = row["long_trades_sum"] - row["short_trades_sum"]

    out_df = pd.DataFrame([row])

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_csv = os.path.join(
        META_OUT_DIR,
        f"meta_compare_GS_k12_LONG_CANONICAL_vs_SHORT_FINAL_{ts}.csv"
    )
    out_md = os.path.join(
        META_OUT_DIR,
        f"meta_compare_GS_k12_LONG_CANONICAL_vs_SHORT_FINAL_{ts}.md"
    )

    out_df.to_csv(out_csv, index=False)

    # Build MD summary
    md = []
    md.append("# GS Meta Compare: K12 LONG_FINAL_CANONICAL vs SHORT_FINAL")
    md.append("")
    md.append(f"- Timestamp: {ts}")
    md.append(f"- Rows window: {ROWS}")
    md.append(f"- Offsets: {', '.join(str(x) for x in OFFSETS)}")
    md.append(f"- Fee (roundtrip): {FEE}")
    md.append("")
    md.append("## Structural")
    md.append(f"- LONG keys:  {long_n}")
    md.append(f"- SHORT keys: {short_n}")
    md.append(f"- signals_key_match: {row['signals_key_match']}")
    md.append(f"- combination_match_exact: {row['combination_match_exact']}")
    md.append("")
    md.append("## Inputs")
    md.append(f"- LONG strategy:  {LONG_STRAT}")
    md.append(f"- SHORT strategy: {SHORT_STRAT}")
    md.append(f"- LONG results (auto):  {row.get('long_results_path','')}")
    md.append(f"- SHORT results (auto): {row.get('short_results_path','')}")
    md.append("")
    md.append("## Key Metrics (if available)")
    for k in ["roi_fee_p25", "roi_fee_mean", "trades_sum"]:
        lk = "long_" + k
        sk = "short_" + k
        if lk in row:
            md.append(f"- LONG {k}: {row[lk]}")
        if sk in row:
            md.append(f"- SHORT {k}: {row[sk]}")
    if "delta_roi_fee_p25_long_minus_short" in row:
        md.append(f"- delta roi_fee_p25 (LONG - SHORT): {row['delta_roi_fee_p25_long_minus_short']}")
    if "delta_roi_fee_mean_long_minus_short" in row:
        md.append(f"- delta roi_fee_mean (LONG - SHORT): {row['delta_roi_fee_mean_long_minus_short']}")
    if "delta_trades_sum_long_minus_short" in row:
        md.append(f"- delta trades_sum (LONG - SHORT): {row['delta_trades_sum_long_minus_short']}")
    md.append("")
    md.append("## Notes")
    md.append("- Read-only report; no FINAL artifacts are modified.")
    md.append("- Results files are auto-detected by newest mtime in results/GS/k12_long and results/GS/k12_short.")
    md.append("")

    write_md(out_md, md)

    print("[ok] wrote:", out_csv)
    print("[ok] wrote:", out_md)


if __name__ == "__main__":
    main()

