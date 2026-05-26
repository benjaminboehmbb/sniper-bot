from __future__ import annotations


def classify_meta_state_bucket(score: float) -> str:
    if score >= 0.60:
        return "STRONG_POSITIVE"

    if score >= 0.20:
        return "POSITIVE"

    if score > -0.20:
        return "NEUTRAL"

    if score > -0.60:
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


def build_meta_state_shadow(score: float) -> dict:
    bucket = classify_meta_state_bucket(score)
    multiplier = get_position_multiplier(bucket)

    return {
        "meta_state_score": float(score),
        "meta_state_bucket": bucket,
        "position_multiplier": multiplier,
    }
