#!/usr/bin/env python3
import os
import csv
import ast
import pandas as pd

ALL_SIGNALS = ["rsi", "macd", "stoch", "bollinger", "mfi", "obv", "roc"]
WEIGHTS = [round(i / 10.0, 1) for i in range(1, 11)]  # 0.1 ... 1.0
TOP_N = 8000
RESULTS_FILENAME = "strategy_results_long_k3_2025-11-14_17-06-51.csv"
OUTPUT_BASENAME = "strategies_k4_from_k3_top%d_long.csv" % TOP_N


def find_combo_column(df):
    candidates = ["Combination", "combination", "combo", "strategy", "Strategy"]
    for col in candidates:
        if col in df.columns:
            return col

    for col in df.columns:
        series = df[col].dropna()
        if series.empty:
            continue
        val = str(series.iloc[0]).strip()
        if val.startswith("{") and ":" in val and "}" in val:
            return col

    raise ValueError("Keine Kombinationsspalte gefunden.")


def parse_combination(value):
    if isinstance(value, dict):
        return value
    return ast.literal_eval(str(value))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    results_path = os.path.join(project_root, "results", RESULTS_FILENAME)
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    out_path = os.path.join(data_dir, OUTPUT_BASENAME)

    print("Loading K3 results from:")
    print(results_path)

    df = pd.read_csv(results_path)

    if "roi" not in df.columns:
        raise ValueError("Spalte 'roi' nicht vorhanden.")

    combo_col = find_combo_column(df)
    print("Using combination column:", combo_col)

    df_sorted = df.sort_values("roi", ascending=False)
    top = df_sorted.head(TOP_N).copy()

    print("Total K3 strategies:", len(df))
    print("Using top", TOP_N)

    total_input = 0
    total_output = 0
    seen = set()

    with open(out_path, "w", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Combination"])

        for _, row in top.iterrows():
            combo_raw = row[combo_col]
            try:
                combo_dict = parse_combination(combo_raw)
            except Exception:
                continue

            base_signals = [s for s in combo_dict.keys() if s in ALL_SIGNALS]
            if len(base_signals) != 3:
                continue

            total_input += 1

            remaining = [s for s in ALL_SIGNALS if s not in base_signals]

            for extra in remaining:
                for w_extra in WEIGHTS:
                    new_dict = dict(combo_dict)
                    new_dict[extra] = w_extra

                    key = tuple(sorted(new_dict.items()))
                    if key in seen:
                        continue
                    seen.add(key)

                    writer.writerow([repr(new_dict)])
                    total_output += 1

                    if total_output % 50000 == 0:
                        print("Generated %d K4 strategies..." % total_output)

    print("Done.")
    print("Input K3 used:", total_input)
    print("Generated K4:", total_output)
    print("Output:", out_path)


if __name__ == "__main__":
    main()
