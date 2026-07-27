"""S3 canonical profile identifiers and allowlist.

Transcribed from Indicator Specification §5 (Indikatorregister), §21.2
(Segment-ID), §26 (Ausgabevertrag), §28 (Numerische Toleranzen).
"""

from __future__ import annotations

INDICATOR_PROFILE_ID = "RCC002_CANONICAL_INDICATORS_V1"
INDICATOR_PROFILE_VERSION = "1.0.0"

INDICATOR_SCHEMA_ID = "rcc002.stage.s3-indicators"
INDICATOR_SCHEMA_VERSION = "1.0.0"
INDICATOR_SCHEMA_REF = f"{INDICATOR_SCHEMA_ID}/{INDICATOR_SCHEMA_VERSION}"

INDICATOR_STATE_SCHEMA_ID = "rcc002.state.s3-indicators"
INDICATOR_STATE_SCHEMA_VERSION = "1.0.0"
INDICATOR_STATE_SCHEMA_REF = f"{INDICATOR_STATE_SCHEMA_ID}/{INDICATOR_STATE_SCHEMA_VERSION}"

INDICATOR_SEGMENT_PROFILE_ID = "RCC002_INDICATOR_SEGMENTATION_V1"
INDICATOR_SEGMENT_PROFILE_VERSION = "1.0.0"

INDICATOR_NUMERIC_PROFILE_ID = "RCC002_FLOAT64_INDICATOR_NUMERICS_V1"
INDICATOR_NUMERIC_PROFILE_VERSION = "1.0.0"

# §28.2: standard tolerance for independent-implementation comparison.
# abs(a - b) <= ABSOLUTE_TOLERANCE + RELATIVE_TOLERANCE * max(abs(a), abs(b))
ABSOLUTE_TOLERANCE = 1e-12
RELATIVE_TOLERANCE = 1e-10

# §5: the positive allowlist of canonical numeric S3 indicator fields, in
# certified order. Each field x is immediately followed by x_valid,
# x_warmup_complete, x_reason_codes (§26.3 column order).
INDICATOR_FIELD_ALLOWLIST: tuple[str, ...] = (
    "sma_close_200",
    "ema_close_50",
    "rsi_wilder_14",
    "macd_line_12_26",
    "macd_signal_line_12_26_9",
    "macd_hist_12_26_9",
    "bb_mid_20",
    "bb_upper_20_2",
    "bb_lower_20_2",
    "bb_width_20_2",
    "stoch_k_14",
    "true_range",
    "atr_wilder_14",
    "roc_close_12_pct",
    "obv",
    "typical_price",
    "cci_20",
    "mfi_14",
    "plus_di_14",
    "minus_di_14",
    "dx_14",
    "adx_wilder_14",
)

assert len(INDICATOR_FIELD_ALLOWLIST) == 22
