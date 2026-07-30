"""Independent fixed-output fixtures for the three S6 profiles."""

from __future__ import annotations

import unittest

from rcc002.s5.constants import RegimeState, TrendStrength
from rcc002.s6.compute import compute_gates
from rcc002.s6.constants import (
    GATE_RESEARCH_OPEN_V1,
    GATE_TREND_ALIGNED_V1,
    GATE_TREND_STRENGTH_ALIGNED_V1,
)
from tests.rcc002.s6._helpers import valid_s5_row


def _projection(row) -> tuple[object, ...]:
    return (
        row.allow_long,
        row.allow_short,
        row.gate_valid,
        row.gate_state.value,
        row.gate_reason_codes_long,
        row.gate_reason_codes_short,
    )


class TestGoldenFixtures(unittest.TestCase):
    def test_research_open_fixture(self) -> None:
        actual = compute_gates(
            (
                valid_s5_row(
                    regime=RegimeState.BEAR,
                    strength=TrendStrength.WEAK,
                ),
            ),
            gate_profile_id=GATE_RESEARCH_OPEN_V1,
        ).rows[0]
        self.assertEqual(
            _projection(actual),
            (
                True,
                True,
                True,
                "ALLOW_BOTH",
                ("GATE_LONG_ALLOWED_RESEARCH_OPEN",),
                ("GATE_SHORT_ALLOWED_RESEARCH_OPEN",),
            ),
        )

    def test_trend_aligned_bear_fixture(self) -> None:
        actual = compute_gates(
            (valid_s5_row(regime=RegimeState.BEAR),),
            gate_profile_id=GATE_TREND_ALIGNED_V1,
        ).rows[0]
        self.assertEqual(
            _projection(actual),
            (
                False,
                True,
                True,
                "ALLOW_SHORT_ONLY",
                ("GATE_LONG_BLOCKED_BEAR",),
                ("GATE_SHORT_ALLOWED_BEAR",),
            ),
        )

    def test_strength_aligned_weak_side_fixture(self) -> None:
        actual = compute_gates(
            (
                valid_s5_row(
                    regime=RegimeState.SIDE,
                    strength=TrendStrength.WEAK,
                ),
            ),
            gate_profile_id=GATE_TREND_STRENGTH_ALIGNED_V1,
        ).rows[0]
        self.assertEqual(
            _projection(actual),
            (
                False,
                False,
                True,
                "BLOCK_BOTH",
                (
                    "GATE_LONG_BLOCKED_SIDE",
                    "GATE_LONG_BLOCKED_WEAK_TREND",
                ),
                (
                    "GATE_SHORT_BLOCKED_SIDE",
                    "GATE_SHORT_BLOCKED_WEAK_TREND",
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
