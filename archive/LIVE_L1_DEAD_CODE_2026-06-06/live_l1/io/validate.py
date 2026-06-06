# live_l1/io/validate.py
#
# L1 Data Validation (Step 2/8)
# - Setzt data_valid True/False
# - Keine Heuristik, nur harte Kriterien
# - Deterministisch, explainable, loggable
#
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from live_l1.io.market import MarketSnapshot


@dataclass(frozen=True)
class ValidationResult:
    data_valid: bool
    reasons: List[str]


def validate_snapshot(s: MarketSnapshot) -> ValidationResult:
    reasons: List[str] = []

    # Hard rules only:
    if not s.timestamp_utc or "T" not in s.timestamp_utc or not s.timestamp_utc.endswith("Z"):
        reasons.append("bad_timestamp_utc_format")

    if not s.symbol:
        reasons.append("missing_symbol")

    if not isinstance(s.price, (int, float)) or not (s.price > 0.0):
        reasons.append("price_non_positive")

    if not isinstance(s.signals, dict) or len(s.signals) == 0:
        reasons.append("signals_missing")

    else:
        # signals must be -1/0/1 integers
        for k in sorted(s.signals.keys()):
            v = s.signals[k]
            if v not in (-1, 0, 1):
                reasons.append(f"signal_out_of_domain:{k}:{v}")

    return ValidationResult(data_valid=(len(reasons) == 0), reasons=reasons)
