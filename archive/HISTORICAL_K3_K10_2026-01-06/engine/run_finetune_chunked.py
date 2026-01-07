#!/usr/bin/env python3
# ASCII only: run_finetune_chunked.py

import argparse
import os
import sys
import time
import subprocess
from pathlib import Path

import pandas as pd


DESC = "Chunked runner to safely evaluate many strategies via analyze_template.py (resume-fähig, long/short, mit normalize-mode)."


def parse_args():
    p = argparse.ArgumentParser(description=DESC)

    # Original-Parameter
    p.add_argument("--data", required=True)
    p.add_argument("--strategies", required=True)
    p.add_argument("--sim", choices=["long", "short"], required=True)
    p.add_argument("--threshold", type=float, default=0.60)
    p.add_argument("--cooldown", type=int, default=0)
    p.add_argument("--require-ma200", type=int, default=0)
    p.add_argument("--min-trades", type=int, default=0)
    p.add_argument("--max-trades", type=int, default=500000)
    p.add_argument("--normalize", type=int, default=0)
    p.add_argument("--save-trades", type=int, default=0)
    p.add_argument("--min-hold-mins", type=int, default=None)
    p.add_argument("--max-hold-mins", type=int, default=None)
    p.add_argument("--regime-filter", type=int, default=0)
    p.add_argument("--regime-col", type=str, default="regime")
    p.add_argument("--regime-check", choices=["entry", "both", "exit"], default="entry")

    p.add_argument("--output-dir", required=True,
                  help="Final output dir for merged results")
    p.add_argument("--chunksize", type=int, default=200,
                  help="Number of strategies per chunk CSV")
    p.add_argument("--tmp-root", default="results/_chunk_tmp",
                  help="Temp root dir to place chunk outputs")
    p.add_argument("--analyze-script", default="engine/analyze_template.py",
                  help="Path to analyze_template.py")
    p.add_argument("--progress-step", type=int, default=1,
                  help="Forwarded to analyze_template.py")
    p.add_argument("--python-bin", default=sys.executable,
                  help="Python binary to invoke")

    # NEU: normalize-mode wie in analyze_template.py
    p.add_argument(
        "--normalize-mode",
        choices=["minmax", "zscore", "none"],
        default="minmax",
        help="Normalization mode forwarded to analyze_template.py",
    )

    return p.parse_args()


def ensure_dir(d: Path):
    d.mkdir(parents=True, exist_ok=True)


def run_chunk(pybin, analyze_script, args, chunk_csv, chunk_outdir):
    cmd = [
        pybin,
        "-u",
        analyze_script,
        "--data",
        args.data,
        "--strategies",
        str(chunk_csv),
        "--sim",
        args.sim,
        "--threshold",
        str(args.threshold),
        "--cooldown",
        str(args.cooldown),
        "--require-ma200",
        str(args.require_ma200),
        "--min-trades",
        str(args.min_trades),
        "--max-trades",
        str(args.max_trades),
        "--num-procs",
        "1",  # bewusst: 1 Prozess je Chunk, damit es deterministisch bleibt
        "--chunksize",
        "1",
        "--progress-step",
        str(args.progress_step),
        "--save-trades",
        str(args.save_trades),
        "--normalize",
        str(args.normalize),
        "--normalize-mode",
        args.normalize_mode,
        "--output-dir",
        str(chunk_outdir),
        "--min-hold-mins",
        str(args.min_hold_mins) if args.min_hold_mins is not None else "0",
        "--max-hold-mins",
        str(args.max_hold_mins) if args.max_hold_mins is not None else "0",
        "--regime-filter",
        str(args.regime_filter),
        "--regime-col",
        args.regime_col,
        "--regime-check",
        args.regime_check,
    ]

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "UTF-8"

    print("[INFO] Running chunk:", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, env=env)
    if proc.returncode != 0:
        raise RuntimeError("Chunk run failed with return code {}".format(proc.returncode))


def main():
    args = parse_args()
    start_ts = time.time()

    strategies_path = Path(args.strategies)
    if not strategies_path.exists():
        raise SystemExit("Strategies CSV not found: {}".format(strategies_path))

    df = pd.read_csv(strategies_path)
    if "Combination" not in df.columns:
        raise SystemExit("Input CSV missing 'Combination' column")

    total = len(df)
    chunksize = max(1, int(args.chunksize))

    out_dir = Path(args.output_dir)
    ensure_dir(out_dir)
    merged_csv = out_dir / "strategy_results.csv"

    tmp_root = Path(args.tmp_root)
    ensure_dir(tmp_root)

    print("[INFO] Total strategies: {} | chunksize: {}".format(total, chunksize), flush=True)

    merged_parts = []
    processed_total = 0

    # Chunk-Schleife (mit Resume: vorhandene chunk-resultate werden übersprungen)
    for i in range(0, total, chunksize):
        j = min(i + chunksize, total)
        chunk_df = df.iloc[i:j].copy()
        tag = "chunk_{:07d}_{:07d}".format(i, j)

        chunk_dir = tmp_root / (out_dir.name + "_" + tag)
        chunk_csv = chunk_dir / "strategies.csv"
        chunk_out = chunk_dir / "out"
        chunk_result = chunk_out / "strategy_results.csv"

        ensure_dir(chunk_dir)
        ensure_dir(chunk_out)

        if chunk_result.exists() and chunk_result.stat().st_size > 0:
            print("[INFO] Skipping existing {} (found results).".format(tag), flush=True)
        else:
            chunk_df.to_csv(chunk_csv, index=False)
            run_chunk(args.python_bin, args.analyze_script, args, chunk_csv, chunk_out)

        if not chunk_result.exists():
            raise SystemExit("Missing result for {}: {}".format(tag, str(chunk_result)))

        part = pd.read_csv(chunk_result)
        if "Combination" not in part.columns:
            raise SystemExit("Chunk result {} missing 'Combination' column".format(str(chunk_result)))

        merged_parts.append(part)
        processed_total += len(part)

        merged_df = pd.concat(merged_parts, ignore_index=True)
        merged_df.to_csv(merged_csv, index=False)
        pct = 100.0 * processed_total / max(1, total)
        print("[INFO] Merged {} rows -> {} (Progress: {:.2f}%)".format(
            len(merged_df), str(merged_csv), pct
        ), flush=True)

    dur = time.time() - start_ts
    print("[INFO] Done. Saved results to {}".format(str(merged_csv)), flush=True)
    print("[INFO] Duration seconds: {}".format(int(dur)), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("[ERROR]", e, file=sys.stderr, flush=True)
        sys.exit(1)

