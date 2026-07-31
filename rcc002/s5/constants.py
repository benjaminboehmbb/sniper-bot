"""Normative constants for RCC-002 S5 regime classification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping


COMPONENT_ID: Final[str] = "RCC002_S5_REGIME_CLASSIFIER"
COMPONENT_VERSION: Final[str] = "0.4.1"

REGIME_MODEL_ID: Final[str] = "RCC002_TREND_CONTEXT_REGIME_V1"
REGIME_MODEL_VERSION: Final[str] = "1.0.0"

RAW_REGIME_PROFILE_ID: Final[str] = "RCC_TREND_REGIME_RAW_V1"
RAW_REGIME_PROFILE_VERSION: Final[str] = "1.0.0"
PERSISTED_REGIME_PROFILE_ID: Final[str] = (
    "RCC_TREND_REGIME_PERSISTED_V1"
)
PERSISTED_REGIME_PROFILE_VERSION: Final[str] = "1.0.0"
CONTEXT_PROFILE_ID: Final[str] = "RCC_CONTEXT_V1"
CONTEXT_PROFILE_VERSION: Final[str] = "1.0.0"

REGIME_SCHEMA_ID: Final[str] = "rcc002.stage.s5-regimes"
REGIME_SCHEMA_VERSION: Final[str] = "1.0.0"
REGIME_SCHEMA_REF: Final[str] = (
    f"{REGIME_SCHEMA_ID}/{REGIME_SCHEMA_VERSION}"
)

EXPECTED_INPUT_SCHEMA_ID: Final[str] = "rcc002.stage.s4-signals"
EXPECTED_INPUT_SCHEMA_VERSION: Final[str] = "1.0.0"

REGIME_STATE_SCHEMA_ID: Final[str] = "rcc002.state.s5-regimes"
REGIME_STATE_SCHEMA_VERSION: Final[str] = "1.0.0"
REGIME_STATE_SCHEMA_REF: Final[str] = (
    f"{REGIME_STATE_SCHEMA_ID}/{REGIME_STATE_SCHEMA_VERSION}"
)

NUMERIC_PROFILE_ID: Final[str] = "RCC002_FLOAT64_REGIME_NUMERICS_V1"
NUMERIC_PROFILE_VERSION: Final[str] = "1.0.0"
# These tolerances govern independent cross-implementation comparisons.
# Internal threshold decisions remain exact and use unrounded binary64 values.
ABSOLUTE_TOLERANCE: Final[float] = 1e-12
RELATIVE_TOLERANCE: Final[float] = 1e-10

SMA200_CONTEXT_PROFILE_ID: Final[str] = "RCC002_S5_SMA200_CONTEXT_V1"
SMA200_CONTEXT_PROFILE_VERSION: Final[str] = "1.0.0"
STATE_HASH_PROFILE_ID: Final[str] = "RCC002_S5_STATE_HASH_V1"
STATE_HASH_PROFILE_VERSION: Final[str] = "1.0.0"

SUPPORTED_INTERVAL: Final[str] = "1m"
INTERVAL_MILLISECONDS: Final[int] = 60_000
SLOPE_LOOKBACK_BARS: Final[int] = 1_440
SLOPE_LOOKBACK_MILLISECONDS: Final[int] = 86_400_000
CONFIRM_BARS: Final[int] = 3


class RegimeState(str, Enum):
    BULL = "BULL"
    SIDE = "SIDE"
    BEAR = "BEAR"
    UNKNOWN = "UNKNOWN"


class TrendStrength(str, Enum):
    WEAK = "WEAK"
    DEVELOPING = "DEVELOPING"
    STRONG = "STRONG"
    UNKNOWN = "UNKNOWN"


class VolatilityRelative(str, Enum):
    BELOW_REFERENCE = "BELOW_REFERENCE"
    AT_REFERENCE = "AT_REFERENCE"
    ABOVE_REFERENCE = "ABOVE_REFERENCE"
    UNKNOWN = "UNKNOWN"


REGIME_EXTENSION_FIELDS: Final[tuple[str, ...]] = (
    "regime_raw",
    "regime_effective",
    "regime_candidate",
    "regime_candidate_count",
    "regime_transition_flag",
    "regime_transition_from",
    "regime_transition_to",
    "ma200_slope_1440_pct",
    "trend_strength",
    "trend_strength_valid",
    "trend_strength_reason_codes",
    "volatility_relative",
    "volatility_relative_valid",
    "volatility_relative_reason_codes",
    "regime_model_id",
    "regime_model_version",
    "regime_schema_id",
    "regime_schema_version",
    "regime_schema_ref",
    "regime_valid",
    "regime_reason_codes",
)


REGIME_METADATA_VALUES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "regime_model_id": REGIME_MODEL_ID,
        "regime_model_version": REGIME_MODEL_VERSION,
        "regime_schema_id": REGIME_SCHEMA_ID,
        "regime_schema_version": REGIME_SCHEMA_VERSION,
        "regime_schema_ref": REGIME_SCHEMA_REF,
    }
)


@dataclass(frozen=True, slots=True)
class RegimeReasonCodeDefinition:
    code: str
    priority: int
    description: str


_REASON_CODES: Final[tuple[RegimeReasonCodeDefinition, ...]] = (
    RegimeReasonCodeDefinition(
        "REG_INPUT_QUALITY_GATE_FAILED", 30,
        "The upstream quality gate failed.",
    ),
    RegimeReasonCodeDefinition(
        "REG_INPUT_INVALID", 40,
        "A required S3 or S4 input is invalid.",
    ),
    RegimeReasonCodeDefinition(
        "REG_WARMUP_INCOMPLETE", 50,
        "The 1,440-bar slope window is incomplete.",
    ),
    RegimeReasonCodeDefinition(
        "REG_WINDOW_CROSSES_INDICATOR_SEGMENT", 60,
        "The slope window would cross an indicator segment.",
    ),
    RegimeReasonCodeDefinition(
        "REG_SLOPE_DENOMINATOR_INVALID", 70,
        "The reference SMA200 denominator is not finite and positive.",
    ),
    RegimeReasonCodeDefinition(
        "REG_NONFINITE_RESULT", 80,
        "A calculated S5 numeric result is not finite.",
    ),
    RegimeReasonCodeDefinition(
        "REG_EFFECTIVE_UNCONFIRMED", 90,
        "No effective regime has completed confirmation.",
    ),
    RegimeReasonCodeDefinition(
        "REG_SEGMENT_RESET", 100,
        "S5 state was reset at an actual segment boundary.",
    ),
    RegimeReasonCodeDefinition(
        "REG_TREND_STRENGTH_INPUT_INVALID", 110,
        "The raw S3 ADX input is invalid.",
    ),
    RegimeReasonCodeDefinition(
        "REG_VOLATILITY_INPUT_INVALID", 120,
        "The S4 relative-volatility state is invalid.",
    ),
)

REASON_CODE_REGISTRY_VERSION: Final[str] = "1.0.0"
REASON_CODE_REGISTRY: Final[
    Mapping[str, RegimeReasonCodeDefinition]
] = MappingProxyType({item.code: item for item in _REASON_CODES})
REASON_CODE_PRIORITY: Final[Mapping[str, int]] = MappingProxyType(
    {item.code: item.priority for item in _REASON_CODES}
)
REGIME_REASON_CODES: Final[frozenset[str]] = frozenset(
    tuple(REASON_CODE_REGISTRY)[:8]
)
TREND_STRENGTH_REASON_CODES: Final[frozenset[str]] = frozenset(
    {"REG_TREND_STRENGTH_INPUT_INVALID"}
)
VOLATILITY_REASON_CODES: Final[frozenset[str]] = frozenset(
    {"REG_VOLATILITY_INPUT_INVALID"}
)

if len(REGIME_EXTENSION_FIELDS) != 21:
    raise RuntimeError("S5 must add exactly 21 canonical fields")
if len(REASON_CODE_REGISTRY) != 10:
    raise RuntimeError("S5 reason-code registry must contain 10 codes")
if tuple(REASON_CODE_PRIORITY.values()) != tuple(
    sorted(REASON_CODE_PRIORITY.values())
):
    raise RuntimeError("S5 reason-code priorities must be ascending")


__all__ = [
    "ABSOLUTE_TOLERANCE",
    "COMPONENT_ID",
    "COMPONENT_VERSION",
    "CONFIRM_BARS",
    "CONTEXT_PROFILE_ID",
    "CONTEXT_PROFILE_VERSION",
    "EXPECTED_INPUT_SCHEMA_ID",
    "EXPECTED_INPUT_SCHEMA_VERSION",
    "INTERVAL_MILLISECONDS",
    "NUMERIC_PROFILE_ID",
    "NUMERIC_PROFILE_VERSION",
    "REASON_CODE_PRIORITY",
    "REASON_CODE_REGISTRY",
    "REASON_CODE_REGISTRY_VERSION",
    "REGIME_REASON_CODES",
    "REGIME_EXTENSION_FIELDS",
    "REGIME_METADATA_VALUES",
    "REGIME_MODEL_ID",
    "REGIME_MODEL_VERSION",
    "REGIME_SCHEMA_ID",
    "REGIME_SCHEMA_REF",
    "REGIME_SCHEMA_VERSION",
    "REGIME_STATE_SCHEMA_ID",
    "REGIME_STATE_SCHEMA_REF",
    "REGIME_STATE_SCHEMA_VERSION",
    "RELATIVE_TOLERANCE",
    "RAW_REGIME_PROFILE_ID",
    "RAW_REGIME_PROFILE_VERSION",
    "PERSISTED_REGIME_PROFILE_ID",
    "PERSISTED_REGIME_PROFILE_VERSION",
    "SLOPE_LOOKBACK_BARS",
    "SLOPE_LOOKBACK_MILLISECONDS",
    "SMA200_CONTEXT_PROFILE_ID",
    "SMA200_CONTEXT_PROFILE_VERSION",
    "STATE_HASH_PROFILE_ID",
    "STATE_HASH_PROFILE_VERSION",
    "SUPPORTED_INTERVAL",
    "TREND_STRENGTH_REASON_CODES",
    "VOLATILITY_REASON_CODES",
    "RegimeReasonCodeDefinition",
    "RegimeState",
    "TrendStrength",
    "VolatilityRelative",
]
