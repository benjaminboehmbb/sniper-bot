#!/usr/bin/env python3
# tools/validate_price_1m.py
"""
Validates 1m price CSV against schema, reports NaNs, duplicates, monotony and gaps.
Produces:
 - data/validate_report.json
 - data/gaps.csv
Usage:
  python tools/validate_price_1m.py data/btcusdt_1m_spot.csv
"""
import os
import sys
import json
import argparse
from datetime import datetime, timezone
import pandas as pd
import numpy as np

def load_schema(path="config/schema_price_1m.json"):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ms_to_iso(ms):
    return datetime.utcfromtimestamp(int(ms)//1000).replace(tzinfo=timezone.utc).isoformat().replace("+00:00","Z")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="Path to 1m CSV (e.g. data/btcusdt_1m_spot.csv)")
    ap.add_argument("--schema", default="config/schema_price_1m.json", help="Schema JSON path")
    args = ap.parse_args()

    csv_path = args.csv
    if not os.path.exists(csv_path):
        print("ERROR: CSV nicht gefunden:", csv_path)
        sys.exit(2)

    print("Lade CSV (keine Spaltenbegrenzung) ...")
    df = pd.read_csv(csv_path)
    n_rows = len(df)
    print(f"Rows: {n_rows:,}")

    schema = load_schema(args.schema)
    report = {
        "csv": csv_path,
        "rows": int(n_rows),
        "schema_present": bool(schema),
        "expected_columns": schema.get("columns", []) if schema else [],
        "found_columns": list(df.columns),
        "missing_columns": [],
        "extra_columns": [],
        "nan_counts": {},
        "duplicate_timestamps": 0,
        "duplicates_sample": [],
        "monotonic_60s": None,
        "num_gaps": 0,
        "largest_gap_min": 0,
        "gaps_file": "data/gaps.csv"
    }

    if schema:
        expected = schema.get("columns", [])
        found = list(df.columns)
        report["missing_columns"] = [c for c in expected if c not in found]
        report["extra_columns"]   = [c for c in found if c not in expected]

    # NaN counts
    nan_counts = df.isna().sum().to_dict()
    report["nan_counts"] = {k:int(v) for k,v in nan_counts.items()}

    # Duplicates by open_time
    if "open_time" in df.columns:
        dup_mask = df.duplicated(subset=["open_time"], keep=False)
        dup_count = int(dup_mask.sum())
        report["duplicate_timestamps"] = dup_count
        if dup_count:
            dup_sample = df[dup_mask].head(20).to_dict(orient="records")
            report["duplicates_sample"] = dup_sample

    # Monotony and gap detection
    if "open_time" not in df.columns:
        print("WARN: open_time Spalte fehlt — keine Gap-Analyse möglich.")
    else:
        # ensure integer
        ts = df["open_time"].astype("int64").values
        # sort by open_time to be safe
        order = np.argsort(ts)
        if not np.all(order == np.arange(len(ts))):
            ts = ts[order]
        seconds = ts // 1000
        diffs = seconds[1:] - seconds[:-1]
        # check monotonic 60s
        is_60 = np.all(diffs == 60)
        report["monotonic_60s"] = bool(is_60)
        # gaps where diff != 60
        idx = np.where(diffs != 60)[0]
        gaps = []
        for i in idx:
            prev_s = int(seconds[i])
            curr_s = int(seconds[i+1])
            gap_min = int((curr_s - prev_s) // 60)
            gaps.append({
                "prev_open_time_s": prev_s,
                "prev_iso": datetime.utcfromtimestamp(prev_s).replace(tzinfo=timezone.utc).isoformat().replace("+00:00","Z"),
                "curr_open_time_s": curr_s,
                "curr_iso": datetime.utcfromtimestamp(curr_s).replace(tzinfo=timezone.utc).isoformat().replace("+00:00","Z"),
                "gap_minutes": gap_min
            })
        report["num_gaps"] = int(len(gaps))
        report["largest_gap_min"] = int(max([g["gap_minutes"] for g in gaps]) if gaps else 0)

        # Save gaps CSV if any
        os.makedirs("data", exist_ok=True)
        if gaps:
            gap_df = pd.DataFrame(gaps)
            gap_df.to_csv("data/gaps.csv", index=False)
            print(f"[INFO] Gaps gefunden: {len(gaps)} -> data/gaps.csv geschrieben")
        else:
            # remove old gaps file if exists
            try:
                if os.path.exists("data/gaps.csv"):
                    os.remove("data/gaps.csv")
            except Exception:
                pass

    # Write report
    with open("data/validate_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Pretty print summary
    print("=== VALIDATION SUMMARY ===")
    print(f"Rows: {report['rows']:,}")
    if schema:
        print("Schema geladen:", args.schema)
        print("Missing cols:", report["missing_columns"])
        print("Extra cols:", report["extra_columns"])
    print("NaN counts (cols with >0):")
    for k,v in report["nan_counts"].items():
        if v>0:
            print(f"  {k}: {v}")
    print("Duplicate timestamps (rows):", report["duplicate_timestamps"])
    print("Monotonisch 60s zwischen Zeilen?:", report["monotonic_60s"])
    print("Anzahl Abweichungen / Gaps:", report["num_gaps"])
    print("Größte Lücke (min):", report["largest_gap_min"])
    print("")
    print("Report -> data/validate_report.json")
    if report["num_gaps"]:
        print("Gaps -> data/gaps.csv  (öffnen/prüfen!)")
    print("Done.")

if __name__ == "__main__":
    main()
