#!/usr/bin/env python3
# ASCII only
"""
Create a SHORT-inverted copy of a data CSV by negating selected signal columns.
- Inverts: mfi, mfi_signal, rsi, rsi_signal (if present)
- Writes a new CSV beside the input

Usage:
  python tools/add_inverted_short_signals.py <input_csv> <output_csv>
Example:
  python tools/add_inverted_short_signals.py \
    data/price_data_with_signals_regime.csv \
    data/price_data_with_signals_regime_short.csv
"""

import sys, os
import pandas as pd

TARGET_COLS = ["mfi", "mfi_signal", "rsi", "rsi_signal"]

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/add_inverted_short_signals.py <input_csv> <output_csv>")
        sys.exit(2)
    inp, outp = sys.argv[1], sys.argv[2]
    if not os.path.isfile(inp):
        print("ERROR: input_csv not found:", inp)
        sys.exit(3)
    df = pd.read_csv(inp)
    found = []
    for col in TARGET_COLS:
        if col in df.columns:
            df[col] = -1.0 * pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            found.append(col)
    if not found:
        print("WARNING: none of the target columns found. Wrote unchanged copy.")
    else:
        print("Inverted columns:", ", ".join(found))
    df.to_csv(outp, index=False)
    print("Wrote:", outp)

if __name__ == "__main__":
    main()
