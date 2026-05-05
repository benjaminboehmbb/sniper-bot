#!/usr/bin/env python3
# scripts/analyze_regimes.py
# Regime and trade-quality analysis for Sniper-Bot L1 baseline.
# ASCII-only.
#
# Does not change strategy logic.

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


TIMESTAMP_CANDIDATES = (
    "timestamp_utc",
    "open_time",
    "timestamp",
    "time",
    "datetime",
)

REQUIRED_TRADE_COLUMNS = (
    "entry_timestamp_utc",
    "exit_timestamp_utc",
    "side",
    "entry_price",
    "exit_price",
    "pnl",
)

SIGNAL_COLUMNS = (
    "rsi_signal",
    "macd_signal",
    "bollinger_signal",
    "ma200_signal",
    "stoch_signal",
    "atr_signal",
    "ema50_signal",
    "adx_signal",
    "cci_signal",
    "mfi_signal",
    "obv_signal",
    "roc_signal",
)

OPTIONAL_MARKET_COLUMNS = (
    "open",
    "high",
    "low",
    "close",
    "volume",
    "regime_v1",
    "allow_long",
    "allow_short",
    "regime_v2",
)


def safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return float(s)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return int(float(s))
    except Exception:
        return default


def read_csv_header(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        try:
            return next(reader)
        except StopIteration:
            return []


def detect_timestamp_column(columns: Iterable[str]) -> str:
    cols = [safe_text(c) for c in columns]
    lower_map = {c.lower(): c for c in cols}

    for candidate in TIMESTAMP_CANDIDATES:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]

    raise RuntimeError(
        "No timestamp column found. Expected one of: "
        + ", ".join(TIMESTAMP_CANDIDATES)
    )


def require_columns(columns: Iterable[str], required: Iterable[str], label: str) -> None:
    existing = set(safe_text(c) for c in columns)
    missing = [c for c in required if c not in existing]
    if missing:
        raise RuntimeError(label + " missing required columns: " + ", ".join(missing))


def load_trades_jsonl(path: str) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    with open(path, "r", encoding="utf-8") as fh:
        for line_no, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if line == "":
                continue
            try:
                obj = json.loads(line)
            except Exception as exc:
                raise RuntimeError("Invalid JSON at line " + str(line_no) + ": " + str(exc))
            if not isinstance(obj, dict):
                raise RuntimeError("Invalid JSON object at line " + str(line_no))
            rows.append(obj)

    if not rows:
        raise RuntimeError("Trade log is empty: " + path)

    df = pd.DataFrame(rows)
    require_columns(df.columns, REQUIRED_TRADE_COLUMNS, "trade log")
    return df


def load_trades_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        raise RuntimeError("Trade CSV is empty: " + path)
    require_columns(df.columns, REQUIRED_TRADE_COLUMNS, "trade CSV")
    return df


def load_trades(trades_jsonl_path: str, trades_csv_path: str) -> pd.DataFrame:
    if trades_csv_path.strip() != "":
        trades = load_trades_csv(trades_csv_path)
    else:
        trades = load_trades_jsonl(trades_jsonl_path)

    trades = trades.copy()
    trades["entry_ts"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True, errors="coerce")
    trades["exit_ts"] = pd.to_datetime(trades["exit_timestamp_utc"], utc=True, errors="coerce")

    bad_entry = int(trades["entry_ts"].isna().sum())
    bad_exit = int(trades["exit_ts"].isna().sum())
    if bad_entry > 0 or bad_exit > 0:
        raise RuntimeError("Invalid trade timestamps. bad_entry=" + str(bad_entry) + " bad_exit=" + str(bad_exit))

    trades["entry_minute_key"] = trades["entry_ts"].dt.floor("min").map(lambda x: x.isoformat())
    trades["exit_minute_key"] = trades["exit_ts"].dt.floor("min").map(lambda x: x.isoformat())

    trades["pnl"] = trades["pnl"].map(lambda x: safe_float(x, 0.0))
    if "pnl_pct" in trades.columns:
        trades["pnl_pct"] = trades["pnl_pct"].map(lambda x: safe_float(x, 0.0))
    else:
        trades["pnl_pct"] = 0.0

    if "duration_sec" in trades.columns:
        trades["duration_sec"] = trades["duration_sec"].map(lambda x: safe_float(x, 0.0))
    else:
        trades["duration_sec"] = (trades["exit_ts"] - trades["entry_ts"]).dt.total_seconds()

    trades = trades.sort_values("exit_ts").reset_index(drop=True)
    trades["trade_index"] = list(range(1, len(trades) + 1))
    return trades


def market_use_columns(header: List[str], ts_col: str) -> List[str]:
    if "ma200_signal" not in header:
        raise RuntimeError("market CSV missing required column: ma200_signal")

    use_cols = [ts_col]

    for col in OPTIONAL_MARKET_COLUMNS:
        if col in header and col not in use_cols:
            use_cols.append(col)

    for col in SIGNAL_COLUMNS:
        if col in header and col not in use_cols:
            use_cols.append(col)

    return use_cols


def load_market_rows_for_trade_times(
    market_csv_path: str,
    needed_keys: set[str],
    chunk_size: int,
) -> Tuple[pd.DataFrame, str]:
    header = read_csv_header(market_csv_path)
    if not header:
        raise RuntimeError("Market CSV is empty: " + market_csv_path)

    ts_col = detect_timestamp_column(header)
    use_cols = market_use_columns(header, ts_col)
    collected: List[pd.DataFrame] = []

    for chunk in pd.read_csv(market_csv_path, usecols=use_cols, chunksize=int(chunk_size)):
        chunk["_ts"] = pd.to_datetime(chunk[ts_col], utc=True, errors="coerce")
        chunk["_minute_key"] = chunk["_ts"].dt.floor("min").map(
            lambda x: "" if pd.isna(x) else x.isoformat()
        )
        matched = chunk[chunk["_minute_key"].isin(needed_keys)].copy()
        if not matched.empty:
            collected.append(matched)

    if collected:
        return pd.concat(collected, ignore_index=True), ts_col

    return pd.DataFrame(columns=use_cols + ["_ts", "_minute_key"]), ts_col


def build_market_lookup(market_rows: pd.DataFrame) -> Dict[str, pd.Series]:
    lookup: Dict[str, pd.Series] = {}
    if market_rows.empty:
        return lookup

    deduped = market_rows.drop_duplicates(subset=["_minute_key"], keep="first")
    for _, row in deduped.iterrows():
        key = safe_text(row.get("_minute_key", ""), "")
        if key:
            lookup[key] = row

    return lookup


def classify_regime(row: pd.Series) -> str:
    ma200 = safe_int(row.get("ma200_signal", 0), 0)
    if ma200 > 0:
        return "bull"
    if ma200 < 0:
        return "bear"
    return "side"


def classify_atr(row: pd.Series) -> str:
    atr = safe_int(row.get("atr_signal", 0), 0)
    if atr == -1:
        return "bad_atr"
    if atr == 1:
        return "good_atr"
    return "neutral_atr"


def entry_score(row: pd.Series) -> int:
    return (
        safe_int(row.get("rsi_signal", 0), 0)
        + safe_int(row.get("bollinger_signal", 0), 0)
        + safe_int(row.get("stoch_signal", 0), 0)
        + safe_int(row.get("cci_signal", 0), 0)
    )


def score_bucket(score: int) -> str:
    s = int(score)
    if s <= -4:
        return "score_le_-4"
    if s == -3:
        return "score_-3"
    if s == -2:
        return "score_-2"
    if s == -1:
        return "score_-1"
    if s == 0:
        return "score_0"
    if s == 1:
        return "score_1"
    if s == 2:
        return "score_2"
    if s == 3:
        return "score_3"
    if s >= 4:
        return "score_ge_4"
    return "score_unknown"


def duration_bucket(duration_sec: float) -> str:
    d = float(duration_sec)
    if d < 15 * 60:
        return "lt_15m"
    if d < 60 * 60:
        return "15m_to_1h"
    if d < 4 * 60 * 60:
        return "1h_to_4h"
    if d < 12 * 60 * 60:
        return "4h_to_12h"
    if d < 24 * 60 * 60:
        return "12h_to_24h"
    return "gt_24h"


def add_market_fields(target: Dict[str, Any], row: pd.Series) -> None:
    target["mapping_status"] = "exact"
    target["market_timestamp_utc"] = safe_text(row.get("_ts", ""), "")
    target["regime"] = classify_regime(row)
    target["atr_quality"] = classify_atr(row)

    sc = entry_score(row)
    target["entry_score"] = int(sc)
    target["entry_score_bucket"] = score_bucket(sc)

    for col in OPTIONAL_MARKET_COLUMNS:
        if col in row.index:
            target["market_" + col] = row.get(col)

    for col in SIGNAL_COLUMNS:
        if col in row.index:
            target[col] = row.get(col)


def enrich_trades(trades: pd.DataFrame, market_rows: pd.DataFrame) -> pd.DataFrame:
    lookup = build_market_lookup(market_rows)
    rows: List[Dict[str, Any]] = []

    for _, trade in trades.iterrows():
        key = safe_text(trade.get("entry_minute_key", ""), "")
        market_row = lookup.get(key)

        item = trade.to_dict()
        if market_row is None:
            item["mapping_status"] = "missing"
            item["regime"] = "unknown"
            item["atr_quality"] = "unknown"
            item["entry_score"] = 0
            item["entry_score_bucket"] = "score_unknown"
        else:
            add_market_fields(item, market_row)

        item["is_win"] = int(float(item.get("pnl", 0.0)) > 0.0)
        item["duration_bucket"] = duration_bucket(float(item.get("duration_sec", 0.0)))

        rows.append(item)

    return pd.DataFrame(rows)


def profit_factor(pnls: List[float]) -> float:
    gross_profit = sum(x for x in pnls if x > 0.0)
    gross_loss = abs(sum(x for x in pnls if x < 0.0))

    if gross_loss == 0.0:
        if gross_profit > 0.0:
            return float("inf")
        return 0.0

    return gross_profit / gross_loss


def max_drawdown_from_pnls(pnls: List[float], start_capital: float) -> Tuple[float, float]:
    equity = float(start_capital)
    peak = equity
    max_dd_abs = 0.0
    max_dd_pct = 0.0

    for pnl in pnls:
        equity += float(pnl)
        if equity > peak:
            peak = equity

        dd_abs = peak - equity
        dd_pct = dd_abs / peak if peak > 0.0 else 0.0

        if dd_abs > max_dd_abs:
            max_dd_abs = dd_abs
        if dd_pct > max_dd_pct:
            max_dd_pct = dd_pct

    return max_dd_abs, max_dd_pct


def add_equity_columns(df: pd.DataFrame, start_capital: float) -> pd.DataFrame:
    out = df.sort_values("exit_ts").reset_index(drop=True).copy()

    equity = float(start_capital)
    peak = equity
    equities: List[float] = []
    peaks: List[float] = []
    dd_abs_list: List[float] = []
    dd_pct_list: List[float] = []

    for pnl in out["pnl"].tolist():
        equity += float(pnl)
        if equity > peak:
            peak = equity

        dd_abs = peak - equity
        dd_pct = dd_abs / peak if peak > 0.0 else 0.0

        equities.append(float(equity))
        peaks.append(float(peak))
        dd_abs_list.append(float(dd_abs))
        dd_pct_list.append(float(dd_pct))

    out["equity_after_trade"] = equities
    out["equity_peak"] = peaks
    out["drawdown_abs_after_trade"] = dd_abs_list
    out["drawdown_pct_after_trade"] = dd_pct_list

    return out


def summarize_group(df: pd.DataFrame, group_name: str, group_value: str, start_capital: float) -> Dict[str, Any]:
    pnls = [float(x) for x in df["pnl"].tolist()]
    wins = [x for x in pnls if x > 0.0]
    losses = [x for x in pnls if x < 0.0]
    total_pnl = sum(pnls)
    max_dd_abs, max_dd_pct = max_drawdown_from_pnls(pnls, start_capital)

    return {
        "group_name": group_name,
        "group_value": group_value,
        "num_trades": int(len(pnls)),
        "num_wins": int(len(wins)),
        "num_losses": int(len(losses)),
        "winrate": float(len(wins) / len(pnls)) if pnls else 0.0,
        "profit_factor": float(profit_factor(pnls)),
        "total_pnl": float(total_pnl),
        "return_pct": float(total_pnl / start_capital) if start_capital > 0.0 else 0.0,
        "avg_pnl": float(total_pnl / len(pnls)) if pnls else 0.0,
        "avg_duration_sec": float(df["duration_sec"].mean()) if "duration_sec" in df.columns and len(df) else 0.0,
        "max_drawdown_abs": float(max_dd_abs),
        "max_drawdown_pct": float(max_dd_pct),
    }


def add_group_summaries(rows: List[Dict[str, Any]], df: pd.DataFrame, col: str, start_capital: float) -> None:
    if col not in df.columns:
        return
    for value, group in df.groupby(col, dropna=False):
        rows.append(summarize_group(df=group, group_name=col, group_value=safe_text(value, "unknown"), start_capital=start_capital))


def add_pair_group_summaries(rows: List[Dict[str, Any]], df: pd.DataFrame, col_a: str, col_b: str, start_capital: float) -> None:
    if col_a not in df.columns or col_b not in df.columns:
        return
    for (a, b), group in df.groupby([col_a, col_b], dropna=False):
        value = safe_text(a, "unknown") + "_" + safe_text(b, "unknown")
        rows.append(summarize_group(df=group, group_name=col_a + "_" + col_b, group_value=value, start_capital=start_capital))


def build_summary(enriched: pd.DataFrame, start_capital: float) -> pd.DataFrame:
    mapped = enriched[enriched["mapping_status"] == "exact"].copy()
    rows: List[Dict[str, Any]] = []

    rows.append(summarize_group(mapped, "all_mapped", "all_mapped", start_capital))

    for col in (
        "regime",
        "atr_quality",
        "side",
        "entry_score_bucket",
        "duration_bucket",
        "exit_reason",
    ):
        add_group_summaries(rows, mapped, col, start_capital)

    for col_a, col_b in (
        ("regime", "side"),
        ("atr_quality", "side"),
        ("atr_quality", "entry_score_bucket"),
        ("side", "entry_score_bucket"),
        ("duration_bucket", "side"),
    ):
        add_pair_group_summaries(rows, mapped, col_a, col_b, start_capital)

    return pd.DataFrame(rows)


def build_dd_events(enriched: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "trade_index",
        "side",
        "regime",
        "atr_quality",
        "entry_score",
        "entry_score_bucket",
        "duration_bucket",
        "entry_timestamp_utc",
        "exit_timestamp_utc",
        "exit_reason",
        "pnl",
        "equity_after_trade",
        "drawdown_abs_after_trade",
        "drawdown_pct_after_trade",
    ]

    existing = [c for c in cols if c in enriched.columns]
    dd = enriched.sort_values("drawdown_pct_after_trade", ascending=False).head(30)
    return dd[existing].copy()


def write_csv(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="analyze_regimes.py")

    p.add_argument("--market-csv-path", default="data/l1_full_run.csv")
    p.add_argument("--trades-jsonl-path", default="live_logs/trades_l1.jsonl")
    p.add_argument("--trades-csv-path", default="")
    p.add_argument("--out-dir", default="reports/regime_analysis")
    p.add_argument("--run-label", default="baseline")
    p.add_argument("--start-capital", type=float, default=10000.0)
    p.add_argument("--chunk-size", type=int, default=250000)
    p.add_argument("--allow-missing-mapping", action="store_true")

    return p


def main() -> int:
    args = build_parser().parse_args()

    if not os.path.isfile(args.market_csv_path):
        raise RuntimeError("Market CSV not found: " + args.market_csv_path)

    if args.trades_csv_path.strip():
        if not os.path.isfile(args.trades_csv_path):
            raise RuntimeError("Trade CSV not found: " + args.trades_csv_path)
    else:
        if not os.path.isfile(args.trades_jsonl_path):
            raise RuntimeError("Trade JSONL not found: " + args.trades_jsonl_path)

    trades = load_trades(args.trades_jsonl_path, args.trades_csv_path)
    needed_keys = set(str(x) for x in trades["entry_minute_key"].tolist() if str(x) != "")

    market_rows, ts_col = load_market_rows_for_trade_times(
        market_csv_path=args.market_csv_path,
        needed_keys=needed_keys,
        chunk_size=int(args.chunk_size),
    )

    enriched = enrich_trades(trades, market_rows)
    mapped_count = int((enriched["mapping_status"] == "exact").sum())
    missing_count = int((enriched["mapping_status"] == "missing").sum())

    if missing_count > 0 and not bool(args.allow_missing_mapping):
        raise RuntimeError(
            "Trade-to-market mapping failed for "
            + str(missing_count)
            + " trades out of "
            + str(len(enriched))
        )

    enriched = add_equity_columns(enriched, float(args.start_capital))
    summary = build_summary(enriched, float(args.start_capital))
    dd_events = build_dd_events(enriched)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = str(out_dir / ("regime_summary_" + args.run_label + ".csv"))
    enriched_path = str(out_dir / ("regime_trades_enriched_" + args.run_label + ".csv"))
    dd_path = str(out_dir / ("regime_dd_events_" + args.run_label + ".csv"))

    write_csv(summary, summary_path)
    write_csv(enriched, enriched_path)
    write_csv(dd_events, dd_path)

    print("market_timestamp_column: " + ts_col)
    print("trades_total: " + str(len(enriched)))
    print("trades_mapped: " + str(mapped_count))
    print("trades_missing_mapping: " + str(missing_count))
    print("")
    print("REGIME ANALYSIS COMPLETE")
    print("summary_csv: " + summary_path)
    print("enriched_trades_csv: " + enriched_path)
    print("dd_events_csv: " + dd_path)
    print("")

    view_cols = [
        "group_name",
        "group_value",
        "num_trades",
        "winrate",
        "profit_factor",
        "return_pct",
        "max_drawdown_pct",
        "total_pnl",
    ]
    view_cols = [c for c in view_cols if c in summary.columns]
    print(summary[view_cols].to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())