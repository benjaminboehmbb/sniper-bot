"""Normative constants for RCC-002 S6 gate evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping


COMPONENT_ID: Final[str] = "RCC002_S6_GATE_EVALUATOR"
COMPONENT_VERSION: Final[str] = "0.4.0"

EXPECTED_INPUT_SCHEMA_ID: Final[str] = "rcc002.stage.s5-regimes"
EXPECTED_INPUT_SCHEMA_VERSION: Final[str] = "1.0.0"

GATE_SCHEMA_ID: Final[str] = "rcc002.stage.s6-gates"
GATE_SCHEMA_VERSION: Final[str] = "1.0.0"
GATE_SCHEMA_REF: Final[str] = f"{GATE_SCHEMA_ID}/{GATE_SCHEMA_VERSION}"

GATE_PROFILE_VERSION: Final[str] = "1.0.0"
GATE_RESEARCH_OPEN_V1: Final[str] = "GATE_RESEARCH_OPEN_V1"
GATE_TREND_ALIGNED_V1: Final[str] = "GATE_TREND_ALIGNED_V1"
GATE_TREND_STRENGTH_ALIGNED_V1: Final[str] = (
    "GATE_TREND_STRENGTH_ALIGNED_V1"
)
DEFAULT_GATE_PROFILE_ID: Final[str] = GATE_RESEARCH_OPEN_V1
GATE_PROFILE_IDS: Final[tuple[str, ...]] = (
    GATE_RESEARCH_OPEN_V1,
    GATE_TREND_ALIGNED_V1,
    GATE_TREND_STRENGTH_ALIGNED_V1,
)

REASON_CODE_REGISTRY_VERSION: Final[str] = "1.0.0"
SUPPORTED_INTERVAL: Final[str] = "1m"
INTERVAL_MILLISECONDS: Final[int] = 60_000


class GateState(str, Enum):
    ALLOW_BOTH = "ALLOW_BOTH"
    ALLOW_LONG_ONLY = "ALLOW_LONG_ONLY"
    ALLOW_SHORT_ONLY = "ALLOW_SHORT_ONLY"
    BLOCK_BOTH = "BLOCK_BOTH"
    INVALID = "INVALID"


GATE_EXTENSION_FIELDS: Final[tuple[str, ...]] = (
    "allow_long",
    "allow_short",
    "data_gate_pass",
    "gate_state",
    "gate_reason_codes_long",
    "gate_reason_codes_short",
    "gate_profile_id",
    "gate_profile_version",
    "gate_schema_id",
    "gate_schema_version",
    "gate_schema_ref",
    "gate_valid",
    "gate_evaluated_at",
)

GATE_SCHEMA_METADATA_VALUES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "gate_profile_version": GATE_PROFILE_VERSION,
        "gate_schema_id": GATE_SCHEMA_ID,
        "gate_schema_version": GATE_SCHEMA_VERSION,
        "gate_schema_ref": GATE_SCHEMA_REF,
    }
)


@dataclass(frozen=True, slots=True)
class GateReasonCodeDefinition:
    code: str
    priority: int
    direction: str
    reason_class: str


_REASON_CODES: Final[tuple[GateReasonCodeDefinition, ...]] = (
    GateReasonCodeDefinition(
        "GATE_INPUT_INVALID", 30, "BOTH", "INVALIDATING"
    ),
    GateReasonCodeDefinition(
        "GATE_WARMUP_INCOMPLETE", 40, "BOTH", "INVALIDATING"
    ),
    GateReasonCodeDefinition(
        "GATE_SEGMENT_RESET", 50, "BOTH", "INVALIDATING"
    ),
    GateReasonCodeDefinition(
        "GATE_REGIME_UNKNOWN", 60, "BOTH", "INVALIDATING"
    ),
    GateReasonCodeDefinition(
        "GATE_TREND_STRENGTH_UNKNOWN", 70, "BOTH", "INVALIDATING"
    ),
    GateReasonCodeDefinition(
        "GATE_STATE_INVALID", 80, "BOTH", "INVALIDATING"
    ),
    GateReasonCodeDefinition(
        "GATE_DATA_QUALITY_FAILED", 90, "BOTH", "BLOCKING"
    ),
    GateReasonCodeDefinition(
        "GATE_LONG_BLOCKED_SIDE", 100, "LONG", "BLOCKING"
    ),
    GateReasonCodeDefinition(
        "GATE_LONG_BLOCKED_BEAR", 110, "LONG", "BLOCKING"
    ),
    GateReasonCodeDefinition(
        "GATE_LONG_BLOCKED_WEAK_TREND", 120, "LONG", "BLOCKING"
    ),
    GateReasonCodeDefinition(
        "GATE_SHORT_BLOCKED_SIDE", 130, "SHORT", "BLOCKING"
    ),
    GateReasonCodeDefinition(
        "GATE_SHORT_BLOCKED_BULL", 140, "SHORT", "BLOCKING"
    ),
    GateReasonCodeDefinition(
        "GATE_SHORT_BLOCKED_WEAK_TREND", 150, "SHORT", "BLOCKING"
    ),
    GateReasonCodeDefinition(
        "GATE_LONG_ALLOWED_RESEARCH_OPEN", 160, "LONG", "ALLOWING"
    ),
    GateReasonCodeDefinition(
        "GATE_SHORT_ALLOWED_RESEARCH_OPEN", 170, "SHORT", "ALLOWING"
    ),
    GateReasonCodeDefinition(
        "GATE_LONG_ALLOWED_BULL", 180, "LONG", "ALLOWING"
    ),
    GateReasonCodeDefinition(
        "GATE_SHORT_ALLOWED_BEAR", 190, "SHORT", "ALLOWING"
    ),
    GateReasonCodeDefinition(
        "GATE_LONG_ALLOWED_BULL_WITH_STRENGTH",
        200,
        "LONG",
        "ALLOWING",
    ),
    GateReasonCodeDefinition(
        "GATE_SHORT_ALLOWED_BEAR_WITH_STRENGTH",
        210,
        "SHORT",
        "ALLOWING",
    ),
)

REASON_CODE_REGISTRY: Final[
    Mapping[str, GateReasonCodeDefinition]
] = MappingProxyType({item.code: item for item in _REASON_CODES})
REASON_CODE_PRIORITY: Final[Mapping[str, int]] = MappingProxyType(
    {item.code: item.priority for item in _REASON_CODES}
)

NEUTRAL_REASON_CODES: Final[frozenset[str]] = frozenset(
    item.code for item in _REASON_CODES if item.direction == "BOTH"
)
LONG_REASON_CODES: Final[frozenset[str]] = frozenset(
    item.code for item in _REASON_CODES if item.direction == "LONG"
)
SHORT_REASON_CODES: Final[frozenset[str]] = frozenset(
    item.code for item in _REASON_CODES if item.direction == "SHORT"
)
INVALIDATING_REASON_CODES: Final[frozenset[str]] = frozenset(
    item.code for item in _REASON_CODES
    if item.reason_class == "INVALIDATING"
)
BLOCKING_REASON_CODES: Final[frozenset[str]] = frozenset(
    item.code for item in _REASON_CODES if item.reason_class == "BLOCKING"
)
ALLOWING_REASON_CODES: Final[frozenset[str]] = frozenset(
    item.code for item in _REASON_CODES if item.reason_class == "ALLOWING"
)

if len(GATE_EXTENSION_FIELDS) != 13:
    raise RuntimeError("S6 must add exactly 13 canonical fields")
if len(REASON_CODE_REGISTRY) != 19:
    raise RuntimeError("S6 reason-code registry must contain 19 codes")
if tuple(REASON_CODE_PRIORITY.values()) != tuple(
    range(30, 220, 10)
):
    raise RuntimeError("S6 reason-code priorities must be 30 through 210")


__all__ = [
    "ALLOWING_REASON_CODES",
    "BLOCKING_REASON_CODES",
    "COMPONENT_ID",
    "COMPONENT_VERSION",
    "DEFAULT_GATE_PROFILE_ID",
    "EXPECTED_INPUT_SCHEMA_ID",
    "EXPECTED_INPUT_SCHEMA_VERSION",
    "GATE_EXTENSION_FIELDS",
    "GATE_PROFILE_IDS",
    "GATE_PROFILE_VERSION",
    "GATE_RESEARCH_OPEN_V1",
    "GATE_SCHEMA_ID",
    "GATE_SCHEMA_METADATA_VALUES",
    "GATE_SCHEMA_REF",
    "GATE_SCHEMA_VERSION",
    "GATE_TREND_ALIGNED_V1",
    "GATE_TREND_STRENGTH_ALIGNED_V1",
    "INTERVAL_MILLISECONDS",
    "INVALIDATING_REASON_CODES",
    "LONG_REASON_CODES",
    "NEUTRAL_REASON_CODES",
    "REASON_CODE_PRIORITY",
    "REASON_CODE_REGISTRY",
    "REASON_CODE_REGISTRY_VERSION",
    "SHORT_REASON_CODES",
    "SUPPORTED_INTERVAL",
    "GateReasonCodeDefinition",
    "GateState",
]
