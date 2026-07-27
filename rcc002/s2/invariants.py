"""S2 OHLCV invariants.

Transcribed from RCC_002_DATA_VALIDATION_2026-07-23.md §12 ("OHLCV-
Invarianten") and §14.1 (nonfinite-as-null-equivalence, per this
implementation's own DVSEV-001-era reasoning, `rcc002.reason_codes`).
"""

from __future__ import annotations

import dataclasses
import math


@dataclasses.dataclass(frozen=True)
class OhlcvInvariantResult:
    ohlc_valid: bool
    volume_valid: bool
    nonfinite_fields: tuple[str, ...]  # which of open/high/low/close/volume were nonfinite
    ohlc_invariant_violated: bool  # a hard §12.1 rule failed on finite values
    volume_negative: bool
    volume_zero_observed: bool


_OHLC_FIELDS: tuple[str, ...] = ("open", "high", "low", "close")


def check_ohlcv_invariants(
    *, open: float, high: float, low: float, close: float, volume: float
) -> OhlcvInvariantResult:
    """Evaluate §12.1 (hard price rules) and §12.2 (volume rules).

    Nonfinite values (NaN/±Inf) are checked first and reported distinctly
    (`DV_NUMERIC_NONFINITE`) rather than run through the §12.1 inequality
    checks, since a nonfinite value makes those comparisons meaningless.
    """
    values = {"open": open, "high": high, "low": low, "close": close, "volume": volume}
    nonfinite = tuple(name for name, value in values.items() if not math.isfinite(value))

    ohlc_nonfinite = any(name in nonfinite for name in _OHLC_FIELDS)
    volume_nonfinite = "volume" in nonfinite

    ohlc_invariant_violated = False
    if not ohlc_nonfinite:
        # §12.1: "open > 0, high > 0, low > 0, close > 0, high >= open,
        # high >= close, high >= low, low <= open, low <= close."
        ohlc_invariant_violated = not (
            open > 0
            and high > 0
            and low > 0
            and close > 0
            and high >= open
            and high >= close
            and high >= low
            and low <= open
            and low <= close
        )

    volume_negative = (not volume_nonfinite) and volume < 0
    volume_zero_observed = (not volume_nonfinite) and volume == 0

    ohlc_valid = (not ohlc_nonfinite) and (not ohlc_invariant_violated)
    volume_valid = (not volume_nonfinite) and (not volume_negative)

    return OhlcvInvariantResult(
        ohlc_valid=ohlc_valid,
        volume_valid=volume_valid,
        nonfinite_fields=nonfinite,
        ohlc_invariant_violated=ohlc_invariant_violated,
        volume_negative=volume_negative,
        volume_zero_observed=volume_zero_observed,
    )
