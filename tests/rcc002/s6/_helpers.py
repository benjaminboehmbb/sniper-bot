"""Shared deterministic S6 test fixtures."""

from __future__ import annotations

import dataclasses
from functools import lru_cache

from rcc002.s4.compute import compute_signals
from rcc002.s5.compute import compute_regimes
from rcc002.s5.constants import RegimeState, TrendStrength
from rcc002.s5.schema import S5Row
from tests.rcc002.s4.test_compute import _make_rows


@lru_cache(maxsize=1)
def canonical_s5_rows() -> tuple[S5Row, ...]:
    s4_rows = compute_signals(_make_rows(1_445)).rows
    return compute_regimes(
        s4_rows, parent_build_id="s6-test-build"
    ).rows


def valid_s5_row(
    *,
    regime: RegimeState = RegimeState.SIDE,
    strength: TrendStrength = TrendStrength.DEVELOPING,
) -> S5Row:
    row = canonical_s5_rows()[-1]
    slope = {
        RegimeState.BULL: 1.0,
        RegimeState.SIDE: 0.0,
        RegimeState.BEAR: -1.0,
    }[regime]
    return dataclasses.replace(
        row,
        regime_raw=regime,
        regime_effective=regime,
        regime_candidate=regime,
        regime_candidate_count=3,
        regime_transition_flag=False,
        regime_transition_from=None,
        regime_transition_to=None,
        ma200_slope_1440_pct=slope,
        regime_valid=True,
        regime_reason_codes=(),
        trend_strength=strength,
        trend_strength_valid=True,
        trend_strength_reason_codes=(),
    )


def invalid_regime_row() -> S5Row:
    return canonical_s5_rows()[0]


def failed_quality_row() -> S5Row:
    return dataclasses.replace(
        invalid_regime_row(),
        quality_gate_pass=False,
        quality_status="ERROR",
        quality_reason_codes=("DV_NUMERIC_PARSE_FAILED",),
        regime_reason_codes=(
            "REG_INPUT_QUALITY_GATE_FAILED",
            "REG_WARMUP_INCOMPLETE",
        ),
    )


def invalid_strength_row() -> S5Row:
    return dataclasses.replace(
        valid_s5_row(regime=RegimeState.BULL),
        trend_strength=TrendStrength.UNKNOWN,
        trend_strength_valid=False,
        trend_strength_reason_codes=(
            "REG_TREND_STRENGTH_INPUT_INVALID",
        ),
    )
