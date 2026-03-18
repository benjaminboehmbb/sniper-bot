#!/usr/bin/env python3
# scripts/run_live_l1_paper.py
#
# Paper runner for L1 loop
# + AUTO ANALYSIS AFTER RUN
# + respects L1_TRADE_LOG_PATH
#
# ASCII-only

import argparse
import os

from live_l1.core.loop import run_l1_loop_step1234567


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="run_live_l1_paper.py")

    p.add_argument("--repo-root", default=".", help="repo root (default: .)")
    p.add_argument("--run-hours", type=float, default=72.0, help="run duration hours (default: 72)")
    p.add_argument("--max-ticks", type=int, default=0, help="if >0 overrides run-hours with fixed ticks")

    p.add_argument("--symbol", default="BTCUSDT", help="symbol (default: BTCUSDT)")
    p.add_argument("--gate", default="auto", help="gate mode (default: auto)")
    p.add_argument("--fee-roundtrip", type=float, default=0.0004, help="fee roundtrip (default: 0.0004)")
    p.add_argument("--decision-tick-seconds", type=float, default=1.0, help="tick seconds (default: 1.0)")
    p.add_argument("--trades-window-hours", type=int, default=6, help="trades window hours (default: 6)")
    p.add_argument("--paper", action="store_true", help="paper mode (default: on)")

    p.add_argument("--seeds-5m-csv", default="", help="5m seeds CSV path")
    p.add_argument("--thresh-5m", type=float, default=0.60, help="5m threshold")

    p.add_argument(
        "--trade-log-path",
        default="",
        help="optional trade log JSONL path (overrides env L1_TRADE_LOG_PATH for this run)",
    )
    p.add_argument(
        "--analysis-csv-out",
        default="",
        help="optional analysis CSV path (default: derived from trade log path)",
    )
    p.add_argument(
        "--start-capital",
        type=float,
        default=10000.0,
        help="start capital for auto analysis (default: 10000)",
    )

    return p


def _derive_analysis_csv_path(trades_file: str) -> str:
    base, _ext = os.path.splitext(trades_file)
    return base + "_auto_analysis.csv"


def main() -> int:
    args = _build_parser().parse_args()

    os.environ["L1_SYMBOL"] = args.symbol
    os.environ["L1_GATE_MODE"] = args.gate
    os.environ["L1_FEE_ROUNDTRIP"] = str(args.fee_roundtrip)
    os.environ["L1_DECISION_TICK_SECONDS"] = str(args.decision_tick_seconds)
    os.environ["L1_TRADES_WINDOW_HOURS"] = str(args.trades_window_hours)

    os.environ["THRESH_5M"] = str(args.thresh_5m)
    if args.seeds_5m_csv:
        os.environ["SEEDS_5M_CSV"] = args.seeds_5m_csv

    if args.trade_log_path:
        os.environ["L1_TRADE_LOG_PATH"] = args.trade_log_path

    if args.max_ticks and args.max_ticks > 0:
        max_ticks = int(args.max_ticks)
        max_run_seconds = None
    else:
        seconds = float(args.run_hours) * 3600.0
        max_ticks = int(seconds / float(args.decision_tick_seconds))
        if max_ticks < 1:
            max_ticks = 1
        max_run_seconds = seconds

    exit_code = int(
        run_l1_loop_step1234567(
            args.repo_root,
            max_ticks=max_ticks,
            max_run_seconds=max_run_seconds,
        )
    )

    trades_file = os.environ.get("L1_TRADE_LOG_PATH", "").strip()
    if trades_file == "":
        trades_file = "live_logs/trades_l1.jsonl"

    analysis_file = args.analysis_csv_out.strip()
    if analysis_file == "":
        analysis_file = _derive_analysis_csv_path(trades_file)

    if os.path.exists(trades_file) and os.path.getsize(trades_file) > 0:
        cmd = (
            f"python3 tools/analyze_trades.py {trades_file} "
            f"--csv-out {analysis_file} "
            f"--start-capital {args.start_capital}"
        )
        rc = os.system(cmd)
        if rc == 0:
            print(f"[AUTO] analysis written to {analysis_file}")
        else:
            print(f"[AUTO] analysis failed for {trades_file}")
    else:
        print(f"[AUTO] no trades found at {trades_file}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())











