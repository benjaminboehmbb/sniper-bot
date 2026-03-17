#!/usr/bin/env python3
# tools/gs_run_guard.py
#
# Purpose:
#   One mandatory guard before ANY run:
#     1) gs_input_preflight.py
#     2) gs_regression_gate.py
#   If both pass, optionally execute a command (after --).
#
# Examples:
#   # Guard only (no follow-up command)
#   python3 tools/gs_run_guard.py --csv data/...REGIMEV1.csv --regime_col regime_v1 --require_signals rsi,macd,ma200
#
#   # Guard + run something afterwards
#   python3 tools/gs_run_guard.py --csv data/...REGIMEV1.csv --regime_col regime_v1 --require_signals rsi,macd,ma200 -- \
#     python3 tools/gs_policy_hold_runner.py --csv data/...REGIMEV1.csv --rows 200000 --offsets "0,500000" --direction long --fee 0.0004 --apply_regime_gate --regime_col regime_v1 --max_hold 240
#
# Notes:
#   - ASCII only.
#   - Exits non-zero on any failure.

from __future__ import annotations

import argparse
import os
import sys
import subprocess
from typing import List


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def die(msg: str, code: int = 1) -> None:
    raise SystemExit(f"[FAIL] {msg}")


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def run_cmd(cmd: List[str]) -> int:
    # Stream output directly; fail if returncode != 0
    p = subprocess.run(cmd)
    return int(p.returncode)


def main() -> None:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--rows", type=int, default=200000)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--fee", type=float, default=0.0004)

    # Preflight inputs
    ap.add_argument("--require_signals", default="rsi,macd,ma200",
                    help="Comma list of signal base names (expects *_signal columns).")
    ap.add_argument("--regime_cols", default="",
                    help="Comma list of regime columns to validate in preflight.")
    ap.add_argument("--timestamp_col", default="")
    ap.add_argument("--require_timestamp", action="store_true")
    ap.add_argument("--fail_on_all_zero_signals", action="store_true")

    # Regression gate input
    ap.add_argument("--regime_col", default="",
                    help="Single regime column name for regression gate (e.g. regime_v1 or regime_v2).")

    # Everything after -- is an optional follow-up command
    args, tail = ap.parse_known_args()

    tools_dir = os.path.join(REPO_ROOT, "tools")
    preflight_py = os.path.join(tools_dir, "gs_input_preflight.py")
    gate_py = os.path.join(tools_dir, "gs_regression_gate.py")

    if not os.path.exists(preflight_py):
        die(f"missing: {preflight_py}")
    if not os.path.exists(gate_py):
        die(f"missing: {gate_py}")

    # --------
    # 1) Preflight
    # --------
    pre_cmd = [
        sys.executable,
        preflight_py,
        "--csv", args.csv,
        "--rows", str(args.rows),
        "--offset", str(args.offset),
        "--require_signals", args.require_signals,
    ]
    if args.regime_cols:
        pre_cmd += ["--regime_cols", args.regime_cols]
    if args.timestamp_col:
        pre_cmd += ["--timestamp_col", args.timestamp_col]
    if args.require_timestamp:
        pre_cmd += ["--require_timestamp"]
    if args.fail_on_all_zero_signals:
        pre_cmd += ["--fail_on_all_zero_signals"]

    rc = run_cmd(pre_cmd)
    if rc != 0:
        die("preflight failed")

    ok("Preflight PASS")

    # --------
    # 2) Regression Gate
    # --------
    gate_cmd = [
        sys.executable,
        gate_py,
        "--csv", args.csv,
        "--rows", str(args.rows),
        "--offset", str(args.offset),
        "--fee", str(args.fee),
    ]
    if args.regime_col:
        gate_cmd += ["--regime_col", args.regime_col]

    rc = run_cmd(gate_cmd)
    if rc != 0:
        die("regression gate failed")

    ok("Regression Gate PASS")
    ok("GS RUN GUARD: ALL PASS")

    # --------
    # 3) Optional follow-up command
    # --------
    if tail:
        # Allow user to pass: -- python3 ... (we do not rewrite)
        if tail[0] == "--":
            tail = tail[1:]
        if not tail:
            return
        ok("Executing follow-up command")
        rc = run_cmd(tail)
        if rc != 0:
            die(f"follow-up command failed (rc={rc})", code=rc)
        ok("Follow-up command PASS")


if __name__ == "__main__":
    main()
