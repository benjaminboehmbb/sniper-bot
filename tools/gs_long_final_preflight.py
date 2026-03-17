#!/usr/bin/env python3
# tools/gs_long_final_preflight.py
#
# Read-only preflight for diagnosing why K12 LONG FULL has 0 canonical K12=12/12 candidates
# under the GS contract (comb uses short keys only; *_signal is internal via KEYMAP).
#
# What it prints (ASCII-only):
# - Row/col counts, column presence
# - Sample of raw combinations (first N)
# - Key-type ratios: only_short / only_signal / mixed / unknown_keys
# - Key-count distribution (len(keys))
# - Weight checks (all 1.0?)
# - After canonicalization (short keys), unique_short_count distribution
# - PASS candidates count: unique_short_count == 12 AND no duplicates AND all weights==1.0
# - Top unknown keys (if any)
#
# Usage (WSL, repo root):
#   python3 tools/gs_long_final_preflight.py
#   python3 tools/gs_long_final_preflight.py --csv <path> --sample 10

import argparse
import os
from collections import Counter

import pandas as pd


DEFAULT_CSV = (
    "results/GS/k12_long/"
    "strategy_results_GS_k12_long_FULL_2026-01-09_15-46-13.csv"
)

SHORT_KEYS = {
    "rsi", "macd", "bollinger",
    "ma200", "stoch", "atr", "ema50",
    "adx", "cci", "mfi", "obv", "roc",
}

SIGNAL_TO_SHORT = {
    "rsi_signal": "rsi",
    "macd_signal": "macd",
    "bollinger_signal": "bollinger",
    "ma200_signal": "ma200",
    "stoch_signal": "stoch",
    "atr_signal": "atr",
    "ema50_signal": "ema50",
    "adx_signal": "adx",
    "cci_signal": "cci",
    "mfi_signal": "mfi",
    "obv_signal": "obv",
    "roc_signal": "roc",
}

SIGNAL_KEYS = set(SIGNAL_TO_SHORT.keys())


def parse_args():
    ap = argparse.ArgumentParser(description="GS LONG FINAL preflight (read-only).")
    ap.add_argument("--csv", default=DEFAULT_CSV, help="K12 LONG FULL results CSV")
    ap.add_argument("--sample", type=int, default=5, help="Number of sample combinations to print")
    ap.add_argument("--max_unknown_print", type=int, default=10, help="Top unknown keys to print")
    return ap.parse_args()


def safe_eval_dict(s: str) -> dict:
    d = eval(s, {"__builtins__": {}}, {})
    if not isinstance(d, dict):
        raise ValueError("combination is not a dict")
    out = {}
    for k, v in d.items():
        out[str(k)] = float(v)
    return out


def analyze_row_keys(d: dict):
    keys = list(d.keys())
    keyset = set(keys)

    has_short = len(keyset.intersection(SHORT_KEYS)) > 0
    has_signal = len(keyset.intersection(SIGNAL_KEYS)) > 0

    unknown = [k for k in keys if (k not in SHORT_KEYS and k not in SIGNAL_KEYS)]
    unknown_set = set(unknown)

    if unknown_set:
        key_type = "unknown_present"
    elif has_short and has_signal:
        key_type = "mixed_short_and_signal"
    elif has_signal and not has_short:
        key_type = "only_signal"
    elif has_short and not has_signal:
        key_type = "only_short"
    else:
        key_type = "empty_or_unexpected"

    return key_type, keys, unknown


def canonicalize_to_short(d: dict):
    """
    Convert keys to short keys for diagnostic purposes.
    Returns:
      can_short: dict or None
      reason: string
      dup_after_map: bool
      all_weights_one: bool
      unknown_keys: list
    """
    out = {}
    dup_after_map = False
    unknown_keys = []
    all_weights_one = True

    for k, v in d.items():
        vv = float(v)
        if abs(vv - 1.0) > 1e-12:
            all_weights_one = False

        if k in SIGNAL_TO_SHORT:
            sk = SIGNAL_TO_SHORT[k]
        elif k in SHORT_KEYS:
            sk = k
        else:
            unknown_keys.append(k)
            continue

        if sk in out:
            dup_after_map = True
        out[sk] = 1.0

    if unknown_keys:
        return None, "unknown_keys", dup_after_map, all_weights_one, unknown_keys
    if not all_weights_one:
        return None, "weight_not_one", dup_after_map, all_weights_one, unknown_keys
    if dup_after_map:
        return None, "duplicate_after_map", dup_after_map, all_weights_one, unknown_keys

    return out, "ok", dup_after_map, all_weights_one, unknown_keys


def main():
    args = parse_args()

    if not os.path.exists(args.csv):
        raise SystemExit(f"[fatal] CSV not found: {args.csv}")

    df = pd.read_csv(args.csv)

    print("[info] CSV:", args.csv)
    print("[info] rows:", len(df), "cols:", len(df.columns))
    print("[info] columns:", list(df.columns))

    if "combination" not in df.columns:
        raise SystemExit("[fatal] Missing column: combination")

    # Basic counters
    keytype_counter = Counter()
    keycount_counter = Counter()
    weight_nonone_counter = 0
    parse_fail = 0

    unknown_key_counter = Counter()

    # Canonicalization diagnostics
    can_reason_counter = Counter()
    unique_short_count_counter = Counter()
    pass_candidates = 0

    # Samples
    sample_n = max(0, int(args.sample))
    printed = 0

    for idx, row in df.iterrows():
        s = str(row["combination"])

        try:
            comb = safe_eval_dict(s)
        except Exception:
            parse_fail += 1
            continue

        # Print samples
        if printed < sample_n:
            print("[sample]", printed + 1, s)
            printed += 1

        # Raw key analysis
        kt, keys, unknown = analyze_row_keys(comb)
        keytype_counter[kt] += 1
        keycount_counter[len(set(keys))] += 1

        for uk in unknown:
            unknown_key_counter[uk] += 1

        # Weight checks
        for v in comb.values():
            if abs(float(v) - 1.0) > 1e-12:
                weight_nonone_counter += 1
                break

        # Canonicalization checks
        can, reason, dup_after_map, all_one, unk = canonicalize_to_short(comb)
        can_reason_counter[reason] += 1

        if can is not None:
            n_short = len(can.keys())
            unique_short_count_counter[n_short] += 1

            # PASS definition for K12 final candidates under GS contract:
            # - ok canonicalization
            # - exactly 12 unique short keys
            # - contains the full SHORT_KEYS set
            if n_short == 12 and set(can.keys()) == SHORT_KEYS:
                pass_candidates += 1

    print("[info] parse_fail:", parse_fail)

    # Raw key type summary
    total_parsed = len(df) - parse_fail
    print("[summary] parsed_rows:", total_parsed)

    def pct(x):
        if total_parsed <= 0:
            return 0.0
        return 100.0 * float(x) / float(total_parsed)

    for k in sorted(keytype_counter.keys()):
        print("[keys] %-22s %8d (%.2f%%)" % (k, keytype_counter[k], pct(keytype_counter[k])))

    # Keycount distribution
    print("[dist] unique_key_count (raw) distribution (count):")
    for k in sorted(keycount_counter.keys()):
        print("  %2d : %d" % (k, keycount_counter[k]))

    # Weight not 1.0 count (row-level)
    print("[weights] rows_with_any_weight_not_1.0:", weight_nonone_counter, "(%.2f%%)" % pct(weight_nonone_counter))

    # Canonicalization reasons
    print("[canon] canonicalization result reasons:")
    for k in sorted(can_reason_counter.keys()):
        print("  %-18s %8d (%.2f%%)" % (k, can_reason_counter[k], pct(can_reason_counter[k])))

    # Unique short count after canonicalization (only for reason==ok)
    ok_rows = can_reason_counter.get("ok", 0)
    print("[canon] ok_rows:", ok_rows, "(%.2f%%)" % pct(ok_rows))
    if ok_rows > 0:
        print("[canon] unique_short_count distribution among ok_rows:")
        # Recompute percentage among ok_rows
        for n in sorted(unique_short_count_counter.keys()):
            c = unique_short_count_counter[n]
            p = 100.0 * float(c) / float(ok_rows) if ok_rows > 0 else 0.0
            print("  %2d : %8d (%.2f%%)" % (n, c, p))

    # PASS candidates
    print("[pass] canonical K12=12/12 candidates:", pass_candidates)

    # Unknown keys top
    if unknown_key_counter:
        print("[unknown] top unknown keys:")
        for k, c in unknown_key_counter.most_common(int(args.max_unknown_print)):
            print("  %-24s %d" % (k, c))

    print("[done] preflight complete")


if __name__ == "__main__":
    main()
