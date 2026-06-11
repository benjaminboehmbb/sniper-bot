#!/usr/bin/env python3
# tools/trade_inspector/inspect_trades.py
# Trade Inspector V1C.
# Read-only trade analysis tool.
# Human analysis + ML feature export.
# ASCII-only.

from __future__ import annotations

import argparse
import bisect
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_ARCHIVE_DIR = Path("live_logs/archive/P79A_pre_run_2026-06-10")
DEFAULT_MARKET_CSV = Path("data/l1_full_run.csv")


FUTURE_WINDOWS_MIN = {
    "15m": 15,
    "1h": 60,
    "4h": 240,
    "24h": 1440,
    "72h": 4320,
    "168h": 10080,
}


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


def parse_ts(value: object) -> datetime | None:
    s = safe_text(value).replace("_", " ")
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def ts_key(value: object) -> str:
    dt = parse_ts(value)
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


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


def market_timestamp(row: dict[str, Any]) -> str:
    for key in ("timestamp_utc", "timestamp", "open_time"):
        value = safe_text(row.get(key))
        if value:
            return ts_key(value)
    return ""


def market_price(row: dict[str, Any]) -> float:
    for key in ("close", "price", "close_price"):
        value = row.get(key)
        if value is not None and safe_text(value) != "":
            return safe_float(value, 0.0)
    return 0.0


def parse_market_rows(path: Path) -> tuple[list[str], list[float]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing market CSV: {path}")

    timestamps: list[str] = []
    prices: list[float] = []

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            ts = market_timestamp(row)
            price = market_price(row)
            if ts and price > 0:
                timestamps.append(ts)
                prices.append(price)

    return timestamps, prices


def find_matching_entry_exit(
    trade: dict[str, Any],
    audit_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    entry_key = ts_key(trade.get("entry_timestamp_utc"))
    exit_key = ts_key(trade.get("exit_timestamp_utc"))
    side = safe_text(trade.get("side")).lower()

    entry_match = None
    exit_match = None

    for row in audit_rows:
        event = safe_text(row.get("event"))
        row_key = ts_key(row.get("timestamp_utc"))
        row_side = safe_text(row.get("side")).lower()

        if event == "ENTRY_ACCEPTED" and row_key == entry_key:
            if side == "" or row_side == side:
                entry_match = row

        if event == "EXIT_EXECUTED" and row_key == exit_key:
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


def trade_pnl_from_price(side: str, entry_price: float, price: float) -> float:
    if side == "long":
        return price - entry_price
    if side == "short":
        return entry_price - price
    return 0.0


def calculate_trade_path(
    trade: dict[str, Any],
    timestamps: list[str],
    prices: list[float],
) -> dict[str, Any]:
    entry_key = ts_key(trade.get("entry_timestamp_utc"))
    exit_key = ts_key(trade.get("exit_timestamp_utc"))
    side = safe_text(trade.get("side")).lower()
    entry_price = safe_float(trade.get("entry_price"), 0.0)

    start = bisect.bisect_left(timestamps, entry_key)
    end = bisect.bisect_right(timestamps, exit_key)

    path_prices = prices[start:end]

    if not path_prices or entry_price <= 0:
        return {
            "bars_held": 0,
            "best_price_during_trade": 0.0,
            "worst_price_during_trade": 0.0,
            "mfe_abs": 0.0,
            "mfe_pct": 0.0,
            "mae_abs": 0.0,
            "mae_pct": 0.0,
            "path_available": 0,
        }

    if side == "long":
        best_price = max(path_prices)
        worst_price = min(path_prices)
    elif side == "short":
        best_price = min(path_prices)
        worst_price = max(path_prices)
    else:
        best_price = path_prices[-1]
        worst_price = path_prices[-1]

    mfe_abs = trade_pnl_from_price(side, entry_price, best_price)
    mae_abs = trade_pnl_from_price(side, entry_price, worst_price)

    return {
        "bars_held": len(path_prices),
        "best_price_during_trade": float(best_price),
        "worst_price_during_trade": float(worst_price),
        "mfe_abs": float(mfe_abs),
        "mfe_pct": float(mfe_abs / entry_price) if entry_price > 0 else 0.0,
        "mae_abs": float(mae_abs),
        "mae_pct": float(mae_abs / entry_price) if entry_price > 0 else 0.0,
        "path_available": 1,
    }


def calculate_counterfactuals(
    trade: dict[str, Any],
    timestamps: list[str],
    prices: list[float],
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    side = safe_text(trade.get("side")).lower()
    entry_price = safe_float(trade.get("entry_price"), 0.0)
    realized_pnl = safe_float(trade.get("pnl"), 0.0)

    exit_dt = parse_ts(trade.get("exit_timestamp_utc"))
    exit_key = ts_key(trade.get("exit_timestamp_utc"))

    if exit_dt is None or entry_price <= 0:
        for label in FUTURE_WINDOWS_MIN:
            result[f"cf_return_{label}_pct"] = 0.0
            result[f"cf_delta_vs_realized_{label}_pct"] = 0.0
            result[f"best_future_return_{label}_pct"] = 0.0
            result[f"exit_efficiency_{label}_pct"] = 0.0
            result[f"opportunity_loss_{label}_pct"] = 0.0
            result[f"counterfactual_available_{label}"] = 0
        return result

    exit_index = bisect.bisect_left(timestamps, exit_key)

    for label, minutes in FUTURE_WINDOWS_MIN.items():
        target_dt = exit_dt + timedelta(minutes=minutes)
        if target_dt.tzinfo is None:
            target_dt = target_dt.replace(tzinfo=timezone.utc)
        target_key = target_dt.isoformat()

        target_index = bisect.bisect_left(timestamps, target_key)

        if exit_index >= len(prices) or target_index >= len(prices):
            result[f"cf_return_{label}_pct"] = 0.0
            result[f"cf_delta_vs_realized_{label}_pct"] = 0.0
            result[f"best_future_return_{label}_pct"] = 0.0
            result[f"exit_efficiency_{label}_pct"] = 0.0
            result[f"opportunity_loss_{label}_pct"] = 0.0
            result[f"counterfactual_available_{label}"] = 0
            continue

        target_price = prices[target_index]
        cf_pnl = trade_pnl_from_price(side, entry_price, target_price)

        window_prices = prices[exit_index : target_index + 1]
        if not window_prices:
            best_future_pnl = cf_pnl
        else:
            if side == "long":
                best_future_price = max(window_prices)
            elif side == "short":
                best_future_price = min(window_prices)
            else:
                best_future_price = target_price
            best_future_pnl = trade_pnl_from_price(side, entry_price, best_future_price)

        cf_return_pct = cf_pnl / entry_price
        realized_pct = realized_pnl / entry_price
        best_future_return_pct = best_future_pnl / entry_price
        delta_vs_realized_pct = cf_return_pct - realized_pct

        opportunity_loss_pct = max(0.0, best_future_return_pct - realized_pct)

        if best_future_pnl > 0 and realized_pnl > 0:
            exit_efficiency_pct = max(0.0, min(1.0, realized_pnl / best_future_pnl))
        elif best_future_pnl <= 0 and realized_pnl >= best_future_pnl:
            exit_efficiency_pct = 1.0
        else:
            exit_efficiency_pct = 0.0

        result[f"cf_return_{label}_pct"] = cf_return_pct
        result[f"cf_delta_vs_realized_{label}_pct"] = delta_vs_realized_pct
        result[f"best_future_return_{label}_pct"] = best_future_return_pct
        result[f"exit_efficiency_{label}_pct"] = exit_efficiency_pct
        result[f"opportunity_loss_{label}_pct"] = opportunity_loss_pct
        result[f"counterfactual_available_{label}"] = 1

    return result


def interpretation_flags(path: dict[str, Any], cf: dict[str, Any]) -> dict[str, Any]:
    mfe_pct = safe_float(path.get("mfe_pct"), 0.0)
    mae_pct = safe_float(path.get("mae_pct"), 0.0)
    opp_24h = safe_float(cf.get("opportunity_loss_24h_pct"), 0.0)
    eff_24h = safe_float(cf.get("exit_efficiency_24h_pct"), 0.0)

    return {
        "high_mfe_flag": 1 if mfe_pct >= 0.01 else 0,
        "high_mae_flag": 1 if mae_pct <= -0.01 else 0,
        "early_exit_flag": 1 if opp_24h >= 0.01 else 0,
        "good_exit_flag": 1 if eff_24h >= 0.8 else 0,
        "exit_problem_flag": 1 if opp_24h >= 0.01 and eff_24h < 0.5 else 0,
        "entry_problem_flag": 1 if mfe_pct <= 0.0 and mae_pct < 0.0 else 0,
    }


def build_ml_row(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
    timestamps: list[str],
    prices: list[float],
) -> dict[str, Any]:
    score, quality_class, positives, negatives = compute_quality_score(trade, entry, exit_)
    flags = quality_flags(trade, entry, exit_)
    path = calculate_trade_path(trade, timestamps, prices)
    cf = calculate_counterfactuals(trade, timestamps, prices)
    interp = interpretation_flags(path, cf)

    pnl = safe_float(trade.get("pnl"), 0.0)
    duration = safe_float(trade.get("duration_sec"), 0.0)

    row: dict[str, Any] = {
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

    row.update(path)
    row.update(cf)
    row.update(interp)
    return row


def print_kv(label: str, value: object) -> None:
    print(f"{label}: {value}")


def print_trade_report(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
    timestamps: list[str],
    prices: list[float],
) -> None:
    row = build_ml_row(idx, trade, entry, exit_, timestamps, prices)
    score = row["quality_score"]
    quality_class = row["quality_class"]

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
    print_kv("positive_factors", row["positive_factors"] or "none")
    print_kv("negative_factors", row["negative_factors"] or "none")

    print("")
    print("TRADE PATH")
    print("-" * 80)
    for key in [
        "path_available",
        "bars_held",
        "best_price_during_trade",
        "worst_price_during_trade",
        "mfe_abs",
        "mfe_pct",
        "mae_abs",
        "mae_pct",
    ]:
        print_kv(key, row.get(key, ""))

    print("")
    print("COUNTERFACTUAL ANALYSIS")
    print("-" * 80)
    for label in FUTURE_WINDOWS_MIN:
        print_kv(f"cf_return_{label}_pct", row.get(f"cf_return_{label}_pct"))
        print_kv(f"cf_delta_vs_realized_{label}_pct", row.get(f"cf_delta_vs_realized_{label}_pct"))
        print_kv(f"best_future_return_{label}_pct", row.get(f"best_future_return_{label}_pct"))
        print_kv(f"exit_efficiency_{label}_pct", row.get(f"exit_efficiency_{label}_pct"))
        print_kv(f"opportunity_loss_{label}_pct", row.get(f"opportunity_loss_{label}_pct"))
        print("")

    print("INTERPRETATION FLAGS")
    print("-" * 80)
    for key in [
        "high_mfe_flag",
        "high_mae_flag",
        "early_exit_flag",
        "good_exit_flag",
        "entry_problem_flag",
        "exit_problem_flag",
    ]:
        print_kv(key, row.get(key, ""))

    print("")
    print("IMPROVEMENT OPTIONS")
    print("-" * 80)
    if safe_int(row.get("entry_problem_flag"), 0) == 1:
        print("P1: review entry filter")
        print("P2: review regime gate")
        print("P3: review signal confirmation")
    elif safe_int(row.get("exit_problem_flag"), 0) == 1:
        print("P1: review exit rule")
        print("P2: test longer hold variant")
        print("P3: test trailing exit")
    else:
        print("none")

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
    timestamps: list[str],
    prices: list[float],
) -> None:
    ranked = sorted(
        enumerate(trades, start=1),
        key=lambda item: safe_float(item[1].get("pnl"), 0.0),
        reverse=reverse,
    )

    for idx, trade in ranked[:count]:
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        row = build_ml_row(idx, trade, entry, exit_, timestamps, prices)
        print(
            f"trade={idx} "
            f"side={safe_text(trade.get('side'))} "
            f"entry={safe_text(trade.get('entry_timestamp_utc'))} "
            f"exit={safe_text(trade.get('exit_timestamp_utc'))} "
            f"pnl={safe_text(trade.get('pnl'))} "
            f"duration_sec={safe_text(trade.get('duration_sec'))} "
            f"quality_score={row['quality_score']} "
            f"quality_class={row['quality_class']} "
            f"mfe_pct={row['mfe_pct']} "
            f"mae_pct={row['mae_pct']} "
            f"opp_loss_24h={row['opportunity_loss_24h_pct']} "
            f"entry_problem={row['entry_problem_flag']} "
            f"exit_problem={row['exit_problem_flag']}"
        )


def build_rows(
    trades: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    timestamps: list[str],
    prices: list[float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, trade in enumerate(trades, start=1):
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        rows.append(build_ml_row(idx, trade, entry, exit_, timestamps, prices))
    return rows


def print_summary(
    trades: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    timestamps: list[str],
    prices: list[float],
) -> None:
    rows = build_rows(trades, audit_rows, timestamps, prices)

    class_counts: dict[str, int] = {}
    winners = 0
    losers = 0
    flats = 0
    total_pnl = 0.0
    exit_problem_count = 0
    entry_problem_count = 0

    for row in rows:
        cls = safe_text(row.get("quality_class"))
        class_counts[cls] = class_counts.get(cls, 0) + 1
        winners += safe_int(row.get("is_winner"), 0)
        losers += safe_int(row.get("is_loser"), 0)
        flats += safe_int(row.get("is_flat"), 0)
        total_pnl += safe_float(row.get("pnl"), 0.0)
        exit_problem_count += safe_int(row.get("exit_problem_flag"), 0)
        entry_problem_count += safe_int(row.get("entry_problem_flag"), 0)

    print("TRADE INSPECTOR SUMMARY")
    print("-" * 80)
    print_kv("trades", len(rows))
    print_kv("winners", winners)
    print_kv("losers", losers)
    print_kv("flats", flats)
    print_kv("total_pnl", total_pnl)
    print_kv("entry_problem_count", entry_problem_count)
    print_kv("exit_problem_count", exit_problem_count)
    print("")
    print("QUALITY CLASS COUNTS")
    print("-" * 80)
    for key in ["excellent", "good", "neutral", "weak", "bad"]:
        print_kv(key, class_counts.get(key, 0))


def export_ml_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

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
    parser.add_argument("--market-csv", default=str(DEFAULT_MARKET_CSV))
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
    timestamps, prices = parse_market_rows(Path(args.market_csv))

    print("TRADE INSPECTOR V1C")
    print("archive_dir:", archive_dir)
    print("trades:", len(trades))
    print("audit_events:", len(audit_rows))
    print("market_rows:", len(timestamps))
    print("")

    if args.trade_index is not None:
        if args.trade_index < 1 or args.trade_index > len(trades):
            raise SystemExit(f"Invalid trade index: {args.trade_index}")
        trade = trades[args.trade_index - 1]
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        print_trade_report(args.trade_index, trade, entry, exit_, timestamps, prices)
        return 0

    if args.best is not None:
        print("BEST TRADES")
        print("-" * 80)
        list_ranked(trades, audit_rows, args.best, True, timestamps, prices)
        return 0

    if args.worst is not None:
        print("WORST TRADES")
        print("-" * 80)
        list_ranked(trades, audit_rows, args.worst, False, timestamps, prices)
        return 0

    if args.summary:
        print_summary(trades, audit_rows, timestamps, prices)
        return 0

    if args.export_ml_csv:
        rows = build_rows(trades, audit_rows, timestamps, prices)
        export_ml_csv(rows, Path(args.export_ml_csv))
        return 0

    print("No selection provided.")
    print("Examples:")
    print("python3 tools/trade_inspector/inspect_trades.py --trade-index 1")
    print("python3 tools/trade_inspector/inspect_trades.py --worst 10")
    print("python3 tools/trade_inspector/inspect_trades.py --best 10")
    print("python3 tools/trade_inspector/inspect_trades.py --summary")
    print("python3 tools/trade_inspector/inspect_trades.py --export-ml-csv data/processed/trade_inspector/ml_v1c.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
