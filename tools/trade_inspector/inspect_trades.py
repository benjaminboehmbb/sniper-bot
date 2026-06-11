#!/usr/bin/env python3
# tools/trade_inspector/inspect_trades.py
# Read-only Trade Inspector V1.
# ASCII-only.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_ARCHIVE_DIR = Path("live_logs/archive/P79A_completed_2026-06-11")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            s = raw.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception as exc:
                raise ValueError(f"Bad JSON in {path} line {line_no}: {exc}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"Non-object JSON in {path} line {line_no}")
            rows.append(obj)

    return rows


def safe_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def find_matching_entry_exit(
    trade: dict[str, Any],
    audit_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    entry_ts = safe_text(trade.get("entry_timestamp_utc"))
    exit_ts = safe_text(trade.get("exit_timestamp_utc"))
    side = safe_text(trade.get("side")).lower()

    entry_match = None
    exit_match = None

    for row in audit_rows:
        event = safe_text(row.get("event"))
        row_ts = safe_text(row.get("timestamp_utc"))
        row_side = safe_text(row.get("side")).lower()

        if event == "ENTRY_ACCEPTED" and row_ts == entry_ts:
            if side == "" or row_side == side:
                entry_match = row

        if event == "EXIT_EXECUTED" and row_ts == exit_ts:
            exit_match = row

    return entry_match, exit_match


def print_kv(label: str, value: object) -> None:
    print(f"{label}: {value}")


def quality_flags(
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
) -> list[str]:
    flags: list[str] = []

    if entry is None:
        flags.append("missing_entry_audit")
    if exit_ is None:
        flags.append("missing_exit_audit")

    duration = safe_float(trade.get("duration_sec"), 0.0)
    pnl = safe_float(trade.get("pnl"), 0.0)

    if duration < 0:
        flags.append("negative_duration")
    if duration < 60:
        flags.append("very_short_trade")
    if duration > 86400:
        flags.append("very_long_trade")
    if pnl < 0:
        flags.append("losing_trade")

    return flags


def print_trade_report(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
) -> None:
    print("=" * 80)
    print(f"TRADE REPORT #{idx}")
    print("=" * 80)

    print("")
    print("TRADE SUMMARY")
    print("-" * 80)
    for key in [
        "side",
        "entry_timestamp_utc",
        "exit_timestamp_utc",
        "duration_sec",
        "entry_price",
        "exit_price",
        "pnl",
        "pnl_pct",
        "exit_reason",
    ]:
        print_kv(key, trade.get(key, ""))

    print("")
    print("ENTRY AUDIT CONTEXT")
    print("-" * 80)
    if entry is None:
        print("missing_entry_audit")
    else:
        for key in sorted(entry.keys()):
            print_kv(key, entry.get(key))

    print("")
    print("EXIT AUDIT CONTEXT")
    print("-" * 80)
    if exit_ is None:
        print("missing_exit_audit")
    else:
        for key in sorted(exit_.keys()):
            print_kv(key, exit_.get(key))

    print("")
    print("QUALITY FLAGS")
    print("-" * 80)
    flags = quality_flags(trade, entry, exit_)
    if flags:
        for flag in flags:
            print(flag)
    else:
        print("none")

    print("")


def list_ranked(
    trades: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    count: int,
    reverse: bool,
) -> None:
    ranked = sorted(
        enumerate(trades, start=1),
        key=lambda item: safe_float(item[1].get("pnl"), 0.0),
        reverse=reverse,
    )

    for idx, trade in ranked[:count]:
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        flags = ",".join(quality_flags(trade, entry, exit_)) or "none"
        print(
            f"trade={idx} "
            f"side={safe_text(trade.get('side'))} "
            f"entry={safe_text(trade.get('entry_timestamp_utc'))} "
            f"exit={safe_text(trade.get('exit_timestamp_utc'))} "
            f"pnl={safe_text(trade.get('pnl'))} "
            f"duration_sec={safe_text(trade.get('duration_sec'))} "
            f"flags={flags}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--trade-index", type=int)
    parser.add_argument("--best", type=int)
    parser.add_argument("--worst", type=int)
    args = parser.parse_args()

    archive_dir = Path(args.archive_dir)

    trades_path = archive_dir / "trades_l1.jsonl"
    audit_path = archive_dir / "execution_audit.jsonl"

    trades = read_jsonl(trades_path)
    audit_rows = read_jsonl(audit_path)

    print("TRADE INSPECTOR V1")
    print("archive_dir:", archive_dir)
    print("trades:", len(trades))
    print("audit_events:", len(audit_rows))
    print("")

    if args.trade_index is not None:
        if args.trade_index < 1 or args.trade_index > len(trades):
            raise SystemExit(f"Invalid trade index: {args.trade_index}")
        trade = trades[args.trade_index - 1]
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        print_trade_report(args.trade_index, trade, entry, exit_)
        return 0

    if args.best is not None:
        print("BEST TRADES")
        print("-" * 80)
        list_ranked(trades, audit_rows, args.best, reverse=True)
        return 0

    if args.worst is not None:
        print("WORST TRADES")
        print("-" * 80)
        list_ranked(trades, audit_rows, args.worst, reverse=False)
        return 0

    print("No selection provided.")
    print("Examples:")
    print("python3 tools/trade_inspector/inspect_trades.py --trade-index 1")
    print("python3 tools/trade_inspector/inspect_trades.py --worst 10")
    print("python3 tools/trade_inspector/inspect_trades.py --best 10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
