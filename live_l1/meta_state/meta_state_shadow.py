from __future__ import annotations

import math


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize_score(current_score: int) -> float:
    raw = clamp(float(current_score), -4.0, 4.0)
    return math.tanh(raw / 2.0)


def classify_meta_state_bucket(score: float) -> str:
    if score >= 0.75:
        return "STRONG_POSITIVE"
    if score >= 0.30:
        return "POSITIVE"
    if score > -0.30:
        return "NEUTRAL"
    if score > -0.75:
        return "NEGATIVE"
    return "STRONG_NEGATIVE"


def get_position_multiplier(bucket: str) -> float:
    mapping = {
        "STRONG_POSITIVE": 1.00,
        "POSITIVE": 0.75,
        "NEUTRAL": 0.50,
        "NEGATIVE": 0.25,
        "STRONG_NEGATIVE": 0.00,
    }
    return float(mapping.get(bucket, 1.0))


def build_meta_state_shadow(current_score: int) -> dict:
    normalized_score = normalize_score(current_score)
    bucket = classify_meta_state_bucket(normalized_score)
    multiplier = get_position_multiplier(bucket)

    return {
        "meta_state_score": float(normalized_score),
        "meta_state_bucket": bucket,
        "position_multiplier": multiplier,
    }
