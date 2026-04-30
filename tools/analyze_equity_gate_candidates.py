#!/usr/bin/env python3
# tools/analyze_equity_gate_candidates.py
# Offline analysis for equity-gate candidates.
# ASCII-only.

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Trade:
    idx: int
    side: str
    pnl: float
    entry_timestamp_utc: str
    exit_timestamp_utc: str
    exit_reason: str


@dataclass
class Metrics:
    name: str
    start_capital: float
    final_equity: float
    total_pnl: float
    return_pct: float
    num_trades: int
    winrate: float
    profit_factor: float
    max_drawdown_abs: float
    max_drawdown_pct: float
    skipped_trades: int


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return float(s)
    except Exception:
        return default


def _safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def load_trades(path: Path) -> list[Trade]:
    trades: list[Trade] = []

    with path.open("r", encoding="utf-8") as fh:
        for idx, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception:
                continue

            if not isinstance(obj, dict):
                continue

            trades.append(
                Trade(
                    idx=idx,
                    side=_safe_text(obj.get("side"), ""),
                    pnl=_safe_float(obj.get("pnl"), 0.0),
                    entry_timestamp_utc=_safe_text(obj.get("entry_timestamp_utc"), ""),
                    exit_timestamp_utc=_safe_text(obj.get("exit_timestamp_utc"), ""),
                    exit_reason=_safe_text(obj.get("exit_reason"), ""),
                )
            )

    return trades


def compute_metrics(
    *,
    name: str,
    trades: list[Trade],
    start_capital: float,
    skipped_trades: int = 0,
) -> Metrics:
    equity = float(start_capital)
    peak = float(start_capital)
    max_dd_abs = 0.0
    max_dd_pct = 0.0

    wins = 0
    losses = 0
    gross_profit = 0.0
    gross_loss = 0.0

    for trade in trades:
        pnl = float(trade.pnl)
        equity += pnl

        if pnl > 0:
            wins += 1
            gross_profit += pnl
        elif pnl < 0:
            losses += 1
            gross_loss += pnl

        if equity > peak:
            peak = equity

        dd_abs = peak - equity
        dd_pct = dd_abs / peak if peak > 0 else 0.0

        if dd_abs > max_dd_abs:
            max_dd_abs = dd_abs
        if dd_pct > max_dd_pct:
            max_dd_pct = dd_pct

    total_pnl = equity - start_capital
    num_trades = len(trades)
    winrate = wins / num_trades if num_trades > 0 else 0.0

    if gross_loss < 0:
        profit_factor = gross_profit / abs(gross_loss)
    else:
        profit_factor = math.inf if gross_profit > 0 else 0.0

    return Metrics(
        name=name,
        start_capital=float(start_capital),
        final_equity=float(equity),
        total_pnl=float(total_pnl),
        return_pct=float(total_pnl / start_capital if start_capital > 0 else 0.0),
        num_trades=int(num_trades),
        winrate=float(winrate),
        profit_factor=float(profit_factor),
        max_drawdown_abs=float(max_dd_abs),
        max_drawdown_pct=float(max_dd_pct),
        skipped_trades=int(skipped_trades),
    )


def simulate_dd_pause_gate(
    *,
    trades: list[Trade],
    start_capital: float,
    block_dd_pct: float,
    pause_trades: int,
) -> tuple[list[Trade], int]:
    kept: list[Trade] = []

    equity = float(start_capital)
    peak = float(start_capital)
    pause_remaining = 0
    skipped = 0

    for trade in trades:
        if pause_remaining > 0:
            pause_remaining -= 1
            skipped += 1
            continue

        kept.append(trade)
        equity += float(trade.pnl)

        if equity > peak:
            peak = equity

        dd_pct = (peak - equity) / peak if peak > 0 else 0.0

        if dd_pct >= block_dd_pct:
            pause_remaining = int(pause_trades)
            peak = equity

    return kept, skipped


def simulate_loss_cluster_gate(
    *,
    trades: list[Trade],
    loss_count: int,
    lookback: int,
    pause_trades: int,
) -> tuple[list[Trade], int]:
    kept: list[Trade] = []
    recent_pnls: list[float] = []
    pause_remaining = 0
    skipped = 0

    for trade in trades:
        if pause_remaining > 0:
            pause_remaining -= 1
            skipped += 1
            continue

        kept.append(trade)
        recent_pnls.append(float(trade.pnl))

        if len(recent_pnls) > lookback:
            recent_pnls.pop(0)

        losses = sum(1 for pnl in recent_pnls if pnl < 0.0)

        if len(recent_pnls) >= lookback and losses >= loss_count:
            pause_remaining = int(pause_trades)
            recent_pnls = []

    return kept, skipped


def write_csv(path: Path, rows: list[Metrics]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "name",
        "start_capital",
        "final_equity",
        "total_pnl",
        "return_pct",
        "num_trades",
        "winrate",
        "profit_factor",
        "max_drawdown_abs",
        "max_drawdown_pct",
        "skipped_trades",
    ]

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()

        for m in rows:
            writer.writerow(
                {
                    "name": m.name,
                    "start_capital": f"{m.start_capital:.2f}",
                    "final_equity": f"{m.final_equity:.2f}",
                    "total_pnl": f"{m.total_pnl:.2f}",
                    "return_pct": f"{m.return_pct:.6f}",
                    "num_trades": m.num_trades,
                    "winrate": f"{m.winrate:.6f}",
                    "profit_factor": (
                        "inf" if math.isinf(m.profit_factor) else f"{m.profit_factor:.6f}"
                    ),
                    "max_drawdown_abs": f"{m.max_drawdown_abs:.2f}",
                    "max_drawdown_pct": f"{m.max_drawdown_pct:.6f}",
                    "skipped_trades": m.skipped_trades,
                }
            )


def print_metrics_table(rows: list[Metrics]) -> None:
    print("")
    print("---- EQUITY GATE CANDIDATE ANALYSIS ----")
    print(
        "{:<34} {:>9} {:>8} {:>8} {:>8} {:>9} {:>8}".format(
            "name",
            "return",
            "trades",
            "PF",
            "DD",
            "skipped",
            "winrate",
        )
    )
    print("-" * 92)

    for m in rows:
        pf_txt = "inf" if math.isinf(m.profit_factor) else f"{m.profit_factor:.3f}"
        print(
            "{:<34} {:>8.2f}% {:>8} {:>8} {:>7.2f}% {:>9} {:>7.2f}%".format(
                m.name[:34],
                m.return_pct * 100.0,
                m.num_trades,
                pf_txt,
                m.max_drawdown_pct * 100.0,
                m.skipped_trades,
                m.winrate * 100.0,
            )
        )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("trades_jsonl", help="Path to trades_l1.jsonl")
    p.add_argument("--start-capital", type=float, default=10000.0)
    p.add_argument("--csv-out", default="live_logs/equity_gate_candidate_analysis.csv")
    return p


def main() -> int:
    args = build_parser().parse_args()

    trades_path = Path(args.trades_jsonl)
    if not trades_path.is_file():
        raise FileNotFoundError(f"trades file not found: {trades_path}")

    trades = load_trades(trades_path)
    if not trades:
        raise RuntimeError(f"no valid trades loaded from: {trades_path}")

    rows: list[Metrics] = []

    rows.append(
        compute_metrics(
            name="baseline_no_gate",
            trades=trades,
            start_capital=args.start_capital,
            skipped_trades=0,
        )
    )

    dd_tests = [
        (0.05, 25),
        (0.05, 50),
        (0.05, 100),
        (0.08, 25),
        (0.08, 50),
        (0.08, 100),
        (0.10, 25),
        (0.10, 50),
        (0.10, 100),
    ]

    for block_dd, pause_trades in dd_tests:
        kept, skipped = simulate_dd_pause_gate(
            trades=trades,
            start_capital=args.start_capital,
            block_dd_pct=block_dd,
            pause_trades=pause_trades,
        )
        rows.append(
            compute_metrics(
                name=f"dd_gate_{int(block_dd * 100)}pct_pause_{pause_trades}tr",
                trades=kept,
                start_capital=args.start_capital,
                skipped_trades=skipped,
            )
        )

    cluster_tests = [
        (3, 5, 25),
        (3, 5, 50),
        (3, 5, 100),
        (4, 8, 25),
        (4, 8, 50),
        (4, 8, 100),
        (5, 10, 25),
        (5, 10, 50),
        (5, 10, 100),
    ]

    for loss_count, lookback, pause_trades in cluster_tests:
        kept, skipped = simulate_loss_cluster_gate(
            trades=trades,
            loss_count=loss_count,
            lookback=lookback,
            pause_trades=pause_trades,
        )
        rows.append(
            compute_metrics(
                name=f"loss_gate_{loss_count}of{lookback}_pause_{pause_trades}tr",
                trades=kept,
                start_capital=args.start_capital,
                skipped_trades=skipped,
            )
        )

    rows_sorted = sorted(
        rows,
        key=lambda m: (
            m.max_drawdown_pct,
            -m.profit_factor if not math.isinf(m.profit_factor) else -9999.0,
            -m.return_pct,
        ),
    )

    print_metrics_table(rows_sorted)

    csv_out = Path(args.csv_out)
    write_csv(csv_out, rows_sorted)

    print("")
    print(f"[OK] wrote analysis CSV: {csv_out}")
    print("")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())