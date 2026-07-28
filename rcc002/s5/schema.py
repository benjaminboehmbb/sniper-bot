"""Canonical in-memory S5 regime row schema."""

from __future__ import annotations

import dataclasses
import math
from numbers import Integral, Real

from rcc002.s4.schema import S4Row
from rcc002.s5.constants import (
    CONFIRM_BARS,
    REGIME_METADATA_VALUES,
    REGIME_REASON_CODES,
    TREND_STRENGTH_REASON_CODES,
    VOLATILITY_REASON_CODES,
    RegimeState,
    TrendStrength,
    VolatilityRelative,
)
from rcc002.s5.reason_codes import normalize_reason_codes


@dataclasses.dataclass(frozen=True)
class S5Row(S4Row):
    regime_raw: RegimeState
    regime_effective: RegimeState
    regime_candidate: RegimeState
    regime_candidate_count: int
    regime_transition_flag: bool
    regime_transition_from: RegimeState | None
    regime_transition_to: RegimeState | None
    ma200_slope_1440_pct: float | None
    trend_strength: TrendStrength
    trend_strength_valid: bool
    trend_strength_reason_codes: tuple[str, ...]
    volatility_relative: VolatilityRelative
    volatility_relative_valid: bool
    volatility_relative_reason_codes: tuple[str, ...]
    regime_model_id: str
    regime_model_version: str
    regime_schema_id: str
    regime_schema_version: str
    regime_schema_ref: str
    regime_valid: bool
    regime_reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        for name, value in REGIME_METADATA_VALUES.items():
            if getattr(self, name) != value:
                raise ValueError(
                    f"{name} must equal {value!r}"
                )
        for name, enum_type in (
            ("regime_raw", RegimeState),
            ("regime_effective", RegimeState),
            ("regime_candidate", RegimeState),
            ("trend_strength", TrendStrength),
            ("volatility_relative", VolatilityRelative),
        ):
            if not isinstance(getattr(self, name), enum_type):
                raise ValueError(f"{name} must be a {enum_type.__name__}")
        if (
            isinstance(self.regime_candidate_count, bool)
            or not isinstance(self.regime_candidate_count, Integral)
            or not 0 <= int(self.regime_candidate_count) <= CONFIRM_BARS
        ):
            raise ValueError(
                "regime_candidate_count must be an integer from 0 to 3"
            )
        if type(self.regime_transition_flag) is not bool:
            raise ValueError("regime_transition_flag must be Boolean")
        if self.ma200_slope_1440_pct is not None:
            if (
                isinstance(self.ma200_slope_1440_pct, bool)
                or not isinstance(self.ma200_slope_1440_pct, Real)
                or not math.isfinite(float(self.ma200_slope_1440_pct))
            ):
                raise ValueError(
                    "ma200_slope_1440_pct must be finite or None"
                )
        for name in (
            "trend_strength_reason_codes",
            "volatility_relative_reason_codes",
            "regime_reason_codes",
        ):
            codes = getattr(self, name)
            if not isinstance(codes, tuple):
                raise ValueError(f"{name} must be a tuple")
            if codes != normalize_reason_codes(codes):
                raise ValueError(f"{name} is not canonically ordered")
        self._validate_context()
        self._validate_transition()
        self._validate_regime()

    def _validate_context(self) -> None:
        if type(self.trend_strength_valid) is not bool:
            raise ValueError("trend_strength_valid must be Boolean")
        if self.trend_strength_valid:
            if self.trend_strength is TrendStrength.UNKNOWN:
                raise ValueError("valid trend strength cannot be UNKNOWN")
            if self.trend_strength_reason_codes:
                raise ValueError("valid trend strength has reason codes")
        elif self.trend_strength is not TrendStrength.UNKNOWN:
            raise ValueError("invalid trend strength must be UNKNOWN")
        elif (
            set(self.trend_strength_reason_codes)
            != TREND_STRENGTH_REASON_CODES
        ):
            raise ValueError(
                "invalid trend strength requires its field-local reason"
            )

        if type(self.volatility_relative_valid) is not bool:
            raise ValueError("volatility_relative_valid must be Boolean")
        if self.volatility_relative_valid:
            if self.volatility_relative is VolatilityRelative.UNKNOWN:
                raise ValueError("valid volatility cannot be UNKNOWN")
            if self.volatility_relative_reason_codes:
                raise ValueError("valid volatility has reason codes")
        elif self.volatility_relative is not VolatilityRelative.UNKNOWN:
            raise ValueError("invalid volatility must be UNKNOWN")
        elif (
            set(self.volatility_relative_reason_codes)
            != VOLATILITY_REASON_CODES
        ):
            raise ValueError(
                "invalid volatility requires its field-local reason"
            )

    def _validate_transition(self) -> None:
        if self.regime_transition_flag:
            if (
                not isinstance(self.regime_transition_from, RegimeState)
                or not isinstance(self.regime_transition_to, RegimeState)
                or
                self.regime_transition_from is self.regime_transition_to
            ):
                raise ValueError("invalid regime transition")
            if self.regime_effective is not self.regime_transition_to:
                raise ValueError("transition target must be effective")
        elif (
            self.regime_transition_from is not None
            or self.regime_transition_to is not None
        ):
            raise ValueError(
                "non-transition rows require null transition endpoints"
            )

    def _validate_regime(self) -> None:
        if type(self.regime_valid) is not bool:
            raise ValueError("regime_valid must be Boolean")
        if self.regime_valid:
            if (
                self.regime_raw is RegimeState.UNKNOWN
                or self.regime_effective is RegimeState.UNKNOWN
                or self.ma200_slope_1440_pct is None
                or self.regime_reason_codes
            ):
                raise ValueError("valid regime row is internally inconsistent")
        elif not self.regime_reason_codes:
            raise ValueError("invalid regime row requires a reason code")
        elif not (
            self.regime_raw is RegimeState.UNKNOWN
            or self.regime_effective is RegimeState.UNKNOWN
        ):
            raise ValueError(
                "invalid regime requires raw or effective UNKNOWN"
            )
        if not set(self.regime_reason_codes).issubset(
            REGIME_REASON_CODES
        ):
            raise ValueError(
                "regime_reason_codes contains a context reason"
            )


__all__ = ["S5Row"]
