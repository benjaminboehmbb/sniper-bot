#!/usr/bin/env python3
# Merge K8-LONG SEEDS + RANDOMPASS into one pool (dedup by Combination).
# Keeps/creates a 'source' column: seed_expansion vs random_pass.

import argparse
import sys
from pathlib import Path

import pandas as pd


def die(msg: str):
    print(f"[error] {msg}")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Merge K8-LONG SEEDS + RANDOMPASS")
    ap.add_argument("--seeds", required=True, help="strategies_k8_long_SEEDS_*.csv")
    ap.add_argument("--randompass", required=True, help="strategies_k8_long_RANDOMPASS_*.csv (from gate)")
    ap.add_argument("--out", required=True, help="Output merged pool CSV")
    args = ap.parse_args()

    seeds_path = Path(args.seeds)
    rp_path = Path(args.randompass)
    out_path = Path(args.out)

    if not seeds_path.exists():
        die(f"SEEDS file not found: {seeds_path}")
    if not rp_path.exists():
        die(f"RANDOMPASS file not found: {rp_path}")

    seeds = pd.read_csv(seeds_path)
    if "Combination" not in seeds.columns:
        die(f"SEEDS missing Combination column. Columns: {list(seeds.columns)}")
    if "source" not in seeds.columns:
        seeds["source"] = "seed_expansion"
    else:
        seeds["source"] = seeds["source"].fillna("seed_expansion")

    rp = pd.read_csv(rp_path)
    if "Combination" not in rp.columns:
        die(f"RANDOMPASS missing Combination column. Columns: {list(rp.columns)}")
    rp = rp[["Combination"]].copy()
    rp["source"] = "random_pass"

    merged = pd.concat([seeds[["Combination", "source"]], rp], ignore_index=True)
    before = len(merged)
    merged = merged.drop_duplicates(subset=["Combination"], keep="first").copy()
    after = len(merged)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out_path, index=False)

    print("[ok] Merged pool written")
    print(f"[ok] SEEDS rows        : {len(seeds)}")
    print(f"[ok] RANDOMPASS rows   : {len(rp)}")
    print(f"[ok] concat rows       : {before}")
    print(f"[ok] dedup rows        : {after}")
    print(f"[ok] Wrote             : {out_path}")


if __name__ == "__main__":
    main()
