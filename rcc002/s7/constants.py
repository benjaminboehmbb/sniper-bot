"""Normative constants and expanded logical schema for RCC-002 S7."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Final, Mapping


COMPONENT_ID: Final[str] = "RCC002_S7_LABEL_BUILDER"
COMPONENT_VERSION: Final[str] = "0.3.0"

EXPECTED_INPUT_SCHEMA_ID: Final[str] = "rcc002.stage.s6-gates"
EXPECTED_INPUT_SCHEMA_VERSION: Final[str] = "1.0.0"

LABEL_PROFILE_ID: Final[str] = "RCC002_CANONICAL_LABELS_V1"
LABEL_PROFILE_VERSION: Final[str] = "1.0.0"
LABEL_SCHEMA_ID: Final[str] = "rcc002.stage.s7-labels"
LABEL_SCHEMA_VERSION: Final[str] = "1.0.0"
LABEL_SCHEMA_REF: Final[str] = (
    f"{LABEL_SCHEMA_ID}/{LABEL_SCHEMA_VERSION}"
)
HORIZON_REGISTRY_ID: Final[str] = "RCC002_FORWARD_HORIZONS_V1"
HORIZON_REGISTRY_VERSION: Final[str] = "1.0.0"
COST_PROFILE_ID: Final[str] = "COST_PROXY_FEE_RT_0004_V1"
COST_PROFILE_VERSION: Final[str] = "1.0.0"
BARRIER_PROFILE_ID: Final[str] = "L1_BARRIER_TP050_SL020_V1"
BARRIER_PROFILE_VERSION: Final[str] = "1.0.0"
REASON_CODE_REGISTRY_VERSION: Final[str] = "1.0.0"
NUMERIC_PROFILE_ID: Final[str] = "RCC002_FLOAT64_LABEL_NUMERICS_V1"
NUMERIC_PROFILE_VERSION: Final[str] = "1.0.0"

SUPPORTED_INTERVAL: Final[str] = "1m"
INTERVAL_MILLISECONDS: Final[int] = 60_000
TOTAL_COST_FRACTION: Final[float] = 0.0004
TAKE_PROFIT_FRACTION: Final[float] = 0.05
STOP_LOSS_FRACTION: Final[float] = 0.02
ABSOLUTE_TOLERANCE: Final[float] = 1e-12
RELATIVE_TOLERANCE: Final[float] = 1e-10


@dataclass(frozen=True, slots=True)
class HorizonDefinition:
    horizon_id: str
    bars: int
    suffix: str


HORIZONS: Final[tuple[HorizonDefinition, ...]] = (
    HorizonDefinition("H001", 1, "h001"),
    HorizonDefinition("H005", 5, "h005"),
    HorizonDefinition("H015", 15, "h015"),
    HorizonDefinition("H060", 60, "h060"),
    HorizonDefinition("H240", 240, "h240"),
    HorizonDefinition("H1440", 1440, "h1440"),
)
HORIZON_IDS: Final[tuple[str, ...]] = tuple(
    item.horizon_id for item in HORIZONS
)
HORIZON_BY_ID: Final[Mapping[str, HorizonDefinition]] = (
    MappingProxyType({item.horizon_id: item for item in HORIZONS})
)
MAX_HORIZON: Final[int] = max(item.bars for item in HORIZONS)


class BarrierOutcome(str, Enum):
    TP_FIRST = "TP_FIRST"
    SL_FIRST = "SL_FIRST"
    TIMEOUT = "TIMEOUT"
    AMBIGUOUS_BOTH_HIT = "AMBIGUOUS_BOTH_HIT"
    INVALID = "INVALID"


LABEL_METADATA_FIELDS: Final[tuple[str, ...]] = (
    "label_profile_id",
    "label_profile_version",
    "label_schema_id",
    "label_schema_version",
    "label_schema_ref",
    "horizon_registry_id",
    "horizon_registry_version",
    "cost_profile_id",
    "cost_profile_version",
    "barrier_profile_id",
    "barrier_profile_version",
    "label_reason_code_registry_version",
    "label_numeric_profile_id",
    "label_numeric_profile_version",
)

LABEL_METADATA_VALUES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "label_profile_id": LABEL_PROFILE_ID,
        "label_profile_version": LABEL_PROFILE_VERSION,
        "label_schema_id": LABEL_SCHEMA_ID,
        "label_schema_version": LABEL_SCHEMA_VERSION,
        "label_schema_ref": LABEL_SCHEMA_REF,
        "horizon_registry_id": HORIZON_REGISTRY_ID,
        "horizon_registry_version": HORIZON_REGISTRY_VERSION,
        "cost_profile_id": COST_PROFILE_ID,
        "cost_profile_version": COST_PROFILE_VERSION,
        "barrier_profile_id": BARRIER_PROFILE_ID,
        "barrier_profile_version": BARRIER_PROFILE_VERSION,
        "label_reason_code_registry_version": (
            REASON_CODE_REGISTRY_VERSION
        ),
        "label_numeric_profile_id": NUMERIC_PROFILE_ID,
        "label_numeric_profile_version": NUMERIC_PROFILE_VERSION,
    }
)

# Exact §36.2 per-horizon order after the 14 S7 metadata fields.
HORIZON_LOCAL_FIELDS: Final[tuple[str, ...]] = (
    "label_horizon_bars",
    "label_available_at",
    "fwd_cc_valid",
    "fwd_cc_reason_codes",
    "fwd_cc_label_segment_id",
    "fwd_cc_long_ret",
    "fwd_cc_short_ret",
    "fwd_cc_log_ret",
    "fwd_cc_short_log_ret",
    "fwd_noc_valid",
    "fwd_noc_reason_codes",
    "fwd_noc_label_segment_id",
    "fwd_noc_long_ret",
    "fwd_noc_short_ret",
    "fwd_noc_long_net_proxy_fee_rt_0004",
    "fwd_noc_short_net_proxy_fee_rt_0004",
    "fwd_excursion_valid",
    "fwd_excursion_reason_codes",
    "fwd_excursion_label_segment_id",
    "fwd_long_mfe",
    "fwd_long_mae",
    "fwd_short_mfe",
    "fwd_short_mae",
    "fwd_long_mfe_first_bar",
    "fwd_long_mae_first_bar",
    "fwd_short_mfe_first_bar",
    "fwd_short_mae_first_bar",
    "label_cc_direction_valid",
    "label_cc_direction_reason_codes",
    "label_cc_direction_segment_id",
    "label_cc_long_direction",
    "label_cc_short_direction",
    "label_noc_direction_valid",
    "label_noc_direction_reason_codes",
    "label_noc_direction_segment_id",
    "label_noc_long_direction",
    "label_noc_short_direction",
    "label_noc_long_net_proxy_fee_rt_0004_direction",
    "label_noc_short_net_proxy_fee_rt_0004_direction",
    "barrier_valid",
    "barrier_reason_codes",
    "barrier_label_segment_id",
    "barrier_long_outcome_tp050_sl020",
    "barrier_short_outcome_tp050_sl020",
    "barrier_long_first_hit_bar_tp050_sl020",
    "barrier_short_first_hit_bar_tp050_sl020",
    "barrier_long_first_hit_time_tp050_sl020",
    "barrier_short_first_hit_time_tp050_sl020",
)


def expanded_horizon_field_name(
    local_name: str,
    suffix: str,
) -> str:
    return f"{local_name}_{suffix}"


LABEL_EXTENSION_FIELDS: Final[tuple[str, ...]] = (
    LABEL_METADATA_FIELDS
    + tuple(
        expanded_horizon_field_name(local_name, horizon.suffix)
        for horizon in HORIZONS
        for local_name in HORIZON_LOCAL_FIELDS
    )
)


@dataclass(frozen=True, slots=True)
class LabelFieldDefinition:
    name: str
    logical_type: str
    nullable: bool
    field_owner_stage: str = "S7_LABELS"
    leakage_class: str = "FUTURE_OUTCOME"
    live_allowed: bool = False
    paper_allowed: bool = False
    backtest_input_allowed: bool = False
    research_feature_allowed: bool = False
    label_research_allowed: bool = True


def _local_field_type(local_name: str) -> tuple[str, bool]:
    if local_name == "label_horizon_bars":
        return "UInt16", False
    if local_name == "label_available_at":
        return "TimestampUTCms", True
    if local_name.endswith("_valid"):
        return "Boolean", False
    if local_name.endswith("_reason_codes"):
        return "OrderedList[Utf8]", False
    if local_name.endswith(("_segment_id", "_label_segment_id")):
        return "Utf8", True
    if "outcome_tp050_sl020" in local_name:
        return "BarrierOutcome", False
    if "first_hit_time" in local_name:
        return "TimestampUTCms", True
    if "first_bar" in local_name or "first_hit_bar" in local_name:
        return "UInt16", True
    if "direction" in local_name:
        return "Int8", True
    return "Float64", True


_FIELD_REGISTRY_ITEMS: Final[tuple[LabelFieldDefinition, ...]] = (
    tuple(
        LabelFieldDefinition(name, "Utf8", False)
        for name in LABEL_METADATA_FIELDS
    )
    + tuple(
        LabelFieldDefinition(
            expanded_horizon_field_name(local_name, horizon.suffix),
            *_local_field_type(local_name),
        )
        for horizon in HORIZONS
        for local_name in HORIZON_LOCAL_FIELDS
    )
)
S7_FIELD_REGISTRY: Final[Mapping[str, LabelFieldDefinition]] = (
    MappingProxyType(
        {definition.name: definition for definition in _FIELD_REGISTRY_ITEMS}
    )
)


def _canonical_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


LABEL_SCHEMA_FINGERPRINT_SHA256: Final[str] = _canonical_sha256(
    {
        "input_schema": [
            EXPECTED_INPUT_SCHEMA_ID,
            EXPECTED_INPUT_SCHEMA_VERSION,
        ],
        "preserve_input_fields_in_order": True,
        "extension_fields": [
            {
                "name": item.name,
                "logical_type": item.logical_type,
                "nullable": item.nullable,
                "field_owner_stage": item.field_owner_stage,
                "leakage_class": item.leakage_class,
                "live_allowed": item.live_allowed,
                "paper_allowed": item.paper_allowed,
                "backtest_input_allowed": (
                    item.backtest_input_allowed
                ),
                "research_feature_allowed": (
                    item.research_feature_allowed
                ),
                "label_research_allowed": (
                    item.label_research_allowed
                ),
            }
            for item in _FIELD_REGISTRY_ITEMS
        ],
    }
)
SEMANTIC_BUILD_CONFIGURATION_SHA256: Final[str] = _canonical_sha256(
    {
        "label_profile": [LABEL_PROFILE_ID, LABEL_PROFILE_VERSION],
        "schema": [LABEL_SCHEMA_ID, LABEL_SCHEMA_VERSION],
        "horizons": [
            [item.horizon_id, item.bars, item.suffix]
            for item in HORIZONS
        ],
        "cost_profile": [
            COST_PROFILE_ID,
            COST_PROFILE_VERSION,
            TOTAL_COST_FRACTION,
        ],
        "barrier_profile": [
            BARRIER_PROFILE_ID,
            BARRIER_PROFILE_VERSION,
            TAKE_PROFIT_FRACTION,
            STOP_LOSS_FRACTION,
            "OPEN_GAP_FIRST_THEN_AMBIGUOUS_BOTH_HIT",
        ],
        "reason_registry_version": REASON_CODE_REGISTRY_VERSION,
        "validity": [
            "FULL_EXACT_1M_HORIZON",
            "SAME_MARKET_SEGMENT_T_THROUGH_T_PLUS_H",
            "OBSERVED_NONSYNTHETIC_QUALITY_VALIDATED",
            "FAMILY_LOCAL_USED_PRICE_ROW_QUALITY",
            "TAIL_INCOMPLETE_EXCLUSIVE",
            "FAMILY_LOCAL_NULL_SEMANTICS",
        ],
        "incremental_invalidation": "K_MINUS_1440_THROUGH_K",
        "numeric_profile": [
            NUMERIC_PROFILE_ID,
            NUMERIC_PROFILE_VERSION,
            "IEEE754_FLOAT64",
            "NO_FMA",
            "NO_INTERMEDIATE_ROUNDING",
            "NEGATIVE_ZERO_TO_POSITIVE_ZERO",
            "PYTHON_MATH_LOG",
        ],
    }
)


@dataclass(frozen=True, slots=True)
class LabelReasonCodeDefinition:
    code: str
    priority: int
    scope: str
    invalidating: bool


_REASON_CODES: Final[tuple[LabelReasonCodeDefinition, ...]] = (
    LabelReasonCodeDefinition("LBL_SCHEMA_MISMATCH", 10, "STAGE", True),
    LabelReasonCodeDefinition("LBL_PROFILE_MISMATCH", 20, "STAGE", True),
    LabelReasonCodeDefinition(
        "LBL_HORIZON_PROFILE_UNKNOWN", 30, "STAGE", True
    ),
    LabelReasonCodeDefinition(
        "LBL_COST_PROFILE_UNKNOWN", 40, "STAGE", True
    ),
    LabelReasonCodeDefinition(
        "LBL_BARRIER_PROFILE_UNKNOWN", 50, "STAGE", True
    ),
    LabelReasonCodeDefinition(
        "LBL_INTERVAL_UNSUPPORTED", 60, "STAGE", True
    ),
    LabelReasonCodeDefinition("LBL_INPUT_INVALID", 100, "ALL", True),
    LabelReasonCodeDefinition(
        "LBL_FUTURE_HORIZON_INCOMPLETE", 110, "ALL", True
    ),
    LabelReasonCodeDefinition(
        "LBL_WINDOW_CROSSES_MARKET_SEGMENT", 120, "ALL", True
    ),
    LabelReasonCodeDefinition(
        "LBL_FUTURE_BAR_QUALITY_FAILED", 130, "ALL", True
    ),
    LabelReasonCodeDefinition(
        "LBL_SYNTHETIC_INPUT_DISALLOWED", 140, "ALL", True
    ),
    LabelReasonCodeDefinition(
        "LBL_ENTRY_PRICE_INVALID", 150, "ENTRY", True
    ),
    LabelReasonCodeDefinition(
        "LBL_EXIT_PRICE_INVALID", 160, "EXIT", True
    ),
    LabelReasonCodeDefinition(
        "LBL_NONFINITE_RESULT", 170, "NUMERIC", True
    ),
    LabelReasonCodeDefinition(
        "LBL_BARRIER_BOTH_HIT", 180, "BARRIER", False
    ),
    LabelReasonCodeDefinition(
        "LBL_BARRIER_TIMEOUT", 190, "BARRIER", False
    ),
)
REASON_CODE_REGISTRY: Final[
    Mapping[str, LabelReasonCodeDefinition]
] = MappingProxyType({item.code: item for item in _REASON_CODES})
REASON_CODE_PRIORITY: Final[Mapping[str, int]] = MappingProxyType(
    {item.code: item.priority for item in _REASON_CODES}
)
STAGE_REASON_CODES: Final[frozenset[str]] = frozenset(
    item.code for item in _REASON_CODES if item.scope == "STAGE"
)
ROW_REASON_CODES: Final[frozenset[str]] = (
    frozenset(REASON_CODE_REGISTRY) - STAGE_REASON_CODES
)
INVALIDATING_REASON_CODES: Final[frozenset[str]] = frozenset(
    item.code for item in _REASON_CODES if item.invalidating
)

if len(HORIZON_LOCAL_FIELDS) != 48:
    raise RuntimeError("S7 must expand exactly 48 fields per horizon")
if len(LABEL_EXTENSION_FIELDS) != 302:
    raise RuntimeError("S7 must add exactly 302 canonical fields")
if tuple(S7_FIELD_REGISTRY) != LABEL_EXTENSION_FIELDS:
    raise RuntimeError("S7 field registry order is not canonical")
if len(REASON_CODE_REGISTRY) != 16:
    raise RuntimeError("S7 reason-code registry must contain 16 codes")


__all__ = [
    "ABSOLUTE_TOLERANCE",
    "BARRIER_PROFILE_ID",
    "BARRIER_PROFILE_VERSION",
    "COMPONENT_ID",
    "COMPONENT_VERSION",
    "COST_PROFILE_ID",
    "COST_PROFILE_VERSION",
    "EXPECTED_INPUT_SCHEMA_ID",
    "EXPECTED_INPUT_SCHEMA_VERSION",
    "HORIZONS",
    "HORIZON_BY_ID",
    "HORIZON_IDS",
    "HORIZON_LOCAL_FIELDS",
    "HORIZON_REGISTRY_ID",
    "HORIZON_REGISTRY_VERSION",
    "INTERVAL_MILLISECONDS",
    "INVALIDATING_REASON_CODES",
    "LABEL_EXTENSION_FIELDS",
    "LABEL_METADATA_FIELDS",
    "LABEL_METADATA_VALUES",
    "LABEL_PROFILE_ID",
    "LABEL_PROFILE_VERSION",
    "LABEL_SCHEMA_ID",
    "LABEL_SCHEMA_FINGERPRINT_SHA256",
    "LABEL_SCHEMA_REF",
    "LABEL_SCHEMA_VERSION",
    "MAX_HORIZON",
    "NUMERIC_PROFILE_ID",
    "NUMERIC_PROFILE_VERSION",
    "REASON_CODE_PRIORITY",
    "REASON_CODE_REGISTRY",
    "REASON_CODE_REGISTRY_VERSION",
    "RELATIVE_TOLERANCE",
    "ROW_REASON_CODES",
    "S7_FIELD_REGISTRY",
    "SEMANTIC_BUILD_CONFIGURATION_SHA256",
    "STAGE_REASON_CODES",
    "STOP_LOSS_FRACTION",
    "SUPPORTED_INTERVAL",
    "TAKE_PROFIT_FRACTION",
    "TOTAL_COST_FRACTION",
    "BarrierOutcome",
    "HorizonDefinition",
    "LabelReasonCodeDefinition",
    "LabelFieldDefinition",
    "expanded_horizon_field_name",
]
