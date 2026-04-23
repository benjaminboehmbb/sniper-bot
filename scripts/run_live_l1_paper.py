#!/usr/bin/env python3
# scripts/run_live_l1_paper.py
#
# Paper runner for L1 loop
# + AUTO ANALYSIS AFTER RUN
# + respects L1_TRADE_LOG_PATH
# + optional CSV offset support via temporary shifted CSV
#
# ASCII-only

import argparse
import csv
import os
from pathlib import Path

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
        "--market-csv-path",
        default="",
        help="optional input market CSV path (default: use loop/env default)",
    )
    p.add_argument(
        "--offset",
        type=int,
        default=0,
        help="optional row offset into market CSV (default: 0)",
    )

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


def _default_market_csv_path(repo_root: str) -> str:
    env_path = os.environ.get("L1_MARKET_CSV_PATH", "").strip()
    if env_path != "":
        return env_path
    return os.path.join(repo_root, "data", "l1_paper_short_gate_test.csv")


def _resolve_market_csv_path(repo_root: str, cli_path: str) -> str:
    if cli_path.strip() != "":
        if os.path.isabs(cli_path):
            return cli_path
        return os.path.join(repo_root, cli_path)
    return _default_market_csv_path(repo_root)


def _build_offset_csv(
    *,
    src_csv: str,
    dst_csv: str,
    offset: int,
) -> tuple[int, int]:
    """
    Returns:
        (input_rows_without_header, output_rows_without_header)
    """
    offset = max(0, int(offset))

    os.makedirs(os.path.dirname(dst_csv), exist_ok=True)

    input_rows = 0
    output_rows = 0

    with open(src_csv, "r", encoding="utf-8", newline="") as fin:
        reader = csv.reader(fin)
        try:
            header = next(reader)
        except StopIteration:
            raise RuntimeError(f"empty CSV: {src_csv}")

        with open(dst_csv, "w", encoding="utf-8", newline="") as fout:
            writer = csv.writer(fout)
            writer.writerow(header)

            for idx, row in enumerate(reader):
                input_rows += 1
                if idx < offset:
                    continue
                writer.writerow(row)
                output_rows += 1

    return (input_rows, output_rows)


def main() -> int:
    args = _build_parser().parse_args()
    repo_root = os.path.abspath(args.repo_root)

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

    resolved_market_csv = _resolve_market_csv_path(repo_root, args.market_csv_path)

    if args.offset > 0:
        offset_csv = os.path.join(
            repo_root,
            "live_logs",
            f"market_offset_{int(args.offset)}.csv",
        )
        in_rows, out_rows = _build_offset_csv(
            src_csv=resolved_market_csv,
            dst_csv=offset_csv,
            offset=int(args.offset),
        )
        os.environ["L1_MARKET_CSV_PATH"] = offset_csv
        print(
            f"[OFFSET] source={resolved_market_csv} offset={int(args.offset)} "
            f"input_rows={in_rows} output_rows={out_rows} shifted_csv={offset_csv}"
        )
    else:
        os.environ["L1_MARKET_CSV_PATH"] = resolved_market_csv

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
            repo_root,
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











