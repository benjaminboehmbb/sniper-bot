"""Regime context, trade identity, family, and ML-row assembly."""

from __future__ import annotations

from datetime import timezone
from typing import Any

if __package__:
    from .inspection_primitives import parse_ts, safe_float, safe_int, safe_text, ts_key
    from .path_diagnosis import (
        calculate_counterfactuals,
        calculate_trade_path,
        compute_confidence_layer,
        compute_diagnosis,
        compute_quality_score,
        interpretation_flags,
        quality_flags,
    )
else:
    from inspection_primitives import parse_ts, safe_float, safe_int, safe_text, ts_key
    from path_diagnosis import (
        calculate_counterfactuals,
        calculate_trade_path,
        compute_confidence_layer,
        compute_diagnosis,
        compute_quality_score,
        interpretation_flags,
        quality_flags,
    )


__all__ = [
    "find_matching_entry_exit",
    "build_regime_index",
    "extract_regime_features",
    "compact_trade_time",
    "chart_time",
    "build_trade_id",
    "build_trade_family",
    "build_ml_row",
    "build_rows",
]


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


def build_regime_index(regime_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}

    for row in regime_rows:
        key = ts_key(row.get("timestamp_utc"))
        if key:
            index[key] = row

    return index


def extract_regime_features(
    trade: dict[str, Any],
    regime_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    entry_key = ts_key(trade.get("entry_timestamp_utc"))
    exit_key = ts_key(trade.get("exit_timestamp_utc"))

    entry_regime = regime_index.get(entry_key, {})
    exit_regime = regime_index.get(exit_key, {})

    entry_label = safe_text(entry_regime.get("regime_label"))
    exit_label = safe_text(exit_regime.get("regime_label"))

    entry_risk = safe_text(entry_regime.get("risk_label"))
    exit_risk = safe_text(exit_regime.get("risk_label"))

    entry_score = safe_int(entry_regime.get("entry_score"), 0)
    exit_score = safe_int(exit_regime.get("entry_score"), 0)

    side = safe_text(trade.get("side")).lower()

    regime_aligned = 0
    if side == "long" and entry_label == "bull":
        regime_aligned = 1
    elif side == "short" and entry_label == "bear":
        regime_aligned = 1
    elif entry_label:
        regime_aligned = -1

    risk_good = 1 if entry_risk == "good_atr" else 0
    regime_changed = 1 if entry_label and exit_label and entry_label != exit_label else 0

    return {
        "entry_regime_label": entry_label,
        "exit_regime_label": exit_label,
        "entry_risk_label": entry_risk,
        "exit_risk_label": exit_risk,
        "entry_score_at_entry": entry_score,
        "entry_score_at_exit": exit_score,
        "entry_ma200_signal": safe_int(entry_regime.get("ma200_signal"), 0),
        "entry_mfi_signal": safe_int(entry_regime.get("mfi_signal"), 0),
        "entry_atr_signal": safe_int(entry_regime.get("atr_signal"), 0),
        "exit_ma200_signal": safe_int(exit_regime.get("ma200_signal"), 0),
        "exit_mfi_signal": safe_int(exit_regime.get("mfi_signal"), 0),
        "exit_atr_signal": safe_int(exit_regime.get("atr_signal"), 0),
        "regime_aligned": regime_aligned,
        "risk_good_at_entry": risk_good,
        "regime_changed_during_trade": regime_changed,
        "has_entry_regime_context": 1 if entry_regime else 0,
        "has_exit_regime_context": 1 if exit_regime else 0,
    }


def compact_trade_time(value: object) -> str:
    dt = parse_ts(value)
    if dt is None:
        return "UNKNOWN_TIME"
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y%m%d_%H%M%S")


def chart_time(value: object) -> str:
    dt = parse_ts(value)
    if dt is None:
        return ""
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def build_trade_id(trade: dict[str, Any]) -> str:
    entry = compact_trade_time(trade.get("entry_timestamp_utc"))
    side = safe_text(trade.get("side")).upper() or "UNKNOWN_SIDE"
    symbol = safe_text(trade.get("symbol")) or "BTCUSDT"
    return f"T_{entry}_{side}_{symbol}"


def build_trade_family(row: dict[str, Any]) -> dict[str, Any]:
    regime = safe_text(row.get("entry_regime_label")) or "unknown_regime"
    risk = safe_text(row.get("entry_risk_label")) or "unknown_risk"
    root = safe_text(row.get("root_cause")) or "unknown_cause"
    side = safe_text(row.get("side")) or "unknown_side"

    regime_changed = safe_int(row.get("regime_changed_during_trade"), 0)
    aligned = safe_int(row.get("regime_aligned"), 0)

    family_parts = [side, regime, risk, root]

    if regime_changed == 1:
        family_parts.append("regime_flip")

    if aligned == 1:
        family_parts.append("aligned")
    elif aligned == -1:
        family_parts.append("counter_regime")
    else:
        family_parts.append("neutral_regime")

    trade_family = "_".join(family_parts)

    if root == "early_exit" and risk == "bad_atr":
        family_group = "exit_risk_trap"
    elif root == "early_exit" and regime_changed == 1:
        family_group = "exit_after_regime_flip"
    elif risk == "good_atr" and aligned == 1:
        family_group = "aligned_good_risk"
    elif regime == "chop":
        family_group = "chop_context"
    elif aligned == -1:
        family_group = "counter_regime"
    else:
        family_group = "general"

    return {
        "trade_family": trade_family,
        "trade_family_group": family_group,
    }


def build_ml_row(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
    audit_rows: list[dict[str, Any]],
    regime_index: dict[str, dict[str, Any]],
    timestamps: list[str],
    prices: list[float],
    label_map: dict[str, str],
) -> dict[str, Any]:
    quality_score, quality_class, positives, negatives = compute_quality_score(trade, entry, exit_)
    flags = quality_flags(trade, entry, exit_)
    path = calculate_trade_path(trade, timestamps, prices)
    cf = calculate_counterfactuals(trade, timestamps, prices)
    interp = interpretation_flags(path, cf)

    pnl = safe_float(trade.get("pnl"), 0.0)
    duration = safe_float(trade.get("duration_sec"), 0.0)
    diagnosis = compute_diagnosis(path, cf, pnl)
    regime = extract_regime_features(trade, regime_index)

    trade_id = build_trade_id(trade)
    human_label = safe_text(label_map.get(trade_id))

    row: dict[str, Any] = {
        "trade_index": idx,
        "trade_id": trade_id,
        "human_label": human_label,
        "symbol": safe_text(trade.get("symbol")) or "BTCUSDT",
        "entry_time_chart": chart_time(trade.get("entry_timestamp_utc")),
        "exit_time_chart": chart_time(trade.get("exit_timestamp_utc")),
        "side": safe_text(trade.get("side")),
        "entry_timestamp_utc": safe_text(trade.get("entry_timestamp_utc")),
        "exit_timestamp_utc": safe_text(trade.get("exit_timestamp_utc")),
        "duration_sec": duration,
        "entry_price": safe_float(trade.get("entry_price"), 0.0),
        "exit_price": safe_float(trade.get("exit_price"), 0.0),
        "pnl": pnl,
        "pnl_pct": safe_float(trade.get("pnl_pct"), 0.0),
        "exit_reason": safe_text(trade.get("exit_reason")),
        "quality_score": quality_score,
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
    row.update(diagnosis)
    row.update(regime)
    row.update(compute_confidence_layer(row))
    row.update(build_trade_family(row))
    return row


def build_rows(
    trades: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    regime_index: dict[str, dict[str, Any]],
    timestamps: list[str],
    prices: list[float],
    label_map: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, trade in enumerate(trades, start=1):
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        rows.append(build_ml_row(idx, trade, entry, exit_, audit_rows, regime_index, timestamps, prices, label_map))
    return rows
