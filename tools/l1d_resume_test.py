#!/usr/bin/env python3
# tools/l1d_resume_test.py
#
# Deterministic L1-D resume verification test.
#
# Test logic:
# 1. Run the L1 loop for N ticks
# 2. Read last_snapshot_id from state
# 3. Run loop again
# 4. Verify the first snapshot of the second run is exactly +1
#
# Fails if restart begins again at CSV-00000001.
#
# ASCII-only.

from __future__ import annotations

import os
import subprocess
import json
import re
from pathlib import Path


REPO_ROOT = Path(".").resolve()
STATE_DIR = REPO_ROOT / "live_state"
LOG_PATH = REPO_ROOT / "live_logs" / "l1d_resume_test.log"


SNAPSHOT_RE = re.compile(r"snapshot_id=(CSV-\d+)")


def run_loop(max_ticks: int) -> str:
    env = os.environ.copy()
    env["L1_LOG_PATH"] = str(LOG_PATH)

    cmd = [
        "python3",
        "-m",
        "scripts.run_live_l1_paper",
        "--repo-root",
        ".",
        "--max-ticks",
        str(max_ticks),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError("L1 loop execution failed")

    return result.stdout


def extract_first_snapshot(log_text: str) -> str:
    for line in log_text.splitlines():
        if "event=market_snapshot" in line:
            m = SNAPSHOT_RE.search(line)
            if m:
                return m.group(1)

    raise RuntimeError("No snapshot found in log")


def snapshot_index(snapshot_id: str) -> int:
    return int(snapshot_id.split("-")[1])


def load_last_snapshot_from_state() -> str:
    s2_path = STATE_DIR / "s2_position.jsonl"

    if not s2_path.exists():
        raise RuntimeError("Missing state file: s2_position.jsonl")

    last_line = None

    with open(s2_path, "r") as f:
        for line in f:
            last_line = line

    if last_line is None:
        raise RuntimeError("State file empty")

    data = json.loads(last_line)

    sid = data.get("snapshot_id")

    if not sid:
        raise RuntimeError("snapshot_id missing in state")

    return sid


def main() -> int:
    print("L1-D resume test starting")
    print("repo:", REPO_ROOT)

    print("\nRun #1 (initial run)")
    run_loop(max_ticks=3)

    last_snapshot = load_last_snapshot_from_state()
    last_idx = snapshot_index(last_snapshot)

    print("last_snapshot_id:", last_snapshot)

    print("\nRun #2 (resume run)")
    out = run_loop(max_ticks=1)

    first_snapshot_resume = extract_first_snapshot(out)
    first_idx = snapshot_index(first_snapshot_resume)

    print("resume_first_snapshot:", first_snapshot_resume)

    expected = last_idx + 1

    if first_idx != expected:
        print("\nFAIL")
        print("Expected snapshot:", f"CSV-{expected:08d}")
        print("Observed snapshot:", first_snapshot_resume)
        return 1

    print("\nPASS")
    print("Resume correctly continued from snapshot", last_snapshot)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())