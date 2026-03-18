#!/usr/bin/env python3
# tools/analyze_trades.py
# ASCII-only

import argparse
import csv
import json
import math
from statistics import mean, pstdev

def load_trades(path):
    trades = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                trades.append(json.loads(line))
    return trades

def compute_equity(trades, start_capital):
    rows = []

    equity = start_capital
    peak = start_capital

    max_dd_abs = 0.0
    max_dd_pct = 0.0

    for i, t in enumerate(trades, start=1):
        pnl = float(t.get("pnl", 0.0))

        equity += pnl

        if equity > peak:
            peak = equity

        dd_abs = peak - equity
        dd_pct = dd_abs / peak if peak > 0 else 0.0

        if dd_abs > max_dd_abs:
            max_dd_abs = dd_abs

        if dd_pct > max_dd_pct:
            max_dd_pct = dd_pct

        row = dict(t)
        row["trade_index"] = i
        row["equity"] = equity
        row["drawdown_abs"] = dd_abs
        row["drawdown_pct"] = dd_pct

        rows.append(row)

    return rows, max_dd_abs, max_dd_pct

def sharpe_like(pcts):
    if len(pcts) < 2:
        return 0.0
    mu = mean(pcts)
    sigma = pstdev(pcts)
    if sigma == 0:
        return 0.0
    return (mu / sigma) * math.sqrt(len(pcts))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("trades")
    p.add_argument("--csv-out", default="")
    p.add_argument("--start-capital", type=float, default=10000.0)
    args = p.parse_args()

    trades = load_trades(args.trades)

    if not trades:
        print("No trades")
        return

    rows, max_dd_abs, max_dd_pct = compute_equity(trades, args.start_capital)

    pnls = [t["pnl"] for t in trades]
    pcts = [t["pnl_pct"] for t in trades]
    durations = [t["duration_sec"] for t in trades]

    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]

    total_pnl = sum(pnls)
    winrate = len(wins) / len(pnls)
    avg_pnl = mean(pnls)
    avg_win = mean(wins) if wins else 0.0
    avg_loss = mean(losses) if losses else 0.0

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    final_equity = rows[-1]["equity"]

    print("---- TRADE ANALYSIS ----")
    print(f"start_capital: {args.start_capital}")
    print(f"final_equity: {final_equity:.2f}")
    print(f"total_pnl: {total_pnl:.2f}")
    print(f"return_pct: {(final_equity/args.start_capital - 1):.4f}")
    print(f"num_trades: {len(trades)}")
    print(f"winrate: {winrate:.4f}")
    print(f"profit_factor: {profit_factor:.4f}")
    print(f"avg_pnl: {avg_pnl:.4f}")
    print(f"avg_duration_sec: {mean(durations):.2f}")
    print(f"max_drawdown_abs: {max_dd_abs:.2f}")
    print(f"max_drawdown_pct: {max_dd_pct:.4f}")
    print(f"sharpe_like: {sharpe_like(pcts):.4f}")

    if args.csv_out:
        with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"csv_out: {args.csv_out}")

if __name__ == "__main__":
    main()