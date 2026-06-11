#!/usr/bin/env python3
# tools/trade_inspector/inspect_trades.py
# Trade Inspector V1D.
# Read-only trade diagnosis tool.
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


def score_band(score: int) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 60:
        return "acceptable"
    if score >= 40:
        return "weak"
    return "bad"


def signed_diagnosis(score: int) -> int:
    if score >= 75:
        return 1
    if score >= 40:
        return 0
    return -1


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

    flags = quality_flags(trade, entry, exit_)
    if "negative_duration" in flags:
        score -= 30

    score = max(0, min(100, int(score)))
    return score, score_band(score), positives, negatives


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


def compute_diagnosis(path: dict[str, Any], cf: dict[str, Any], pnl: float) -> dict[str, Any]:
    mfe_pct = safe_float(path.get("mfe_pct"), 0.0)
    mae_pct = safe_float(path.get("mae_pct"), 0.0)
    opp_24h = safe_float(cf.get("opportunity_loss_24h_pct"), 0.0)
    exit_eff_24h = safe_float(cf.get("exit_efficiency_24h_pct"), 0.0)

    entry_score = 50
    if mfe_pct <= 0.0 and mae_pct < 0.0:
        entry_score -= 35
    elif mfe_pct >= 0.02:
        entry_score += 30
    elif mfe_pct >= 0.01:
        entry_score += 15
    elif mfe_pct > 0.0:
        entry_score += 5

    if pnl < 0 and mfe_pct <= 0.0:
        entry_score -= 15

    risk_score = 80
    if mae_pct <= -0.05:
        risk_score -= 50
    elif mae_pct <= -0.02:
        risk_score -= 30
    elif mae_pct <= -0.01:
        risk_score -= 15
    elif mae_pct >= -0.002:
        risk_score += 10

    exit_score = 60
    if exit_eff_24h >= 0.8:
        exit_score += 25
    elif exit_eff_24h >= 0.6:
        exit_score += 10
    elif exit_eff_24h < 0.3:
        exit_score -= 20

    if opp_24h >= 0.10:
        exit_score -= 45
    elif opp_24h >= 0.05:
        exit_score -= 30
    elif opp_24h >= 0.01:
        exit_score -= 15

    entry_score = max(0, min(100, int(entry_score)))
    exit_score = max(0, min(100, int(exit_score)))
    risk_score = max(0, min(100, int(risk_score)))

    overall_score = int(round((entry_score * 0.4) + (exit_score * 0.4) + (risk_score * 0.2)))

    cause_raw = {
        "entry_filter_quality": max(0, 100 - entry_score),
        "early_exit": max(0, int(opp_24h * 10000)),
        "high_adverse_move": max(0, int(abs(min(0.0, mae_pct)) * 10000)),
        "risk_management": max(0, 100 - risk_score),
    }

    total = sum(cause_raw.values())
    if total <= 0:
        cause_weights = {"none": 100}
    else:
        cause_weights = {
            key: int(round(value / total * 100))
            for key, value in cause_raw.items()
            if value > 0
        }

    sorted_causes = sorted(cause_weights.items(), key=lambda item: item[1], reverse=True)
    root_cause, root_weight = sorted_causes[0]

    additional_1 = sorted_causes[1] if len(sorted_causes) > 1 else ("", 0)
    additional_2 = sorted_causes[2] if len(sorted_causes) > 2 else ("", 0)

    key_findings: list[str] = []
    if mfe_pct <= 0:
        key_findings.append("trade_never_profitable")
    if mfe_pct >= 0.01:
        key_findings.append("high_mfe")
    if mae_pct <= -0.01:
        key_findings.append("high_mae")
    if opp_24h >= 0.01:
        key_findings.append("high_opportunity_loss_24h")
    if exit_eff_24h < 0.5:
        key_findings.append("weak_exit_efficiency_24h")
    if pnl < 0:
        key_findings.append("negative_pnl")

    improvement_options: list[str] = []
    if root_cause == "early_exit":
        improvement_options = ["P1 review exit rule", "P2 test longer hold variant", "P3 test trailing exit"]
    elif root_cause == "entry_filter_quality":
        improvement_options = ["P1 review entry filter", "P2 review regime gate", "P3 review confirmation logic"]
    elif root_cause == "high_adverse_move":
        improvement_options = ["P1 review risk filter", "P2 review stop logic", "P3 review volatility filter"]
    elif root_cause == "risk_management":
        improvement_options = ["P1 review risk management", "P2 review position sizing", "P3 review drawdown control"]
    else:
        improvement_options = ["none"]

    return {
        "entry_score": entry_score,
        "exit_score": exit_score,
        "risk_score": risk_score,
        "overall_score": overall_score,
        "entry_score_band": score_band(entry_score),
        "exit_score_band": score_band(exit_score),
        "risk_score_band": score_band(risk_score),
        "overall_score_band": score_band(overall_score),
        "entry_diagnosis": signed_diagnosis(entry_score),
        "exit_diagnosis": signed_diagnosis(exit_score),
        "risk_diagnosis": signed_diagnosis(risk_score),
        "root_cause": root_cause,
        "root_cause_weight": root_weight,
        "additional_cause_1": additional_1[0],
        "additional_cause_1_weight": additional_1[1],
        "additional_cause_2": additional_2[0],
        "additional_cause_2_weight": additional_2[1],
        "cause_weights": "|".join([f"{k}={v}" for k, v in sorted_causes]),
        "key_findings": "|".join(key_findings),
        "improvement_options": "|".join(improvement_options),
    }



def compute_confidence_layer(row: dict[str, Any]) -> dict[str, Any]:
    reliability = 0

    if safe_int(row.get("has_entry_audit"), 0) == 1:
        reliability += 20
    if safe_int(row.get("has_exit_audit"), 0) == 1:
        reliability += 20
    if safe_int(row.get("path_available"), 0) == 1:
        reliability += 20
    if safe_int(row.get("counterfactual_available_24h"), 0) == 1:
        reliability += 20
    if safe_text(row.get("root_cause")):
        reliability += 20

    reliability = max(0, min(100, reliability))

    evidence_items: list[str] = []

    if safe_float(row.get("opportunity_loss_24h_pct"), 0.0) >= 0.01:
        evidence_items.append("opportunity_loss_24h_ge_1pct")
    if safe_float(row.get("exit_efficiency_24h_pct"), 0.0) < 0.5:
        evidence_items.append("exit_efficiency_24h_lt_50pct")
    if safe_float(row.get("mfe_pct"), 0.0) <= 0.0:
        evidence_items.append("mfe_zero_or_negative")
    if safe_float(row.get("mae_pct"), 0.0) <= -0.005:
        evidence_items.append("mae_below_minus_0_5pct")
    if safe_int(row.get("entry_problem_flag"), 0) == 1:
        evidence_items.append("entry_problem_flag")
    if safe_int(row.get("exit_problem_flag"), 0) == 1:
        evidence_items.append("exit_problem_flag")

    evidence_count = len(evidence_items)
    evidence_score = max(0, min(100, evidence_count * 15))

    root_weight = safe_int(row.get("root_cause_weight"), 0)
    root_cause_confidence = int(round((root_weight * 0.6) + (evidence_score * 0.25) + (reliability * 0.15)))
    root_cause_confidence = max(0, min(100, root_cause_confidence))

    opp_24h = safe_float(row.get("opportunity_loss_24h_pct"), 0.0)
    mfe_pct = safe_float(row.get("mfe_pct"), 0.0)
    mae_pct = safe_float(row.get("mae_pct"), 0.0)

    impact_score = 0
    impact_score += min(60, int(round(opp_24h * 3000)))
    impact_score += min(20, int(round(max(0.0, mfe_pct) * 1000)))
    impact_score += min(20, int(round(abs(min(0.0, mae_pct)) * 1000)))
    impact_score = max(0, min(100, impact_score))

    priority_score = int(round((impact_score * root_cause_confidence) / 100.0))
    priority_score = max(0, min(100, priority_score))

    if priority_score >= 80:
        priority = "CRITICAL"
    elif priority_score >= 60:
        priority = "HIGH"
    elif priority_score >= 35:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        "root_cause_confidence": root_cause_confidence,
        "evidence_score": evidence_score,
        "evidence_count": evidence_count,
        "evidence_items": "|".join(evidence_items),
        "impact_score": impact_score,
        "priority_score": priority_score,
        "priority": priority,
        "diagnosis_reliability": reliability,
    }




def parse_key_value_log(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            s = raw.strip()
            if "event=regime_snapshot" not in s:
                continue

            row: dict[str, Any] = {}
            parts = s.split()
            for part in parts:
                if "=" not in part:
                    continue
                key, value = part.split("=", 1)
                row[key] = value

            if row:
                rows.append(row)

    return rows


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


def build_ml_row(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
    audit_rows: list[dict[str, Any]],
    regime_index: dict[str, dict[str, Any]],
    timestamps: list[str],
    prices: list[float],
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
    return row


def print_kv(label: str, value: object) -> None:
    print(f"{label}: {value}")


def print_trade_report(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
    audit_rows: list[dict[str, Any]],
    regime_index: dict[str, dict[str, Any]],
    timestamps: list[str],
    prices: list[float],
) -> None:
    row = build_ml_row(idx, trade, entry, exit_, audit_rows, regime_index, timestamps, prices)

    print("=" * 80)
    print(f"TRADE REPORT #{idx}")
    print("=" * 80)

    print("")
    print("TRADE SUMMARY")
    print("-" * 80)
    for key in ["side", "entry_timestamp_utc", "exit_timestamp_utc", "duration_sec", "entry_price", "exit_price", "pnl", "pnl_pct", "exit_reason"]:
        print_kv(key, trade.get(key, ""))

    print("")
    print("TRADE DIAGNOSIS")
    print("-" * 80)
    for key in [
        "overall_score", "overall_score_band",
        "entry_score", "entry_score_band", "entry_diagnosis",
        "exit_score", "exit_score_band", "exit_diagnosis",
        "risk_score", "risk_score_band", "risk_diagnosis",
        "root_cause", "root_cause_weight",
        "additional_cause_1", "additional_cause_1_weight",
        "additional_cause_2", "additional_cause_2_weight",
        "cause_weights",
        "root_cause_confidence",
        "evidence_score",
        "evidence_count",
        "impact_score",
        "priority_score",
        "priority",
        "diagnosis_reliability",
    ]:
        print_kv(key, row.get(key, ""))

    print("")
    print("EVIDENCE")
    print("-" * 80)
    evidence = safe_text(row.get("evidence_items"))
    if evidence:
        for item in evidence.split("|"):
            print(f"- {item}")
    else:
        print("none")

    print("")
    print("KEY FINDINGS")
    print("-" * 80)
    findings = safe_text(row.get("key_findings"))
    if findings:
        for item in findings.split("|"):
            print(f"- {item}")
    else:
        print("none")

    print("")
    print("IMPROVEMENT OPTIONS")
    print("-" * 80)
    options = safe_text(row.get("improvement_options"))
    if options:
        for item in options.split("|"):
            print(f"- {item}")
    else:
        print("none")

    print("")
    print("QUALITY ASSESSMENT")
    print("-" * 80)
    for key in ["quality_score", "quality_class", "positive_factors", "negative_factors"]:
        print_kv(key, row.get(key, ""))

    print("")
    print("TRADE PATH")
    print("-" * 80)
    for key in ["path_available", "bars_held", "best_price_during_trade", "worst_price_during_trade", "mfe_abs", "mfe_pct", "mae_abs", "mae_pct"]:
        print_kv(key, row.get(key, ""))

    print("")
    print("REGIME CONTEXT")
    print("-" * 80)
    for key in [
        "entry_regime_label",
        "exit_regime_label",
        "entry_risk_label",
        "exit_risk_label",
        "entry_score_at_entry",
        "entry_score_at_exit",
        "entry_ma200_signal",
        "entry_mfi_signal",
        "entry_atr_signal",
        "regime_aligned",
        "risk_good_at_entry",
        "regime_changed_during_trade",
        "has_entry_regime_context",
        "has_exit_regime_context",
    ]:
        print_kv(key, row.get(key, ""))

    print("")
    print("COUNTERFACTUAL 24H CORE")
    print("-" * 80)
    for key in ["cf_return_24h_pct", "best_future_return_24h_pct", "exit_efficiency_24h_pct", "opportunity_loss_24h_pct"]:
        print_kv(key, row.get(key, ""))

    print("")
    print("INTERPRETATION FLAGS")
    print("-" * 80)
    for key in ["high_mfe_flag", "high_mae_flag", "early_exit_flag", "good_exit_flag", "entry_problem_flag", "exit_problem_flag"]:
        print_kv(key, row.get(key, ""))

    print("")


def build_rows(trades: list[dict[str, Any]], audit_rows: list[dict[str, Any]], regime_index: dict[str, dict[str, Any]], timestamps: list[str], prices: list[float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, trade in enumerate(trades, start=1):
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        rows.append(build_ml_row(idx, trade, entry, exit_, audit_rows, regime_index, timestamps, prices))
    return rows


def print_summary(rows: list[dict[str, Any]]) -> None:
    class_counts: dict[str, int] = {}
    root_counts: dict[str, int] = {}
    winners = losers = flats = 0
    total_pnl = 0.0

    for row in rows:
        cls = safe_text(row.get("quality_class"))
        root = safe_text(row.get("root_cause"))
        class_counts[cls] = class_counts.get(cls, 0) + 1
        root_counts[root] = root_counts.get(root, 0) + 1
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
    for key in ["excellent", "good", "acceptable", "weak", "bad"]:
        print_kv(key, class_counts.get(key, 0))

    print("")
    print("ROOT CAUSE COUNTS")
    print("-" * 80)
    for key, value in sorted(root_counts.items(), key=lambda item: item[1], reverse=True):
        print_kv(key, value)


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
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--export-ml-csv", default="")
    args = parser.parse_args()

    archive_dir = Path(args.archive_dir)
    trades = read_jsonl(archive_dir / "trades_l1.jsonl")
    audit_rows = read_jsonl(archive_dir / "execution_audit.jsonl")
    log_rows = parse_key_value_log(archive_dir / "l1_paper.log")
    regime_rows = log_rows
    regime_index = build_regime_index(regime_rows)
    timestamps, prices = parse_market_rows(Path(args.market_csv))

    print("TRADE INSPECTOR V2")
    print("archive_dir:", archive_dir)
    print("trades:", len(trades))
    print("audit_events:", len(audit_rows))
    print("regime_events:", len(regime_rows))
    print("market_rows:", len(timestamps))
    print("")

    rows = build_rows(trades, audit_rows, regime_index, timestamps, prices)

    if args.trade_index is not None:
        if args.trade_index < 1 or args.trade_index > len(trades):
            raise SystemExit(f"Invalid trade index: {args.trade_index}")
        trade = trades[args.trade_index - 1]
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        print_trade_report(args.trade_index, trade, entry, exit_, audit_rows, regime_index, timestamps, prices)
        return 0

    if args.summary:
        print_summary(rows)
        return 0

    if args.export_ml_csv:
        export_ml_csv(rows, Path(args.export_ml_csv))
        return 0

    print("No selection provided.")
    print("Examples:")
    print("python3 tools/trade_inspector/inspect_trades.py --trade-index 1")
    print("python3 tools/trade_inspector/inspect_trades.py --summary")
    print("python3 tools/trade_inspector/inspect_trades.py --export-ml-csv data/processed/trade_inspector/ml_v1d.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
