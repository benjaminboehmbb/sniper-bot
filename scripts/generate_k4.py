#!/usr/bin/env python3
import os
import csv
import ast

import pandas as pd


ALL_SIGNALS = ["rsi", "macd", "stoch", "bollinger", "mfi", "obv", "roc"]
WEIGHTS = [round(i / 10.0, 1) for i in range(1, 11)]  # 0.1 ... 1.0
TOP_N = 1000
RESULTS_FILENAME = "strategy_results_long_k3_2025-11-14_17-06-51.csv"
OUTPUT_BASENAME = "strategies_k4_from_k3_top%d.csv" % TOP_N


def find_combo_column(df):
    """
    Versucht, die Spalte zu finden, in der die K3-Kombination
    als Dict-String gespeichert ist (z. B. "{'rsi': 0.1, 'macd': 0.2, 'roc': 0.7}").
    """
    candidates = ["Combination", "combination", "combo", "strategy", "Strategy"]
    for col in candidates:
        if col in df.columns:
            return col

    # Fallback: erste Spalte suchen, deren erste nicht-leere Zelle wie ein Dict aussieht
    for col in df.columns:
        series = df[col].dropna()
        if series.empty:
            continue
        val = str(series.iloc[0]).strip()
        if val.startswith("{") and ":" in val and "}" in val:
            return col

    raise ValueError("Keine geeignete Kombinationsspalte gefunden.")


def parse_combination(value):
    """
    Wandelt den Dict-String in ein echtes Python-Dict um.
    Erwartet z. B. "{'rsi': 0.1, 'macd': 0.2, 'roc': 0.7}".
    """
    if isinstance(value, dict):
        return value
    text = str(value)
    return ast.literal_eval(text)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    results_dir = os.path.join(project_root, "results")
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    results_path = os.path.join(results_dir, RESULTS_FILENAME)
    out_path = os.path.join(data_dir, OUTPUT_BASENAME)

    print("Loading K3 results from:")
    print(results_path)

    if not os.path.isfile(results_path):
        raise FileNotFoundError(
            "Ergebnisdatei nicht gefunden: %s" % results_path
        )

    df = pd.read_csv(results_path)

    if "roi" not in df.columns:
        raise ValueError("Spalte 'roi' nicht in Ergebnisdatei gefunden.")

    combo_col = find_combo_column(df)
    print("Using combination column: %s" % combo_col)

    # Top-N nach ROI
    df_sorted = df.sort_values("roi", ascending=False)
    top = df_sorted.head(TOP_N).copy()

    print("Total K3 strategies in file: %d" % len(df))
    print("Using top %d by roi." % len(top))

    total_input_strats = 0
    total_output_k4 = 0
    seen = set()

    with open(out_path, "w", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Combination"])

        for _, row in top.iterrows():
            combo_raw = row[combo_col]
            try:
                combo_dict = parse_combination(combo_raw)
            except Exception as e:
                print("Warning: konnte Kombination nicht parsen, ueberspringe. Wert:")
                print(combo_raw)
                print("Fehler: %s" % str(e))
                continue

            # Sicherstellen, dass nur bekannte Signale verwendet werden
            base_signals = [s for s in combo_dict.keys() if s in ALL_SIGNALS]
            if len(base_signals) != 3:
                # Falls unerwartete Struktur, ueberspringen
                print("Warning: unerwartete Anzahl Basis-Signale (%d), ueberspringe." % len(base_signals))
                continue

            total_input_strats += 1

            remaining_signals = [s for s in ALL_SIGNALS if s not in base_signals]

            for extra_signal in remaining_signals:
                for w_extra in WEIGHTS:
                    new_dict = dict(combo_dict)
                    new_dict[extra_signal] = w_extra

                    # Key zur Duplikat-Vermeidung (sortiert nach Signalnamen)
                    key = tuple(sorted(new_dict.items()))
                    if key in seen:
                        continue
                    seen.add(key)

                    writer.writerow([repr(new_dict)])
                    total_output_k4 += 1

                    if total_output_k4 % 50000 == 0:
                        print("Generated %d K4 strategies..." % total_output_k4)

    print("Done.")
    print("Input top K3 strategies used: %d" % total_input_strats)
    print("Total unique K4 strategies generated: %d" % total_output_k4)
    print("Output written to: %s" % out_path)


if __name__ == "__main__":
    main()
