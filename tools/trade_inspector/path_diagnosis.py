"""Trade-path, counterfactual, quality, diagnosis, and confidence logic."""

from __future__ import annotations

import bisect
from datetime import timedelta, timezone
from typing import Any

if __package__:
    from .inspection_primitives import parse_ts, safe_float, safe_int, safe_text, ts_key
else:
    from inspection_primitives import parse_ts, safe_float, safe_int, safe_text, ts_key


__all__ = [
    "FUTURE_WINDOWS_MIN",
    "quality_flags",
    "score_band",
    "signed_diagnosis",
    "trade_pnl_from_price",
    "calculate_trade_path",
    "calculate_counterfactuals",
    "compute_quality_score",
    "interpretation_flags",
    "compute_diagnosis",
    "compute_confidence_layer",
]


FUTURE_WINDOWS_MIN = {
    "15m": 15,
    "1h": 60,
    "4h": 240,
    "24h": 1440,
    "72h": 4320,
    "168h": 10080,
}


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
