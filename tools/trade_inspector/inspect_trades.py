#!/usr/bin/env python3
# tools/trade_inspector/inspect_trades.py
# Trade Inspector V1A.
# Read-only trade analysis tool.
# ASCII-only.

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_ARCHIVE_DIR = Path("live_logs/archive/P79A_pre_run_2026-06-10")
DEFAULT_OUTPUT_DIR = Path("data/processed/trade_inspector")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if not path.exists():
        raise FileNotFoundError(
            "Missing file: "
            + str(path)
            + "\nUse --archive-dir to point to an archive containing trades_l1.jsonl and execution_audit.jsonl."
        )

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


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
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
    if abs(pnl) < 1e-12:
        flags.append("flat_trade")

    return flags


def compute_quality_score(
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
) -> tuple[int, str, list[str], list[str]]:
    score = 50
    positives: list[str] = []
    negatives: list[str] = []

    pnl = safe_float(trade.get("pnl"), 0.0)
    duration = safe_float(trade.get("duration_sec"), 0.0)

    if pnl > 0:
        score += 20
        positives.append("positive_pnl")
    elif pnl < 0:
        score -= 25
        negatives.append("negative_pnl")
    else:
        positives.append("flat_pnl")

    if duration <= 0:
        score -= 20
        negatives.append("invalid_duration")
    elif duration <= 3600:
        score += 10
        positives.append("short_duration")
    elif duration <= 21600:
        score += 3
        positives.append("moderate_duration")
    else:
        score -= 8
        negatives.append("long_duration")

    if entry is None:
        score -= 20
        negatives.append("missing_entry_context")
    else:
        positives.append("entry_context_found")

    if exit_ is None:
        score -= 20
        negatives.append("missing_exit_context")
    else:
        positives.append("exit_context_found")

    exit_reason = safe_text(trade.get("exit_reason")).upper()
    audit_exit_reason = safe_text(exit_.get("reason") if exit_ else "").upper()

    if "TIME_STOP" in exit_reason or "TIME_STOP" in audit_exit_reason:
        score -= 5
        negatives.append("time_stop_exit")

    if "TP" in exit_reason or "TP" in audit_exit_reason:
        score += 10
        positives.append("take_profit_exit")

    if "SL" in exit_reason or "SL" in audit_exit_reason:
        score -= 15
        negatives.append("stop_loss_exit")

    flags = quality_flags(trade, entry, exit_)
    if "missing_entry_audit" in flags or "missing_exit_audit" in flags:
        score -= 15
    if "negative_duration" in flags:
        score -= 30
    if "very_long_trade" in flags:
        score -= 5

    score = max(0, min(100, int(score)))

    if score >= 85:
        quality_class = "excellent"
    elif score >= 70:
        quality_class = "good"
    elif score >= 50:
        quality_class = "neutral"
    elif score >= 30:
        quality_class = "weak"
    else:
        quality_class = "bad"

    return score, quality_class, positives, negatives


def build_ml_row(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
) -> dict[str, Any]:
    score, quality_class, positives, negatives = compute_quality_score(trade, entry, exit_)
    flags = quality_flags(trade, entry, exit_)

    pnl = safe_float(trade.get("pnl"), 0.0)
    duration = safe_float(trade.get("duration_sec"), 0.0)

    return {
        "trade_index": idx,
        "side": safe_text(trade.get("side")),
        "entry_timestamp_utc": safe_text(trade.get("entry_timestamp_utc")),
        "exit_timestamp_utc": safe_text(trade.get("exit_timestamp_utc")),
        "duration_sec": duration,
        "entry_price": safe_float(trade.get("entry_price"), 0.0),
        "exit_price": safe_float(trade.get("exit_price"), 0.0),
        "pnl": pnl,
        "pnl_pct": safe_float(trade.get("pnl_pct"), 0.0),
        "exit_reason": safe_text(trade.get("exit_reason")),
        "quality_score": score,
        "quality_class": quality_class,
        "is_winner": 1 if pnl > 0 else 0,
        "is_loser": 1 if pnl < 0 else 0,
        "is_flat": 1 if abs(pnl) < 1e-12 else 0,
        "has_entry_audit": 1 if entry is not None else 0,
        "has_exit_audit": 1 if exit_ is not None else 0,
        "entry_audit_reason": safe_text(entry.get("reason") if entry else ""),
        "entry_position_before": safe_text(entry.get("position_before") if entry else ""),
        "entry_position_after": safe_text(entry.get("position_after") if entry else ""),
        "exit_audit_reason": safe_text(exit_.get("reason") if exit_ else ""),
        "exit_position_after": safe_text(exit_.get("position_after") if exit_ else ""),
        "flags": "|".join(flags),
        "positive_factors": "|".join(positives),
        "negative_factors": "|".join(negatives),
    }


def print_kv(label: str, value: object) -> None:
    print(f"{label}: {value}")


def print_trade_report(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
) -> None:
    score, quality_class, positives, negatives = compute_quality_score(trade, entry, exit_)

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
    print("QUALITY ASSESSMENT")
    print("-" * 80)
    print_kv("quality_score", score)
    print_kv("quality_class", quality_class)
    print_kv("positive_factors", ",".join(positives) if positives else "none")
    print_kv("negative_factors", ",".join(negatives) if negatives else "none")

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
        score, quality_class, _, _ = compute_quality_score(trade, entry, exit_)
        flags = ",".join(quality_flags(trade, entry, exit_)) or "none"
        print(
            f"trade={idx} "
            f"side={safe_text(trade.get('side'))} "
            f"entry={safe_text(trade.get('entry_timestamp_utc'))} "
            f"exit={safe_text(trade.get('exit_timestamp_utc'))} "
            f"pnl={safe_text(trade.get('pnl'))} "
            f"duration_sec={safe_text(trade.get('duration_sec'))} "
            f"quality_score={score} "
            f"quality_class={quality_class} "
            f"flags={flags}"
        )


def print_summary(trades: list[dict[str, Any]], audit_rows: list[dict[str, Any]]) -> None:
    rows = []
    for idx, trade in enumerate(trades, start=1):
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        rows.append(build_ml_row(idx, trade, entry, exit_))

    class_counts: dict[str, int] = {}
    winners = 0
    losers = 0
    flats = 0
    total_pnl = 0.0

    for row in rows:
        cls = safe_text(row.get("quality_class"))
        class_counts[cls] = class_counts.get(cls, 0) + 1
        winners += safe_int(row.get("is_winner"), 0)
        losers += safe_int(row.get("is_loser"), 0)
        flats += safe_int(row.get("is_flat"), 0)
        total_pnl += safe_float(row.get("pnl"), 0.0)

    print("TRADE INSPECTOR SUMMARY")
    print("-" * 80)
    print_kv("trades", len(rows))
    print_kv("winners", winners)
    print_kv("losers", losers)
    print_kv("flats", flats)
    print_kv("total_pnl", total_pnl)
    print("")
    print("QUALITY CLASS COUNTS")
    print("-" * 80)
    for key in ["excellent", "good", "neutral", "weak", "bad"]:
        print_kv(key, class_counts.get(key, 0))


def export_ml_csv(
    trades: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for idx, trade in enumerate(trades, start=1):
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        rows.append(build_ml_row(idx, trade, entry, exit_))

    if not rows:
        raise ValueError("No trades to export.")

    fieldnames = list(rows[0].keys())

    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("ML CSV exported:", output_path)
    print("rows:", len(rows))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--trade-index", type=int)
    parser.add_argument("--best", type=int)
    parser.add_argument("--worst", type=int)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--export-ml-csv", default="")
    args = parser.parse_args()

    archive_dir = Path(args.archive_dir)

    trades_path = archive_dir / "trades_l1.jsonl"
    audit_path = archive_dir / "execution_audit.jsonl"

    trades = read_jsonl(trades_path)
    audit_rows = read_jsonl(audit_path)

    print("TRADE INSPECTOR V1A")
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

    if args.summary:
        print_summary(trades, audit_rows)
        return 0

    if args.export_ml_csv:
        export_ml_csv(trades, audit_rows, Path(args.export_ml_csv))
        return 0

    print("No selection provided.")
    print("Examples:")
    print("python3 tools/trade_inspector/inspect_trades.py --trade-index 1")
    print("python3 tools/trade_inspector/inspect_trades.py --worst 10")
    print("python3 tools/trade_inspector/inspect_trades.py --best 10")
    print("python3 tools/trade_inspector/inspect_trades.py --summary")
    print("python3 tools/trade_inspector/inspect_trades.py --export-ml-csv data/processed/trade_inspector/ml_v1a.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
