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




DEFAULT_LABEL_LIST = Path("config/trade_inspector/human_labels.txt")
DEFAULT_LABEL_REGISTRY = Path("config/trade_inspector/trade_label_registry.csv")


def load_human_labels(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing human label list: {path}")

    labels: list[str] = []
    seen: set[str] = set()

    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            label = raw.strip().lower()
            if not label or label.startswith("#"):
                continue
            if not label.isascii():
                raise ValueError(f"Non-ASCII label: {label}")
            if len(label) > 8:
                raise ValueError(f"Label too long: {label}")
            if " " in label:
                raise ValueError(f"Label contains space: {label}")
            if label in seen:
                raise ValueError(f"Duplicate label: {label}")
            seen.add(label)
            labels.append(label)

    if not labels:
        raise ValueError(f"No labels loaded from: {path}")

    return labels


def load_label_registry(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    registry: dict[str, str] = {}

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            trade_id = safe_text(row.get("trade_id"))
            label = safe_text(row.get("human_label")).lower()
            if trade_id and label:
                registry[trade_id] = label

    return registry


def save_label_registry(path: Path, registry: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["trade_id", "human_label"])
        writer.writeheader()
        for trade_id in sorted(registry):
            writer.writerow({"trade_id": trade_id, "human_label": registry[trade_id]})


def assign_human_labels(
    trades: list[dict[str, Any]],
    label_list: list[str],
    registry: dict[str, str],
) -> dict[str, str]:
    used_labels = set(registry.values())

    if len(used_labels) != len(registry.values()):
        raise ValueError("Label registry contains duplicate labels.")

    available = [label for label in label_list if label not in used_labels]

    trade_ids = sorted({build_trade_id(trade) for trade in trades})

    assigned = dict(registry)

    for trade_id in trade_ids:
        if trade_id in assigned:
            continue
        if not available:
            raise ValueError("Not enough human labels. Extend config/trade_inspector/human_labels.txt.")
        assigned[trade_id] = available.pop(0)

    return assigned


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
    label_map: dict[str, str],
) -> None:
    row = build_ml_row(idx, trade, entry, exit_, audit_rows, regime_index, timestamps, prices, label_map)

    print("=" * 80)
    print(f"TRADE REPORT #{idx}")
    print("=" * 80)

    print("")
    print("TRADE SUMMARY")
    print("-" * 80)
    for key in [
        "trade_id",
        "human_label",
        "symbol",
        "entry_time_chart",
        "exit_time_chart",
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
        if key in row:
            print_kv(key, row.get(key, ""))
        else:
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



def avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def group_rows(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        value = safe_text(row.get(key)) or "UNKNOWN"
        groups.setdefault(value, []).append(row)
    return groups


def group_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pnl_values = [safe_float(row.get("pnl"), 0.0) for row in rows]
    pnl_pct_values = [safe_float(row.get("pnl_pct"), 0.0) for row in rows]
    exit_eff_values = [safe_float(row.get("exit_efficiency_24h_pct"), 0.0) for row in rows]
    opp_values = [safe_float(row.get("opportunity_loss_24h_pct"), 0.0) for row in rows]
    overall_values = [safe_float(row.get("overall_score"), 0.0) for row in rows]

    winners = sum(1 for row in rows if safe_int(row.get("is_winner"), 0) == 1)
    losers = sum(1 for row in rows if safe_int(row.get("is_loser"), 0) == 1)

    return {
        "count": len(rows),
        "winners": winners,
        "losers": losers,
        "winrate": winners / len(rows) if rows else 0.0,
        "total_pnl": sum(pnl_values),
        "avg_pnl": avg(pnl_values),
        "avg_pnl_pct": avg(pnl_pct_values),
        "avg_exit_efficiency_24h_pct": avg(exit_eff_values),
        "avg_opportunity_loss_24h_pct": avg(opp_values),
        "avg_overall_score": avg(overall_values),
    }


def print_group_table(title: str, groups: dict[str, list[dict[str, Any]]], sort_key: str, reverse: bool = True) -> None:
    print("")
    print(title)
    print("-" * 80)

    table = []
    for name, items in groups.items():
        stats = group_stats(items)
        table.append((name, stats))

    table.sort(key=lambda item: safe_float(item[1].get(sort_key), 0.0), reverse=reverse)

    print("group,count,winrate,total_pnl,avg_pnl,avg_pnl_pct,avg_exit_eff_24h,avg_opp_loss_24h,avg_overall")
    for name, stats in table:
        print(
            f"{name},"
            f"{stats['count']},"
            f"{stats['winrate']:.4f},"
            f"{stats['total_pnl']:.8f},"
            f"{stats['avg_pnl']:.8f},"
            f"{stats['avg_pnl_pct']:.8f},"
            f"{stats['avg_exit_efficiency_24h_pct']:.8f},"
            f"{stats['avg_opportunity_loss_24h_pct']:.8f},"
            f"{stats['avg_overall_score']:.2f}"
        )



def print_trade_family_summary(rows: list[dict[str, Any]]) -> None:
    print_group_table(
        "PERFORMANCE BY TRADE FAMILY GROUP",
        group_rows(rows, "trade_family_group"),
        "total_pnl",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY TRADE FAMILY",
        group_rows(rows, "trade_family"),
        "total_pnl",
        reverse=True,
    )

def print_top_improvement_candidates(rows: list[dict[str, Any]], limit: int = 20) -> None:
    print("")
    print("TOP IMPROVEMENT CANDIDATES")
    print("-" * 80)
    print("rank,human_label,trade_id,root_cause,priority,priority_score,impact_score,confidence,opp_loss_24h,pnl,regime,risk")

    ranked = sorted(
        rows,
        key=lambda row: (
            safe_float(row.get("priority_score"), 0.0),
            safe_float(row.get("impact_score"), 0.0),
            safe_float(row.get("opportunity_loss_24h_pct"), 0.0),
        ),
        reverse=True,
    )

    for rank, row in enumerate(ranked[:limit], start=1):
        print(
            f"{rank},"
            f"{safe_text(row.get('human_label'))},"
            f"{safe_text(row.get('trade_id'))},"
            f"{safe_text(row.get('root_cause'))},"
            f"{safe_text(row.get('priority'))},"
            f"{safe_text(row.get('priority_score'))},"
            f"{safe_text(row.get('impact_score'))},"
            f"{safe_text(row.get('root_cause_confidence'))},"
            f"{safe_float(row.get('opportunity_loss_24h_pct'), 0.0):.8f},"
            f"{safe_float(row.get('pnl'), 0.0):.8f},"
            f"{safe_text(row.get('entry_regime_label'))},"
            f"{safe_text(row.get('entry_risk_label'))}"
        )



def parse_cause_weights(value: object) -> dict[str, float]:
    text = safe_text(value)
    output: dict[str, float] = {}

    if not text:
        return output

    for part in text.split("|"):
        if "=" not in part:
            continue
        key, raw_value = part.split("=", 1)
        key = safe_text(key)
        weight = safe_float(raw_value, 0.0)
        if key:
            output[key] = weight

    return output


def compute_root_cause_attribution(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[str, dict[str, float]] = {}

    for row in rows:
        pnl = safe_float(row.get("pnl"), 0.0)
        opportunity_loss = safe_float(row.get("opportunity_loss_24h_pct"), 0.0)
        impact_score = safe_float(row.get("impact_score"), 0.0)
        priority_score = safe_float(row.get("priority_score"), 0.0)
        cause_weights = parse_cause_weights(row.get("cause_weights"))

        for cause, weight in cause_weights.items():
            share = weight / 100.0
            bucket = totals.setdefault(cause, {
                "cause_weight_sum": 0.0,
                "trade_count_weighted": 0.0,
                "negative_pnl_contribution": 0.0,
                "opportunity_loss_contribution": 0.0,
                "impact_contribution": 0.0,
                "priority_contribution": 0.0,
            })

            bucket["cause_weight_sum"] += weight
            bucket["trade_count_weighted"] += share
            bucket["negative_pnl_contribution"] += max(0.0, -pnl) * share
            bucket["opportunity_loss_contribution"] += opportunity_loss * share
            bucket["impact_contribution"] += impact_score * share
            bucket["priority_contribution"] += priority_score * share

    total_weight = sum(v["cause_weight_sum"] for v in totals.values())
    total_neg = sum(v["negative_pnl_contribution"] for v in totals.values())
    total_opp = sum(v["opportunity_loss_contribution"] for v in totals.values())
    total_impact = sum(v["impact_contribution"] for v in totals.values())
    total_priority = sum(v["priority_contribution"] for v in totals.values())

    output: list[dict[str, Any]] = []

    for cause, values in totals.items():
        output.append({
            "root_cause": cause,
            "cause_weight_sum": values["cause_weight_sum"],
            "cause_share_pct": values["cause_weight_sum"] / total_weight if total_weight else 0.0,
            "trade_count_weighted": values["trade_count_weighted"],
            "negative_pnl_contribution": values["negative_pnl_contribution"],
            "negative_pnl_share_pct": values["negative_pnl_contribution"] / total_neg if total_neg else 0.0,
            "opportunity_loss_contribution": values["opportunity_loss_contribution"],
            "opportunity_loss_share_pct": values["opportunity_loss_contribution"] / total_opp if total_opp else 0.0,
            "impact_contribution": values["impact_contribution"],
            "impact_share_pct": values["impact_contribution"] / total_impact if total_impact else 0.0,
            "priority_contribution": values["priority_contribution"],
            "priority_share_pct": values["priority_contribution"] / total_priority if total_priority else 0.0,
        })

    output.sort(key=lambda row: safe_float(row.get("priority_contribution"), 0.0), reverse=True)
    return output


def print_root_cause_attribution(rows: list[dict[str, Any]]) -> None:
    attribution = compute_root_cause_attribution(rows)

    print("")
    print("ROOT CAUSE ATTRIBUTION")
    print("-" * 80)
    print(
        "root_cause,"
        "cause_share,"
        "weighted_trades,"
        "neg_pnl_share,"
        "opp_loss_share,"
        "impact_share,"
        "priority_share,"
        "priority_contribution"
    )

    for row in attribution:
        print(
            f"{safe_text(row.get('root_cause'))},"
            f"{safe_float(row.get('cause_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('trade_count_weighted'), 0.0):.4f},"
            f"{safe_float(row.get('negative_pnl_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('opportunity_loss_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('impact_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('priority_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('priority_contribution'), 0.0):.4f}"
        )


def export_root_cause_attribution_csv(rows: list[dict[str, Any]], output_dir: Path) -> None:
    write_csv_rows(
        output_dir / "aggregate_root_cause_attribution.csv",
        compute_root_cause_attribution(rows),
    )

def print_aggregate_intelligence(rows: list[dict[str, Any]]) -> None:
    print("TRADE INSPECTOR V3 AGGREGATE INTELLIGENCE")
    print("=" * 80)

    stats = group_stats(rows)

    print("")
    print("GLOBAL SUMMARY")
    print("-" * 80)
    print_kv("trades", stats["count"])
    print_kv("winners", stats["winners"])
    print_kv("losers", stats["losers"])
    print_kv("winrate", f"{stats['winrate']:.4f}")
    print_kv("total_pnl", f"{stats['total_pnl']:.8f}")
    print_kv("avg_pnl", f"{stats['avg_pnl']:.8f}")
    print_kv("avg_pnl_pct", f"{stats['avg_pnl_pct']:.8f}")
    print_kv("avg_exit_efficiency_24h_pct", f"{stats['avg_exit_efficiency_24h_pct']:.8f}")
    print_kv("avg_opportunity_loss_24h_pct", f"{stats['avg_opportunity_loss_24h_pct']:.8f}")
    print_kv("avg_overall_score", f"{stats['avg_overall_score']:.2f}")

    print_group_table(
        "ROOT CAUSE RANKING",
        group_rows(rows, "root_cause"),
        "count",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY ENTRY REGIME",
        group_rows(rows, "entry_regime_label"),
        "total_pnl",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY ENTRY RISK LABEL",
        group_rows(rows, "entry_risk_label"),
        "total_pnl",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY REGIME ALIGNMENT",
        group_rows(rows, "regime_aligned"),
        "total_pnl",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY PRIORITY",
        group_rows(rows, "priority"),
        "priority_score",
        reverse=True,
    )

    print_trade_family_summary(rows)

    print_top_improvement_candidates(rows, limit=20)
    print_root_cause_attribution(rows)


def write_csv_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        with path.open("w", encoding="utf-8", newline="") as fh:
            fh.write("")
        return

    fieldnames = list(rows[0].keys())

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def aggregate_group_rows(rows: list[dict[str, Any]], group_key: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []

    for group_name, items in group_rows(rows, group_key).items():
        stats = group_stats(items)
        output.append({
            "group_key": group_key,
            "group": group_name,
            "count": stats["count"],
            "winners": stats["winners"],
            "losers": stats["losers"],
            "winrate": stats["winrate"],
            "total_pnl": stats["total_pnl"],
            "avg_pnl": stats["avg_pnl"],
            "avg_pnl_pct": stats["avg_pnl_pct"],
            "avg_exit_efficiency_24h_pct": stats["avg_exit_efficiency_24h_pct"],
            "avg_opportunity_loss_24h_pct": stats["avg_opportunity_loss_24h_pct"],
            "avg_overall_score": stats["avg_overall_score"],
        })

    output.sort(key=lambda row: safe_float(row.get("total_pnl"), 0.0), reverse=True)
    return output


def aggregate_top_improvement_rows(rows: list[dict[str, Any]], limit: int = 100) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            safe_float(row.get("priority_score"), 0.0),
            safe_float(row.get("impact_score"), 0.0),
            safe_float(row.get("opportunity_loss_24h_pct"), 0.0),
        ),
        reverse=True,
    )

    output: list[dict[str, Any]] = []
    for rank, row in enumerate(ranked[:limit], start=1):
        output.append({
            "rank": rank,
            "human_label": safe_text(row.get("human_label")),
            "trade_id": safe_text(row.get("trade_id")),
            "root_cause": safe_text(row.get("root_cause")),
            "priority": safe_text(row.get("priority")),
            "priority_score": safe_int(row.get("priority_score"), 0),
            "impact_score": safe_int(row.get("impact_score"), 0),
            "root_cause_confidence": safe_int(row.get("root_cause_confidence"), 0),
            "opportunity_loss_24h_pct": safe_float(row.get("opportunity_loss_24h_pct"), 0.0),
            "exit_efficiency_24h_pct": safe_float(row.get("exit_efficiency_24h_pct"), 0.0),
            "pnl": safe_float(row.get("pnl"), 0.0),
            "pnl_pct": safe_float(row.get("pnl_pct"), 0.0),
            "entry_regime_label": safe_text(row.get("entry_regime_label")),
            "entry_risk_label": safe_text(row.get("entry_risk_label")),
            "regime_aligned": safe_int(row.get("regime_aligned"), 0),
            "regime_changed_during_trade": safe_int(row.get("regime_changed_during_trade"), 0),
            "entry_score_at_entry": safe_int(row.get("entry_score_at_entry"), 0),
            "entry_time_chart": safe_text(row.get("entry_time_chart")),
            "exit_time_chart": safe_text(row.get("exit_time_chart")),
        })

    return output


def export_aggregate_csvs(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    global_stats = group_stats(rows)
    write_csv_rows(output_dir / "aggregate_global_summary.csv", [{
        "trades": global_stats["count"],
        "winners": global_stats["winners"],
        "losers": global_stats["losers"],
        "winrate": global_stats["winrate"],
        "total_pnl": global_stats["total_pnl"],
        "avg_pnl": global_stats["avg_pnl"],
        "avg_pnl_pct": global_stats["avg_pnl_pct"],
        "avg_exit_efficiency_24h_pct": global_stats["avg_exit_efficiency_24h_pct"],
        "avg_opportunity_loss_24h_pct": global_stats["avg_opportunity_loss_24h_pct"],
        "avg_overall_score": global_stats["avg_overall_score"],
    }])

    group_keys = [
        "root_cause",
        "entry_regime_label",
        "entry_risk_label",
        "regime_aligned",
        "priority",
        "quality_class",
        "overall_score_band",
        "trade_family_group",
        "trade_family",
    ]

    for key in group_keys:
        write_csv_rows(
            output_dir / f"aggregate_by_{key}.csv",
            aggregate_group_rows(rows, key),
        )

    write_csv_rows(
        output_dir / "aggregate_top_improvement_candidates.csv",
        aggregate_top_improvement_rows(rows, limit=100),
    )

    export_root_cause_attribution_csv(rows, output_dir)

    print("Aggregate CSV export directory:", output_dir)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)


def add_ml_targets(row: dict[str, Any]) -> dict[str, Any]:
    pnl = safe_float(row.get("pnl"), 0.0)
    pnl_pct = safe_float(row.get("pnl_pct"), 0.0)
    overall_score = safe_int(row.get("overall_score"), 0)
    exit_eff = safe_float(row.get("exit_efficiency_24h_pct"), 0.0)
    opp_loss = safe_float(row.get("opportunity_loss_24h_pct"), 0.0)
    mae_pct = safe_float(row.get("mae_pct"), 0.0)
    mfe_pct = safe_float(row.get("mfe_pct"), 0.0)

    return {
        "target_winner": 1 if pnl > 0 else 0,
        "target_loser": 1 if pnl < 0 else 0,
        "target_flat": 1 if abs(pnl) < 1e-12 else 0,
        "target_positive_pct": 1 if pnl_pct > 0 else 0,
        "target_quality_good": 1 if overall_score >= 60 else 0,
        "target_quality_bad": 1 if overall_score < 40 else 0,
        "target_exit_efficiency_high": 1 if exit_eff >= 0.6 else 0,
        "target_exit_efficiency_low": 1 if exit_eff < 0.3 else 0,
        "target_opportunity_loss_high": 1 if opp_loss >= 0.02 else 0,
        "target_adverse_move_high": 1 if mae_pct <= -0.01 else 0,
        "target_favorable_move_present": 1 if mfe_pct > 0 else 0,
        "target_pnl": pnl,
        "target_pnl_pct": pnl_pct,
        "target_future_return_24h_pct": safe_float(row.get("cf_return_24h_pct"), 0.0),
        "target_future_return_72h_pct": safe_float(row.get("cf_return_72h_pct"), 0.0),
        "target_future_return_168h_pct": safe_float(row.get("cf_return_168h_pct"), 0.0),
    }


def dataset_split_from_trade_id(trade_id: str) -> str:
    total = sum(ord(ch) for ch in trade_id)
    bucket = total % 100

    if bucket < 70:
        return "train"
    if bucket < 85:
        return "validation"
    return "test"


def build_ml_dataset_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dataset_rows: list[dict[str, Any]] = []

    for row in rows:
        out = dict(row)
        out.update(add_ml_targets(row))
        out["ml_split"] = dataset_split_from_trade_id(safe_text(row.get("trade_id")))
        out["ml_dataset_version"] = "v4a"
        dataset_rows.append(out)

    return dataset_rows



def evaluate_split_quality(dataset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    split_counts: dict[str, int] = {"train": 0, "validation": 0, "test": 0}

    for row in dataset_rows:
        split = safe_text(row.get("ml_split"))
        if split in split_counts:
            split_counts[split] += 1

    total = len(dataset_rows)
    warnings: list[str] = []

    if total < 30:
        warnings.append("dataset_too_small_for_reliable_ml")

    for split in ["train", "validation", "test"]:
        if split_counts[split] == 0:
            warnings.append(f"empty_{split}_split")

    if split_counts["train"] > 0 and split_counts["validation"] > 0 and split_counts["test"] > 0:
        status = "PASS"
    elif total < 30:
        status = "WARN"
    else:
        status = "FAIL"

    return {
        "split_quality_status": status,
        "split_quality_warnings": "|".join(warnings) if warnings else "none",
        "rows_total": total,
        "rows_train": split_counts["train"],
        "rows_validation": split_counts["validation"],
        "rows_test": split_counts["test"],
        "train_share": split_counts["train"] / total if total else 0.0,
        "validation_share": split_counts["validation"] / total if total else 0.0,
        "test_share": split_counts["test"] / total if total else 0.0,
    }


def print_split_quality(split_quality: dict[str, Any]) -> None:
    print("")
    print("ML SPLIT QUALITY")
    print("-" * 80)
    for key in [
        "split_quality_status",
        "split_quality_warnings",
        "rows_total",
        "rows_train",
        "rows_validation",
        "rows_test",
        "train_share",
        "validation_share",
        "test_share",
    ]:
        print_kv(key, split_quality.get(key, ""))


NON_FEATURE_COLUMNS = {
    "trade_index",
    "trade_id",
    "human_label",
    "symbol",
    "entry_time_chart",
    "exit_time_chart",
    "entry_timestamp_utc",
    "exit_timestamp_utc",
    "flags",
    "positive_factors",
    "negative_factors",
    "cause_weights",
    "key_findings",
    "improvement_options",
    "evidence_items",
    "ml_dataset_version",
    "ml_split",
}

TARGET_COLUMNS = {
    "target_winner",
    "target_loser",
    "target_flat",
    "target_positive_pct",
    "target_quality_good",
    "target_quality_bad",
    "target_exit_efficiency_high",
    "target_exit_efficiency_low",
    "target_opportunity_loss_high",
    "target_adverse_move_high",
    "target_favorable_move_present",
    "target_pnl",
    "target_pnl_pct",
    "target_future_return_24h_pct",
    "target_future_return_72h_pct",
    "target_future_return_168h_pct",
}


def is_number_like(value: object) -> bool:
    if value is None:
        return False
    text = safe_text(value)
    if text == "":
        return False
    try:
        float(text)
        return True
    except Exception:
        return False


def build_category_maps(rows: list[dict[str, Any]], candidate_columns: list[str]) -> dict[str, dict[str, int]]:
    maps: dict[str, dict[str, int]] = {}

    for col in candidate_columns:
        values = sorted({safe_text(row.get(col)) for row in rows if safe_text(row.get(col)) != ""})
        maps[col] = {value: idx for idx, value in enumerate(values)}

    return maps


def build_feature_catalog(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    if not rows:
        return [], {}

    all_columns = list(rows[0].keys())

    numeric_features: list[str] = []
    categorical_features: list[str] = []

    for col in all_columns:
        if col in NON_FEATURE_COLUMNS or col in TARGET_COLUMNS:
            continue

        values = [row.get(col) for row in rows if safe_text(row.get(col)) != ""]
        if not values:
            continue

        if all(is_number_like(value) for value in values):
            numeric_features.append(col)
        else:
            categorical_features.append(col)

    category_maps = build_category_maps(rows, categorical_features)

    catalog: list[dict[str, Any]] = []

    for col in numeric_features:
        catalog.append({
            "feature_name": col,
            "feature_type": "numeric",
            "encoded_name": col,
            "category_count": 0,
            "include_for_model": 1,
        })

    for col in categorical_features:
        catalog.append({
            "feature_name": col,
            "feature_type": "categorical_label_encoded",
            "encoded_name": f"{col}_encoded",
            "category_count": len(category_maps.get(col, {})),
            "include_for_model": 1,
        })

    catalog.sort(key=lambda row: safe_text(row.get("encoded_name")))
    return catalog, category_maps


def build_model_ready_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    catalog, category_maps = build_feature_catalog(rows)

    feature_order = [safe_text(item.get("encoded_name")) for item in catalog]
    feature_sources = {safe_text(item.get("encoded_name")): item for item in catalog}

    output_rows: list[dict[str, Any]] = []

    for row in rows:
        out: dict[str, Any] = {
            "trade_id": safe_text(row.get("trade_id")),
            "human_label": safe_text(row.get("human_label")),
            "ml_split": safe_text(row.get("ml_split")),
        }

        for target in sorted(TARGET_COLUMNS):
            out[target] = row.get(target, "")

        for encoded_name in feature_order:
            item = feature_sources[encoded_name]
            source = safe_text(item.get("feature_name"))
            feature_type = safe_text(item.get("feature_type"))

            if feature_type == "numeric":
                out[encoded_name] = safe_float(row.get(source), 0.0)
            else:
                value = safe_text(row.get(source))
                out[encoded_name] = category_maps.get(source, {}).get(value, -1)

        output_rows.append(out)

    return output_rows, catalog


def export_feature_preparation(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_rows = build_ml_dataset_rows(rows)
    model_ready_rows, catalog = build_model_ready_rows(dataset_rows)

    write_csv_rows(output_dir / "trade_dataset_v4b_model_ready.csv", model_ready_rows)
    write_csv_rows(output_dir / "trade_dataset_v4b_feature_catalog.csv", catalog)

    for split in ["train", "validation", "test"]:
        split_rows = [row for row in model_ready_rows if safe_text(row.get("ml_split")) == split]
        write_csv_rows(output_dir / f"trade_dataset_v4b_model_ready_{split}.csv", split_rows)

    manifest = [{
        "ml_dataset_version": "v4b",
        "rows_total": len(model_ready_rows),
        "feature_count": len(catalog),
        "numeric_feature_count": sum(1 for row in catalog if safe_text(row.get("feature_type")) == "numeric"),
        "categorical_feature_count": sum(1 for row in catalog if safe_text(row.get("feature_type")) == "categorical_label_encoded"),
        "target_count": len(TARGET_COLUMNS),
        "purpose": "feature_importance_preparation",
        "model_training": "not_performed",
    }]

    write_csv_rows(output_dir / "trade_dataset_v4b_feature_manifest.csv", manifest)

    print("Feature preparation export directory:", output_dir)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)


HIGH_LEAKAGE_PREFIXES = (
    "target_",
    "cf_return_",
    "cf_delta_vs_realized_",
    "best_future_return_",
    "opportunity_loss_",
    "exit_efficiency_",
)

HIGH_LEAKAGE_EXACT = {
    "pnl",
    "pnl_pct",
    "is_winner",
    "is_loser",
    "is_flat",
    "quality_score",
    "quality_class_encoded",
    "root_cause_encoded",
    "root_cause_weight",
    "additional_cause_1_encoded",
    "additional_cause_1_weight",
    "additional_cause_2_encoded",
    "additional_cause_2_weight",
    "impact_score",
    "priority_score",
    "priority_encoded",
    "overall_score",
    "overall_score_band_encoded",
    "entry_score",
    "exit_score",
    "risk_score",
    "entry_diagnosis",
    "exit_diagnosis",
    "risk_diagnosis",
    "root_cause_confidence",
    "evidence_score",
    "evidence_count",
    "diagnosis_reliability",
    "early_exit_flag",
    "good_exit_flag",
    "exit_problem_flag",
    "entry_problem_flag",
    "high_mfe_flag",
    "high_mae_flag",
    "mfe_abs",
    "mfe_pct",
    "mae_abs",
    "mae_pct",
    "best_price_during_trade",
    "worst_price_during_trade",
}

MEDIUM_LEAKAGE_EXACT = {
    "bars_held",
    "duration_sec",
    "exit_price",
    "exit_reason_encoded",
    "exit_regime_label_encoded",
    "exit_risk_label_encoded",
    "exit_score_at_exit",
    "exit_ma200_signal",
    "exit_mfi_signal",
    "exit_atr_signal",
    "regime_changed_during_trade",
}

SAFE_ID_COLUMNS = {
    "trade_id",
    "human_label",
    "ml_split",
}


def audit_feature_leakage(model_ready_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    if not model_ready_rows:
        return [], [], []

    columns = list(model_ready_rows[0].keys())
    report: list[dict[str, Any]] = []
    allowed_features: list[str] = []
    blocked_features: list[str] = []

    for col in columns:
        if col in SAFE_ID_COLUMNS:
            continue

        if col in TARGET_COLUMNS or any(col.startswith(prefix) for prefix in HIGH_LEAKAGE_PREFIXES):
            risk = "HIGH"
            reason = "target_or_future_information"
            allowed = 0
        elif col in HIGH_LEAKAGE_EXACT:
            risk = "HIGH"
            reason = "post_trade_outcome_or_diagnosis"
            allowed = 0
        elif col in MEDIUM_LEAKAGE_EXACT:
            risk = "MEDIUM"
            reason = "exit_or_in_trade_information"
            allowed = 0
        else:
            risk = "LOW"
            reason = "entry_or_static_feature"
            allowed = 1

        row = {
            "feature_name": col,
            "risk_level": risk,
            "reason": reason,
            "allowed_for_training": allowed,
        }
        report.append(row)

        if allowed == 1:
            allowed_features.append(col)
        else:
            blocked_features.append(col)

    return report, allowed_features, blocked_features


def export_leakage_audit_dataset(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_rows = build_ml_dataset_rows(rows)
    model_ready_rows, catalog = build_model_ready_rows(dataset_rows)
    leakage_report, allowed_features, blocked_features = audit_feature_leakage(model_ready_rows)

    training_columns = ["trade_id", "human_label", "ml_split"] + allowed_features
    target_columns = ["trade_id", "human_label", "ml_split"] + sorted(TARGET_COLUMNS)
    blocked_columns = ["trade_id", "human_label", "ml_split"] + blocked_features

    training_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    blocked_rows: list[dict[str, Any]] = []

    for row in model_ready_rows:
        training_rows.append({col: row.get(col, "") for col in training_columns if col in row})
        target_rows.append({col: row.get(col, "") for col in target_columns if col in row})
        blocked_rows.append({col: row.get(col, "") for col in blocked_columns if col in row})

    high_count = sum(1 for row in leakage_report if row["risk_level"] == "HIGH")
    medium_count = sum(1 for row in leakage_report if row["risk_level"] == "MEDIUM")
    low_count = sum(1 for row in leakage_report if row["risk_level"] == "LOW")

    high_in_training = sum(
        1 for row in leakage_report
        if row["risk_level"] == "HIGH" and row["allowed_for_training"] == 1
    )

    audit_status = "PASS" if high_in_training == 0 else "FAIL"
    leakage_score = high_count * 3 + medium_count

    write_csv_rows(output_dir / "trade_dataset_v4c_model_ready.csv", model_ready_rows)
    write_csv_rows(output_dir / "trade_dataset_v4c_training_features.csv", training_rows)
    write_csv_rows(output_dir / "trade_dataset_v4c_targets.csv", target_rows)
    write_csv_rows(output_dir / "trade_dataset_v4c_blocked_features.csv", blocked_rows)
    write_csv_rows(output_dir / "trade_dataset_v4c_leakage_report.csv", leakage_report)
    write_csv_rows(output_dir / "trade_dataset_v4c_feature_catalog.csv", catalog)

    manifest = [{
        "ml_dataset_version": "v4c",
        "rows_total": len(model_ready_rows),
        "total_features_audited": len(leakage_report),
        "allowed_features": len(allowed_features),
        "target_columns": len(TARGET_COLUMNS),
        "blocked_features": len(blocked_features),
        "high_risk_leakage_features": high_count,
        "medium_risk_leakage_features": medium_count,
        "low_risk_features": low_count,
        "high_risk_features_allowed_for_training": high_in_training,
        "leakage_score": leakage_score,
        "audit_status": audit_status,
        "purpose": "dataset_leakage_audit",
    }]

    write_csv_rows(output_dir / "trade_dataset_v4c_manifest.csv", manifest)

    print("Leakage audit export directory:", output_dir)
    print("audit_status:", audit_status)
    print("allowed_features:", len(allowed_features))
    print("blocked_features:", len(blocked_features))
    print("high_risk_leakage_features:", high_count)
    print("medium_risk_leakage_features:", medium_count)
    print("low_risk_features:", low_count)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)


def pearson_abs(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0

    mx = avg(xs)
    my = avg(ys)

    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = sum((x - mx) ** 2 for x in xs)
    den_y = sum((y - my) ** 2 for y in ys)

    if den_x <= 0 or den_y <= 0:
        return 0.0

    return abs(num / ((den_x ** 0.5) * (den_y ** 0.5)))


def feature_importance_rows(
    training_rows: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    target_column: str,
) -> list[dict[str, Any]]:
    target_by_trade_id = {
        safe_text(row.get("trade_id")): safe_float(row.get(target_column), 0.0)
        for row in target_rows
    }

    if not training_rows:
        return []

    blocked = {"trade_id", "human_label", "ml_split"}
    features = [col for col in training_rows[0].keys() if col not in blocked]

    output: list[dict[str, Any]] = []

    for feature in features:
        xs: list[float] = []
        ys: list[float] = []

        for row in training_rows:
            trade_id = safe_text(row.get("trade_id"))
            if trade_id not in target_by_trade_id:
                continue
            xs.append(safe_float(row.get(feature), 0.0))
            ys.append(target_by_trade_id[trade_id])

        score = pearson_abs(xs, ys)

        output.append({
            "target_column": target_column,
            "feature_name": feature,
            "importance_score": score,
            "rows_used": len(xs),
            "method": "absolute_pearson_correlation",
        })

    output.sort(key=lambda row: safe_float(row.get("importance_score"), 0.0), reverse=True)
    return output


def export_feature_importance(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_rows = build_ml_dataset_rows(rows)
    model_ready_rows, _catalog = build_model_ready_rows(dataset_rows)
    _leakage_report, allowed_features, _blocked_features = audit_feature_leakage(model_ready_rows)

    training_columns = ["trade_id", "human_label", "ml_split"] + allowed_features
    target_columns = ["trade_id", "human_label", "ml_split"] + sorted(TARGET_COLUMNS)

    training_rows = [
        {col: row.get(col, "") for col in training_columns if col in row}
        for row in model_ready_rows
    ]

    target_rows = [
        {col: row.get(col, "") for col in target_columns if col in row}
        for row in model_ready_rows
    ]

    main_targets = [
        "target_winner",
        "target_loser",
        "target_quality_good",
        "target_quality_bad",
        "target_opportunity_loss_high",
        "target_exit_efficiency_high",
        "target_pnl_pct",
        "target_future_return_24h_pct",
        "target_future_return_72h_pct",
    ]

    all_importance: list[dict[str, Any]] = []

    for target in main_targets:
        all_importance.extend(feature_importance_rows(training_rows, target_rows, target))

    write_csv_rows(output_dir / "feature_importance_v5.csv", all_importance)

    for target in main_targets:
        target_rows_out = [row for row in all_importance if safe_text(row.get("target_column")) == target]
        write_csv_rows(output_dir / f"feature_importance_v5_{target}.csv", target_rows_out)

    rows_total = len(model_ready_rows)
    status = "PASS" if rows_total >= 30 else "WARN"
    warning = "dataset_too_small_for_reliable_feature_importance" if rows_total < 30 else "none"

    manifest = [{
        "engine_version": "v5",
        "rows_total": rows_total,
        "allowed_features": len(allowed_features),
        "targets_evaluated": len(main_targets),
        "method": "absolute_pearson_correlation",
        "model_training": "not_performed",
        "feature_importance_status": status,
        "feature_importance_warning": warning,
    }]

    write_csv_rows(output_dir / "feature_importance_v5_manifest.csv", manifest)

    print("Feature importance export directory:", output_dir)
    print("feature_importance_status:", status)
    print("feature_importance_warning:", warning)
    print("rows_total:", rows_total)
    print("allowed_features:", len(allowed_features))
    print("targets_evaluated:", len(main_targets))
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)

def export_ml_dataset(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_rows = build_ml_dataset_rows(rows)

    all_path = output_dir / "trade_dataset_v4a.csv"
    write_csv_rows(all_path, dataset_rows)

    for split in ["train", "validation", "test"]:
        split_rows = [row for row in dataset_rows if safe_text(row.get("ml_split")) == split]
        write_csv_rows(output_dir / f"trade_dataset_v4a_{split}.csv", split_rows)

    split_quality = evaluate_split_quality(dataset_rows)
    print_split_quality(split_quality)

    manifest_rows = [{
        "ml_dataset_version": "v4a",
        "split_quality_status": split_quality["split_quality_status"],
        "split_quality_warnings": split_quality["split_quality_warnings"],
        "rows_total": split_quality["rows_total"],
        "rows_train": split_quality["rows_train"],
        "rows_validation": split_quality["rows_validation"],
        "rows_test": split_quality["rows_test"],
        "train_share": split_quality["train_share"],
        "validation_share": split_quality["validation_share"],
        "test_share": split_quality["test_share"],
        "target_columns": "|".join([
            "target_winner",
            "target_loser",
            "target_quality_good",
            "target_quality_bad",
            "target_exit_efficiency_high",
            "target_opportunity_loss_high",
            "target_pnl",
            "target_pnl_pct",
            "target_future_return_24h_pct",
            "target_future_return_72h_pct",
            "target_future_return_168h_pct",
        ]),
        "feature_scope": "trade|path|counterfactual|diagnosis|confidence|regime|family",
        "split_method": "deterministic_trade_id_ascii_bucket",
    }]

    write_csv_rows(output_dir / "trade_dataset_v4a_manifest.csv", manifest_rows)

    print("ML dataset export directory:", output_dir)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)

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
    parser.add_argument("--aggregate", action="store_true")
    parser.add_argument("--export-ml-csv", default="")
    parser.add_argument("--export-aggregate-csv-dir", default="")
    parser.add_argument("--export-ml-dataset-dir", default="")
    parser.add_argument("--export-feature-prep-dir", default="")
    parser.add_argument("--export-leakage-audit-dir", default="")
    parser.add_argument("--export-feature-importance-dir", default="")
    parser.add_argument("--label-list", default=str(DEFAULT_LABEL_LIST))
    parser.add_argument("--label-registry", default=str(DEFAULT_LABEL_REGISTRY))
    parser.add_argument("--update-label-registry", action="store_true")
    args = parser.parse_args()

    archive_dir = Path(args.archive_dir)
    trades = read_jsonl(archive_dir / "trades_l1.jsonl")
    audit_rows = read_jsonl(archive_dir / "execution_audit.jsonl")
    log_rows = parse_key_value_log(archive_dir / "l1_paper.log")
    regime_rows = log_rows
    regime_index = build_regime_index(regime_rows)
    timestamps, prices = parse_market_rows(Path(args.market_csv))
    label_list = load_human_labels(Path(args.label_list))
    existing_registry = load_label_registry(Path(args.label_registry))
    label_map = assign_human_labels(trades, label_list, existing_registry)

    if args.update_label_registry:
        save_label_registry(Path(args.label_registry), label_map)

    print("TRADE INSPECTOR V5")
    print("archive_dir:", archive_dir)
    print("trades:", len(trades))
    print("audit_events:", len(audit_rows))
    print("regime_events:", len(regime_rows))
    print("market_rows:", len(timestamps))
    print("human_labels_loaded:", len(label_list))
    print("label_registry_entries:", len(label_map))
    print("")

    rows = build_rows(trades, audit_rows, regime_index, timestamps, prices, label_map)

    if args.trade_index is not None:
        if args.trade_index < 1 or args.trade_index > len(trades):
            raise SystemExit(f"Invalid trade index: {args.trade_index}")
        trade = trades[args.trade_index - 1]
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        print_trade_report(args.trade_index, trade, entry, exit_, audit_rows, regime_index, timestamps, prices, label_map)
        return 0

    if args.summary:
        print_summary(rows)
        return 0

    if args.aggregate:
        print_aggregate_intelligence(rows)
        return 0

    if args.export_ml_csv:
        export_ml_csv(rows, Path(args.export_ml_csv))
        return 0

    if args.export_aggregate_csv_dir:
        export_aggregate_csvs(rows, Path(args.export_aggregate_csv_dir))
        return 0

    if args.export_ml_dataset_dir:
        export_ml_dataset(rows, Path(args.export_ml_dataset_dir))
        return 0

    if args.export_feature_prep_dir:
        export_feature_preparation(rows, Path(args.export_feature_prep_dir))
        return 0

    if args.export_leakage_audit_dir:
        export_leakage_audit_dataset(rows, Path(args.export_leakage_audit_dir))
        return 0

    if args.export_feature_importance_dir:
        export_feature_importance(rows, Path(args.export_feature_importance_dir))
        return 0

    print("No selection provided.")
    print("Examples:")
    print("python3 tools/trade_inspector/inspect_trades.py --trade-index 1")
    print("python3 tools/trade_inspector/inspect_trades.py --summary")
    print("python3 tools/trade_inspector/inspect_trades.py --aggregate")
    print("python3 tools/trade_inspector/inspect_trades.py --export-ml-csv data/processed/trade_inspector/ml_v3.csv")
    print("python3 tools/trade_inspector/inspect_trades.py --export-aggregate-csv-dir reports/trade_inspector/aggregate_v3a")
    print("python3 tools/trade_inspector/inspect_trades.py --export-ml-dataset-dir data/ml/trade_inspector_v4")
    print("python3 tools/trade_inspector/inspect_trades.py --export-feature-prep-dir data/ml/trade_inspector_v4b")
    print("python3 tools/trade_inspector/inspect_trades.py --export-leakage-audit-dir data/ml/trade_inspector_v4c")
    print("python3 tools/trade_inspector/inspect_trades.py --export-feature-importance-dir data/ml/trade_inspector_v5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
