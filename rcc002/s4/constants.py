"""Normative constants and registries for RCC-002 S4 signal transformation.

This module contains no transformation logic. It defines the immutable
identities, field ordering, roles, value domains, and reason-code registry
required by the certified RCC-002 S4 specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping


# ---------------------------------------------------------------------------
# Component identity
# ---------------------------------------------------------------------------

COMPONENT_ID: Final[str] = "RCC002_S4_SIGNAL_TRANSFORMER"
COMPONENT_VERSION: Final[str] = "0.3.1"


# ---------------------------------------------------------------------------
# Canonical profile and schema identity
# ---------------------------------------------------------------------------

SIGNAL_PROFILE_ID: Final[str] = "RCC002_CANONICAL_SIGNALS_V1"
SIGNAL_PROFILE_VERSION: Final[str] = "1.0.0"

SIGNAL_SCHEMA_ID: Final[str] = "rcc002.stage.s4-signals"
SIGNAL_SCHEMA_VERSION: Final[str] = "1.0.0"
SIGNAL_SCHEMA_REF: Final[str] = (
    f"{SIGNAL_SCHEMA_ID}/{SIGNAL_SCHEMA_VERSION}"
)

EXPECTED_INPUT_SCHEMA_ID: Final[str] = "rcc002.stage.s3-indicators"
EXPECTED_INPUT_SCHEMA_VERSION: Final[str] = "1.0.0"
EXPECTED_INPUT_SCHEMA_REF: Final[str] = (
    f"{EXPECTED_INPUT_SCHEMA_ID}/{EXPECTED_INPUT_SCHEMA_VERSION}"
)

DISCRETE_PROFILE_ID: Final[str] = "RCC_DISCRETE_V1"
DISCRETE_PROFILE_VERSION: Final[str] = "1.0.0"

CONTINUOUS_PROFILE_ID: Final[str] = "RCC_CONTINUOUS_V1"
CONTINUOUS_PROFILE_VERSION: Final[str] = "1.0.0"

VALIDITY_PROFILE_ID: Final[str] = "RCC002_SIGNAL_VALIDITY_V1"
VALIDITY_PROFILE_VERSION: Final[str] = "1.0.0"

REASON_CODE_REGISTRY_VERSION: Final[str] = "1.0.0"

LEGACY_PROFILE_ID: Final[str] = "LEGACY_BTC_BINARY_V1"
LEGACY_PROFILE_VERSION: Final[str] = "1.0.0"
LEGACY_SCHEMA_REF: Final[str] = (
    "rcc002.comparison.s4-legacy-btc-binary/1.0.0"
)


# ---------------------------------------------------------------------------
# Metadata fields
# ---------------------------------------------------------------------------

SIGNAL_METADATA_FIELDS: Final[tuple[str, ...]] = (
    "signal_profile_id",
    "signal_profile_version",
    "signal_schema_id",
    "signal_schema_version",
    "signal_schema_ref",
)

SIGNAL_METADATA_VALUES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "signal_profile_id": SIGNAL_PROFILE_ID,
        "signal_profile_version": SIGNAL_PROFILE_VERSION,
        "signal_schema_id": SIGNAL_SCHEMA_ID,
        "signal_schema_version": SIGNAL_SCHEMA_VERSION,
        "signal_schema_ref": SIGNAL_SCHEMA_REF,
    }
)


# ---------------------------------------------------------------------------
# Signal roles
# ---------------------------------------------------------------------------

class SignalRole(str, Enum):
    """Normative semantic roles of S4 base fields."""

    DIRECTION_DISCRETE = "DIRECTION_DISCRETE"
    DIRECTION_SCORE = "DIRECTION_SCORE"
    TREND_STATE = "TREND_STATE"
    VOLATILITY_STATE = "VOLATILITY_STATE"
    TREND_STRENGTH = "TREND_STRENGTH"


# ---------------------------------------------------------------------------
# Canonical S4 base fields
# ---------------------------------------------------------------------------

DISCRETE_DIRECTION_FIELDS: Final[tuple[str, ...]] = (
    "sig_rsi_mr_d",
    "sig_macd_momentum_d",
    "sig_bollinger_mr_d",
    "sig_stoch_mr_d",
    "sig_cci_mr_d",
    "sig_mfi_mr_d",
    "sig_obv_momentum_d",
    "sig_roc_momentum_d",
)

DISCRETE_STATE_FIELDS: Final[tuple[str, ...]] = (
    "state_ma200_trend_d",
    "state_ema50_trend_d",
    "state_atr_relative_d",
    "state_adx_strength_d",
)

DISCRETE_BASE_FIELDS: Final[tuple[str, ...]] = (
    *DISCRETE_DIRECTION_FIELDS,
    *DISCRETE_STATE_FIELDS,
)

CONTINUOUS_DIRECTION_FIELDS: Final[tuple[str, ...]] = (
    "score_rsi_mr_c",
    "score_macd_momentum_c",
    "score_bollinger_mr_c",
    "score_stoch_mr_c",
    "score_cci_mr_c",
    "score_mfi_mr_c",
    "score_obv_momentum_c",
    "score_roc_momentum_c",
)

CONTINUOUS_STATE_FIELDS: Final[tuple[str, ...]] = (
    "score_ma200_trend_c",
    "score_ema50_trend_c",
    "score_atr_relative_c",
    "score_adx_strength_c",
)

CONTINUOUS_BASE_FIELDS: Final[tuple[str, ...]] = (
    *CONTINUOUS_DIRECTION_FIELDS,
    *CONTINUOUS_STATE_FIELDS,
)

SIGNAL_BASE_FIELDS: Final[tuple[str, ...]] = (
    *DISCRETE_BASE_FIELDS,
    *CONTINUOUS_BASE_FIELDS,
)

if len(SIGNAL_BASE_FIELDS) != 24:
    raise RuntimeError(
        "The canonical S4 schema must contain exactly 24 base fields."
    )

if len(set(SIGNAL_BASE_FIELDS)) != len(SIGNAL_BASE_FIELDS):
    raise RuntimeError("Duplicate canonical S4 base-field registration.")


# ---------------------------------------------------------------------------
# Field roles
# ---------------------------------------------------------------------------

FIELD_ROLES: Final[Mapping[str, SignalRole]] = MappingProxyType(
    {
        "sig_rsi_mr_d": SignalRole.DIRECTION_DISCRETE,
        "sig_macd_momentum_d": SignalRole.DIRECTION_DISCRETE,
        "sig_bollinger_mr_d": SignalRole.DIRECTION_DISCRETE,
        "sig_stoch_mr_d": SignalRole.DIRECTION_DISCRETE,
        "sig_cci_mr_d": SignalRole.DIRECTION_DISCRETE,
        "sig_mfi_mr_d": SignalRole.DIRECTION_DISCRETE,
        "sig_obv_momentum_d": SignalRole.DIRECTION_DISCRETE,
        "sig_roc_momentum_d": SignalRole.DIRECTION_DISCRETE,
        "state_ma200_trend_d": SignalRole.TREND_STATE,
        "state_ema50_trend_d": SignalRole.TREND_STATE,
        "state_atr_relative_d": SignalRole.VOLATILITY_STATE,
        "state_adx_strength_d": SignalRole.TREND_STRENGTH,
        "score_rsi_mr_c": SignalRole.DIRECTION_SCORE,
        "score_macd_momentum_c": SignalRole.DIRECTION_SCORE,
        "score_bollinger_mr_c": SignalRole.DIRECTION_SCORE,
        "score_stoch_mr_c": SignalRole.DIRECTION_SCORE,
        "score_cci_mr_c": SignalRole.DIRECTION_SCORE,
        "score_mfi_mr_c": SignalRole.DIRECTION_SCORE,
        "score_obv_momentum_c": SignalRole.DIRECTION_SCORE,
        "score_roc_momentum_c": SignalRole.DIRECTION_SCORE,
        "score_ma200_trend_c": SignalRole.TREND_STATE,
        "score_ema50_trend_c": SignalRole.TREND_STATE,
        "score_atr_relative_c": SignalRole.VOLATILITY_STATE,
        "score_adx_strength_c": SignalRole.TREND_STRENGTH,
    }
)

if tuple(FIELD_ROLES) != SIGNAL_BASE_FIELDS:
    raise RuntimeError(
        "FIELD_ROLES order must exactly match SIGNAL_BASE_FIELDS."
    )


# ---------------------------------------------------------------------------
# Logical field definitions
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SignalFieldDefinition:
    """Normative logical definition of one S4 base field."""

    name: str
    logical_type: str
    nullable: bool
    role: SignalRole
    owner_stage: str
    minimum: float
    maximum: float
    allowed_discrete_values: frozenset[int] | None = None


def _discrete_definition(
    name: str,
    role: SignalRole,
    allowed_values: frozenset[int],
) -> SignalFieldDefinition:
    return SignalFieldDefinition(
        name=name,
        logical_type="Int8",
        nullable=True,
        role=role,
        owner_stage="S4_SIGNALS",
        minimum=float(min(allowed_values)),
        maximum=float(max(allowed_values)),
        allowed_discrete_values=allowed_values,
    )


def _continuous_definition(
    name: str,
    role: SignalRole,
) -> SignalFieldDefinition:
    minimum = 0.0 if name == "score_adx_strength_c" else -1.0

    return SignalFieldDefinition(
        name=name,
        logical_type="Float64",
        nullable=True,
        role=role,
        owner_stage="S4_SIGNALS",
        minimum=minimum,
        maximum=1.0,
        allowed_discrete_values=None,
    )


_SIGNED_DISCRETE_VALUES: Final[frozenset[int]] = frozenset(
    {-1, 0, 1}
)
_ADX_DISCRETE_VALUES: Final[frozenset[int]] = frozenset({0, 1})

FIELD_DEFINITIONS: Final[Mapping[str, SignalFieldDefinition]] = (
    MappingProxyType(
        {
            **{
                name: _discrete_definition(
                    name,
                    FIELD_ROLES[name],
                    (
                        _ADX_DISCRETE_VALUES
                        if name == "state_adx_strength_d"
                        else _SIGNED_DISCRETE_VALUES
                    ),
                )
                for name in DISCRETE_BASE_FIELDS
            },
            **{
                name: _continuous_definition(
                    name,
                    FIELD_ROLES[name],
                )
                for name in CONTINUOUS_BASE_FIELDS
            },
        }
    )
)

if tuple(FIELD_DEFINITIONS) != SIGNAL_BASE_FIELDS:
    raise RuntimeError(
        "FIELD_DEFINITIONS order must exactly match SIGNAL_BASE_FIELDS."
    )


# ---------------------------------------------------------------------------
# Companion fields and canonical S4 extension order
# ---------------------------------------------------------------------------

def valid_field_name(base_field: str) -> str:
    """Return the normative validity companion-field name."""

    return f"{base_field}_valid"


def reason_codes_field_name(base_field: str) -> str:
    """Return the normative reason-code companion-field name."""

    return f"{base_field}_reason_codes"


def _build_signal_extension_fields() -> tuple[str, ...]:
    fields: list[str] = list(SIGNAL_METADATA_FIELDS)

    for base_field in SIGNAL_BASE_FIELDS:
        fields.extend(
            (
                base_field,
                valid_field_name(base_field),
                reason_codes_field_name(base_field),
            )
        )

    return tuple(fields)


SIGNAL_EXTENSION_FIELDS: Final[tuple[str, ...]] = (
    _build_signal_extension_fields()
)

EXPECTED_SIGNAL_EXTENSION_FIELD_COUNT: Final[int] = 5 + (24 * 3)

if len(SIGNAL_EXTENSION_FIELDS) != EXPECTED_SIGNAL_EXTENSION_FIELD_COUNT:
    raise RuntimeError(
        "Canonical S4 extension must contain exactly 77 fields."
    )

if len(set(SIGNAL_EXTENSION_FIELDS)) != len(SIGNAL_EXTENSION_FIELDS):
    raise RuntimeError("Duplicate canonical S4 extension-field registration.")


# ---------------------------------------------------------------------------
# Reason-code registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SignalReasonCodeDefinition:
    """Normative S4 reason-code registration."""

    code: str
    priority: int
    invalidating: bool
    description: str


_REASON_CODE_DEFINITIONS: Final[
    tuple[SignalReasonCodeDefinition, ...]
] = (
    SignalReasonCodeDefinition(
        code="SIG_SCHEMA_MISMATCH",
        priority=10,
        invalidating=True,
        description="S3 or S4 schema is incompatible.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_PROFILE_MISMATCH",
        priority=20,
        invalidating=True,
        description="Profile ID or profile version is incompatible.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_INPUT_QUALITY_GATE_FAILED",
        priority=30,
        invalidating=True,
        description="quality_gate_pass is false.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_INPUT_INVALID",
        priority=40,
        invalidating=True,
        description="At least one required S3 input is invalid.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_WARMUP_INCOMPLETE",
        priority=50,
        invalidating=True,
        description="An additional S4 rolling window is incomplete.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_WINDOW_CROSSES_INDICATOR_SEGMENT",
        priority=60,
        invalidating=True,
        description="A required window would cross an indicator segment.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_MACD_ZERO_ATR_CONFLICT",
        priority=70,
        invalidating=True,
        description="MACD is nonzero while ATR is zero.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_BB_ZERO_WIDTH_CONFLICT",
        priority=80,
        invalidating=True,
        description="Close differs from BB mid while band width is zero.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_OBV_ZERO_VOLUME_CONFLICT",
        priority=90,
        invalidating=True,
        description="OBV differs while the relevant volume sum is zero.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_ROC_ZERO_ATR_CONFLICT",
        priority=100,
        invalidating=True,
        description="ROC is nonzero while the ATR quotient is zero.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_MA200_ZERO_ATR_CONFLICT",
        priority=110,
        invalidating=True,
        description="MA200 distance is nonzero while ATR is zero.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_EMA50_ZERO_ATR_CONFLICT",
        priority=120,
        invalidating=True,
        description="EMA50 distance is nonzero while ATR is zero.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_ATR_RATIO_ZERO_CONFLICT",
        priority=130,
        invalidating=True,
        description="Current ATR is positive while reference ATR is zero.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_NONFINITE_RESULT",
        priority=140,
        invalidating=True,
        description="The calculated result is NaN or infinite.",
    ),
    SignalReasonCodeDefinition(
        code="SIG_RANGE_INVARIANT_FAILED",
        priority=150,
        invalidating=True,
        description="The result violates its registered value range.",
    ),
)

REASON_CODE_REGISTRY: Final[
    Mapping[str, SignalReasonCodeDefinition]
] = MappingProxyType(
    {
        definition.code: definition
        for definition in _REASON_CODE_DEFINITIONS
    }
)

REASON_CODE_PRIORITY: Final[Mapping[str, int]] = MappingProxyType(
    {
        definition.code: definition.priority
        for definition in _REASON_CODE_DEFINITIONS
    }
)

if len(REASON_CODE_REGISTRY) != 15:
    raise RuntimeError(
        "The S4 reason-code registry must contain exactly 15 codes."
    )

if tuple(REASON_CODE_PRIORITY.values()) != tuple(
    sorted(REASON_CODE_PRIORITY.values())
):
    raise RuntimeError(
        "S4 reason-code priorities must be strictly ascending."
    )

if len(set(REASON_CODE_PRIORITY.values())) != len(
    REASON_CODE_PRIORITY
):
    raise RuntimeError("S4 reason-code priorities must be unique.")

if not all(
    definition.invalidating
    for definition in REASON_CODE_REGISTRY.values()
):
    raise RuntimeError(
        "All S4 reason codes in registry version 1.0.0 are invalidating."
    )


# ---------------------------------------------------------------------------
# Forbidden stage outputs
# ---------------------------------------------------------------------------

FORBIDDEN_S4_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "market_regime",
        "regime_state",
        "regime_raw_state",
        "regime_persisted_state",
        "allow_long",
        "allow_short",
        "data_gate_pass",
        "gate_state",
        "gate_valid",
    }
)

FORBIDDEN_S4_PREFIXES: Final[tuple[str, ...]] = (
    "fwd_",
    "label_",
    "barrier_",
)


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def sort_reason_codes(codes: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Validate, deduplicate, and normatively order S4 reason codes."""

    unknown = set(codes).difference(REASON_CODE_REGISTRY)
    if unknown:
        unknown_text = ", ".join(sorted(unknown))
        raise ValueError(f"Unknown S4 reason code(s): {unknown_text}")

    return tuple(
        sorted(
            set(codes),
            key=REASON_CODE_PRIORITY.__getitem__,
        )
    )


def is_registered_base_field(field_name: str) -> bool:
    """Return whether a field is a canonical S4 base field."""

    return field_name in FIELD_DEFINITIONS


def is_forbidden_s4_field(field_name: str) -> bool:
    """Return whether a field violates the S4 ownership boundary."""

    if field_name in FORBIDDEN_S4_FIELDS:
        return True

    return field_name.startswith(FORBIDDEN_S4_PREFIXES)


__all__ = [
    "COMPONENT_ID",
    "COMPONENT_VERSION",
    "SIGNAL_PROFILE_ID",
    "SIGNAL_PROFILE_VERSION",
    "SIGNAL_SCHEMA_ID",
    "SIGNAL_SCHEMA_VERSION",
    "SIGNAL_SCHEMA_REF",
    "EXPECTED_INPUT_SCHEMA_ID",
    "EXPECTED_INPUT_SCHEMA_VERSION",
    "EXPECTED_INPUT_SCHEMA_REF",
    "DISCRETE_PROFILE_ID",
    "DISCRETE_PROFILE_VERSION",
    "CONTINUOUS_PROFILE_ID",
    "CONTINUOUS_PROFILE_VERSION",
    "VALIDITY_PROFILE_ID",
    "VALIDITY_PROFILE_VERSION",
    "REASON_CODE_REGISTRY_VERSION",
    "LEGACY_PROFILE_ID",
    "LEGACY_PROFILE_VERSION",
    "LEGACY_SCHEMA_REF",
    "SIGNAL_METADATA_FIELDS",
    "SIGNAL_METADATA_VALUES",
    "SignalRole",
    "DISCRETE_DIRECTION_FIELDS",
    "DISCRETE_STATE_FIELDS",
    "DISCRETE_BASE_FIELDS",
    "CONTINUOUS_DIRECTION_FIELDS",
    "CONTINUOUS_STATE_FIELDS",
    "CONTINUOUS_BASE_FIELDS",
    "SIGNAL_BASE_FIELDS",
    "FIELD_ROLES",
    "SignalFieldDefinition",
    "FIELD_DEFINITIONS",
    "valid_field_name",
    "reason_codes_field_name",
    "SIGNAL_EXTENSION_FIELDS",
    "EXPECTED_SIGNAL_EXTENSION_FIELD_COUNT",
    "SignalReasonCodeDefinition",
    "REASON_CODE_REGISTRY",
    "REASON_CODE_PRIORITY",
    "FORBIDDEN_S4_FIELDS",
    "FORBIDDEN_S4_PREFIXES",
    "sort_reason_codes",
    "is_registered_base_field",
    "is_forbidden_s4_field",
]
