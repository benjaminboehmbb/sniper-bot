#!/usr/bin/env python3
# scripts/run_live_l1_paper.py
#
# Paper runner for L1 loop.
# Adds:
#   --seeds-5m-csv  -> sets env SEEDS_5M_CSV
#   --thresh-5m     -> sets env THRESH_5M
#
# ASCII-only.

import argparse
import os

from live_l1.core.loop import run_l1_loop_step1234567


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="run_live_l1_paper.py")

    p.add_argument("--repo-root", default=".", help="repo root (default: .)")
    p.add_argument("--run-hours", type=float, default=72.0, help="run duration hours (default: 72)")
    p.add_argument("--max-ticks", type=int, default=0, help="if >0 overrides run-hours with fixed ticks")

    # existing flags you showed in usage
    p.add_argument("--symbol", default="BTCUSDT", help="symbol (default: BTCUSDT)")
    p.add_argument("--gate", default="auto", help="gate mode (default: auto)")
    p.add_argument("--fee-roundtrip", type=float, default=0.0004, help="fee roundtrip (default: 0.0004)")
    p.add_argument("--decision-tick-seconds", type=float, default=1.0, help="tick seconds (default: 1.0)")
    p.add_argument("--trades-window-hours", type=int, default=6, help="trades window hours (default: 6)")
    p.add_argument("--paper", action="store_true", help="paper mode (default: on)")

    # NEW
    p.add_argument("--seeds-5m-csv", default="", help="5m seeds CSV path (sets env SEEDS_5M_CSV)")
    p.add_argument("--thresh-5m", type=float, default=0.60, help="5m threshold (sets env THRESH_5M)")

    return p


def main() -> int:
    args = _build_parser().parse_args()

    # Make runner params visible to loop via env (keeps your current patterns stable)
    os.environ["L1_SYMBOL"] = args.symbol
    os.environ["L1_GATE_MODE"] = args.gate
    os.environ["L1_FEE_ROUNDTRIP"] = str(args.fee_roundtrip)
    os.environ["L1_DECISION_TICK_SECONDS"] = str(args.decision_tick_seconds)
    os.environ["L1_TRADES_WINDOW_HOURS"] = str(args.trades_window_hours)

    # Set 5m config
    os.environ["THRESH_5M"] = str(args.thresh_5m)
    if args.seeds_5m_csv:
        os.environ["SEEDS_5M_CSV"] = args.seeds_5m_csv

    # Compute ticks (still used as a safety cap)
    if args.max_ticks and args.max_ticks > 0:
        max_ticks = int(args.max_ticks)
        max_run_seconds = None
    else:
        seconds = float(args.run_hours) * 3600.0
        max_ticks = int(seconds / float(args.decision_tick_seconds))
        if max_ticks < 1:
            max_ticks = 1
        # NEW: wall-clock stop
        max_run_seconds = seconds

    return int(
        run_l1_loop_step1234567(
            args.repo_root,
            max_ticks=max_ticks,
            max_run_seconds=max_run_seconds,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())











