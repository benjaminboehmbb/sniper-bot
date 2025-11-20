#!/usr/bin/env python3
# scripts/pipeline_orchestrator.py
# ASCII-only. Minimaler orchestrator für Pipeline 2.0.
# - führt Preflight (engine.validators) aus
# - iteriert über strategy-shards und startet für jeden einen Runner (konfigurierbar)
# - sichert alte results (backup) und schreibt run_meta.json
# - unterstützt dry-run und einfache Logging-Ausgaben
#
# Usage:
#  python -u scripts/pipeline_orchestrator.py --config config/run.yaml
#
# Wichtig: Der "runner_template" in config/run.yaml muss angepasst werden,
# falls deine analyze-Skripte andere CLI-Flags / Namen haben.

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
import yaml

# ---------------------------
# Helpers
# ---------------------------
def now_ts():
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

def info(msg):
    sys.stdout.write("[INFO] " + msg + "\n")
    sys.stdout.flush()

def warn(msg):
    sys.stderr.write("[WARN] " + msg + "\n")
    sys.stderr.flush()

def err(msg):
    sys.stderr.write("[ERROR] " + msg + "\n")
    sys.stderr.flush()

# ---------------------------
# Core
# ---------------------------
def load_config(path):
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg

def run_preflight(price_path, strategies_glob):
    info("Running preflight validators...")
    cmd = [
        sys.executable, "-m", "engine.validators",
        "--price", price_path,
        "--strategies-glob", strategies_glob
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(res.stdout)
    if res.returncode != 0:
        raise RuntimeError("Preflight validators failed.")
    info("Preflight passed.")

def backup_existing_results(results_dir, archive_dir):
    if not os.path.exists(results_dir):
        info(f"No results dir to backup at {results_dir}")
        return None
    ts = now_ts()
    dest = os.path.join(archive_dir, f"backup_results_{ts}")
    os.makedirs(archive_dir, exist_ok=True)
    info(f"Backing up {results_dir} -> {dest}")
    shutil.copytree(results_dir, dest)
    return dest

def write_run_meta(out_dir, meta):
    os.makedirs(out_dir, exist_ok=True)
    meta_path = os.path.join(out_dir, f"run_meta_{now_ts()}.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    info(f"Wrote run meta: {meta_path}")
    return meta_path

def find_shards(shards_list, shards_glob_template):
    shards = []
    if shards_list:
        for p in shards_list:
            if os.path.exists(p):
                shards.append(p)
            else:
                warn(f"Shard not found: {p}")
    else:
        # use glob template
        shards = sorted(glob.glob(shards_glob_template))
    return shards

def build_runner_cmd(template, subs):
    # simple .format substitution
    return template.format(**subs)

def run_worker(cmd, dry_run=False):
    info(f"Runner cmd: {cmd}")
    if dry_run:
        info("Dry-run: skipping execution.")
        return 0
    # run streaming output
    p = subprocess.Popen(cmd, shell=True)
    p.wait()
    return p.returncode

# ---------------------------
# Entrypoint
# ---------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="Path to config/run.yaml")
    ap.add_argument("--dry-run", action="store_true", help="Only print commands")
    args = ap.parse_args()

    cfg = load_config(args.config)

    # canonicalize config minimal fields
    price_path = cfg["price"]["path"]
    time_col = cfg["price"].get("time_col", "open_time")
    k = int(cfg["strategies"]["k"])
    shards_list = cfg["strategies"].get("shards", [])
    shards_glob = cfg["strategies"].get("shards_glob", f"data/strategies/k{k}/strategies_k{k}_*.csv")

    sim_mode = cfg["sim"]["mode"]
    results_dir = cfg["output"]["results_dir"]
    logs_dir = cfg["output"].get("logs_dir", "logs")
    archive_dir = cfg["output"].get("archive_dir", "archive")

    runner_template = cfg.get("runner_template",
        # default template -- adjust to your analyze script naming if needed
        "python -u scripts/analyze_{k}er_mp.py --data {price} --strategies {shard} --sim {sim} "
        "--num-procs {num_procs} --chunksize {chunksize} --progress_step {progress_step} --save-trades {save_trades} --output-dir {results_dir}"
    )

    runner_subs_defaults = {
        "k": k,
        "price": price_path,
        "sim": sim_mode,
        "num_procs": cfg["engine"].get("num_procs", 8),
        "chunksize": cfg["engine"].get("chunksize", 512),
        "progress_step": cfg["engine"].get("progress_step", 2),
        "save_trades": cfg["engine"].get("save_trades", 0),
        "results_dir": results_dir,
    }

    # 0) Preflight
    try:
        # build glob to pass validators
        strategies_glob_for_validator = shards_glob if shards_list == [] else shards_list[0]
        run_preflight(price_path, strategies_glob_for_validator)
    except Exception as e:
        err(str(e))
        sys.exit(2)

    # 1) Backup existing results
    backup_existing_results(results_dir, archive_dir)

    # 2) gather shards
    shards = find_shards(shards_list, shards_glob)
    if not shards:
        err(f"No strategy shards found with pattern: {shards_glob}")
        sys.exit(3)
    info(f"Found {len(shards)} shard(s). First shard: {shards[0]}")

    # 3) run shards sequentially
    run_start = time.time()
    errors = []
    for i, shard in enumerate(shards, start=1):
        info(f"=== Running shard {i}/{len(shards)}: {shard} ===")
        subs = runner_subs_defaults.copy()
        subs["shard"] = shard
        cmd = build_runner_cmd(runner_template, subs)
        rc = run_worker(cmd, dry_run=args.dry_run)
        if rc != 0:
            errors.append({"shard": shard, "rc": rc})
            warn(f"Shard failed (rc={rc}): {shard}")
        else:
            info(f"Shard completed: {shard}")

    run_end = time.time()
    # 4) write run meta
    meta = {
        "run": cfg.get("run_name", f"k{k}_{sim_mode}_{now_ts()}"),
        "k": k,
        "sim": sim_mode,
        "shards_run": len(shards),
        "shards": shards,
        "start_utc": now_ts(),
        "duration_s": int(run_end - run_start),
        "errors": errors,
    }
    write_run_meta(logs_dir, meta)

    if errors:
        warn(f"Finished with {len(errors)} error(s). See logs.")
        sys.exit(4)

    info("Orchestration finished successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
