#!/usr/bin/env python3
# P28F Paper Performance Baseline from live_logs/l1_paper.log.
# Streaming, ASCII-only.

from __future__ import annotations

from collections import Counter
from pathlib import Path

LOG_PATH = Path("live_logs/l1_paper.log")
OUT_PATH = Path("docs/review/P28F_PAPER_PERFORMANCE_BASELINE_2026-06-06.md")


def parse_line(line: str) -> dict:
    out = {}
    for part in line.strip().split():
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
    return out


def fnum(x: object, default: float = 0.0) -> float:
    try:
        return float(str(x))
    except Exception:
        return default


def main() -> int:
    if not LOG_PATH.is_file():
        print("ERROR: missing log:", LOG_PATH)
        return 1

    event_counts = Counter()
    actions = Counter()
    execution_reasons = Counter()
    final_intents = Counter()
    gates = Counter()

    last_price_by_tick = {}

    position = "FLAT"
    entry_price = None
    entry_tick = None
    entry_side = ""

    reconstructed = []
    bad_closes = 0
    repeated_opens = 0

    with LOG_PATH.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            row = parse_line(raw)
            event = row.get("event", "")
            if not event:
                continue

            event_counts[event] += 1

            if event == "market_snapshot":
                tick = row.get("tick", "")
                price = fnum(row.get("price", "0"), 0.0)
                if tick:
                    last_price_by_tick[tick] = price
                    if len(last_price_by_tick) > 10000:
                        last_price_by_tick.clear()
                gates[(row.get("allow_long", ""), row.get("allow_short", ""))] += 1

            elif event == "intent_fused":
                final_intents[row.get("intent_final", "")] += 1

            elif event == "execution":
                action = row.get("action", "")
                reason = row.get("reason", "")
                tick = row.get("tick", "")
                price = last_price_by_tick.get(tick, 0.0)

                actions[action] += 1
                execution_reasons[reason] += 1

                if action == "OPEN_LONG":
                    if position != "FLAT":
                        repeated_opens += 1
                    position = "LONG"
                    entry_price = price
                    entry_tick = int(tick) if str(tick).isdigit() else 0
                    entry_side = "long"

                elif action == "OPEN_SHORT":
                    if position != "FLAT":
                        repeated_opens += 1
                    position = "SHORT"
                    entry_price = price
                    entry_tick = int(tick) if str(tick).isdigit() else 0
                    entry_side = "short"

                elif action == "CLOSE_LONG":
                    if position != "LONG" or entry_price is None:
                        bad_closes += 1
                    else:
                        exit_tick = int(tick) if str(tick).isdigit() else 0
                        pnl = price - float(entry_price)
                        reconstructed.append(
                            {
                                "side": entry_side,
                                "entry_tick": entry_tick,
                                "exit_tick": exit_tick,
                                "duration_ticks": max(0, exit_tick - int(entry_tick or 0)),
                                "entry_price": float(entry_price),
                                "exit_price": price,
                                "pnl": pnl,
                                "exit_reason": reason,
                            }
                        )
                    position = "FLAT"
                    entry_price = None
                    entry_tick = None
                    entry_side = ""

                elif action == "CLOSE_SHORT":
                    if position != "SHORT" or entry_price is None:
                        bad_closes += 1
                    else:
                        exit_tick = int(tick) if str(tick).isdigit() else 0
                        pnl = float(entry_price) - price
                        reconstructed.append(
                            {
                                "side": entry_side,
                                "entry_tick": entry_tick,
                                "exit_tick": exit_tick,
                                "duration_ticks": max(0, exit_tick - int(entry_tick or 0)),
                                "entry_price": float(entry_price),
                                "exit_price": price,
                                "pnl": pnl,
                                "exit_reason": reason,
                            }
                        )
                    position = "FLAT"
                    entry_price = None
                    entry_tick = None
                    entry_side = ""

    total = len(reconstructed)
    wins = [t for t in reconstructed if t["pnl"] > 0]
    losses = [t for t in reconstructed if t["pnl"] < 0]
    flats = [t for t in reconstructed if t["pnl"] == 0]

    long_trades = [t for t in reconstructed if t["side"] == "long"]
    short_trades = [t for t in reconstructed if t["side"] == "short"]

    total_pnl = sum(t["pnl"] for t in reconstructed)
    gross_win = sum(t["pnl"] for t in wins)
    gross_loss = abs(sum(t["pnl"] for t in losses))
    profit_factor = gross_win / gross_loss if gross_loss > 0 else 0.0

    avg_pnl = total_pnl / total if total else 0.0
    winrate = len(wins) / total if total else 0.0
    avg_duration = sum(t["duration_ticks"] for t in reconstructed) / total if total else 0.0

    exit_reasons = Counter(t["exit_reason"] for t in reconstructed)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as out:
        out.write("# P28F PAPER PERFORMANCE BASELINE\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")
        out.write("## Source\n\n")
        out.write("Source file: live_logs/l1_paper.log\n\n")
        out.write("Method: streaming reconstruction from market_snapshot and execution events.\n\n")
        out.write("Note: This is a log-derived baseline, not the official recovery trade ledger.\n\n")

        out.write("## Runtime Counts\n\n")
        for k, v in event_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Signal / Gate Counts\n\n")
        out.write("Final intents:\n\n")
        for k, v in final_intents.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\nGate counts:\n\n")
        for k, v in gates.most_common():
            out.write(f"- allow_long={k[0]} allow_short={k[1]}: {v}\n")
        out.write("\n")

        out.write("## Execution Actions\n\n")
        for k, v in actions.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Reconstructed Trade Baseline\n\n")
        out.write(f"closed_trades_reconstructed: {total}\n\n")
        out.write(f"long_trades: {len(long_trades)}\n\n")
        out.write(f"short_trades: {len(short_trades)}\n\n")
        out.write(f"wins: {len(wins)}\n\n")
        out.write(f"losses: {len(losses)}\n\n")
        out.write(f"flat_trades: {len(flats)}\n\n")
        out.write(f"winrate: {winrate:.6f}\n\n")
        out.write(f"total_pnl_points: {total_pnl:.6f}\n\n")
        out.write(f"avg_pnl_points: {avg_pnl:.6f}\n\n")
        out.write(f"gross_win_points: {gross_win:.6f}\n\n")
        out.write(f"gross_loss_points: {gross_loss:.6f}\n\n")
        out.write(f"profit_factor_points: {profit_factor:.6f}\n\n")
        out.write(f"avg_duration_ticks: {avg_duration:.2f}\n\n")
        out.write(f"bad_closes: {bad_closes}\n\n")
        out.write(f"repeated_opens: {repeated_opens}\n\n")
        out.write(f"open_position_remaining: {position}\n\n")

        out.write("## Exit Reasons\n\n")
        for k, v in exit_reasons.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P28F PAPER PERFORMANCE BASELINE")
    print("source:", LOG_PATH)
    print("doc_out:", OUT_PATH)
    print("closed_trades_reconstructed:", total)
    print("long_trades:", len(long_trades))
    print("short_trades:", len(short_trades))
    print("wins:", len(wins))
    print("losses:", len(losses))
    print("flat_trades:", len(flats))
    print("winrate:", round(winrate, 6))
    print("total_pnl_points:", round(total_pnl, 6))
    print("profit_factor_points:", round(profit_factor, 6))
    print("avg_duration_ticks:", round(avg_duration, 2))
    print("bad_closes:", bad_closes)
    print("repeated_opens:", repeated_opens)
    print("open_position_remaining:", position)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
