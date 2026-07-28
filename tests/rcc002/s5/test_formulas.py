"""Pure formula tests for RCC-002 S5."""

from __future__ import annotations

import math
import unittest

from rcc002.s5.constants import (
    RegimeState,
    TrendStrength,
    VolatilityRelative,
)
from rcc002.s5.formulas import (
    RegimeFormulaError,
    SlopeDenominatorInvalid,
    classify_raw_regime,
    classify_trend_strength,
    classify_volatility_relative,
    ma200_slope_1440_pct,
)


class TestSlopeFormula(unittest.TestCase):
    def test_zero_slope(self) -> None:
        self.assertEqual(ma200_slope_1440_pct(100.0, 100.0), 0.0)

    def test_positive_slope(self) -> None:
        self.assertAlmostEqual(
            ma200_slope_1440_pct(110.0, 100.0), 10.0
        )

    def test_negative_slope(self) -> None:
        self.assertAlmostEqual(
            ma200_slope_1440_pct(90.0, 100.0), -10.0
        )

    def test_operation_order_golden_value(self) -> None:
        self.assertEqual(
            ma200_slope_1440_pct(100.0001, 99.9999),
            0.0002000002000013268,
        )

    def test_zero_denominator_rejected(self) -> None:
        with self.assertRaises(SlopeDenominatorInvalid):
            ma200_slope_1440_pct(1.0, 0.0)

    def test_negative_denominator_rejected(self) -> None:
        with self.assertRaises(SlopeDenominatorInvalid):
            ma200_slope_1440_pct(1.0, -1.0)

    def test_bool_and_nonfinite_rejected(self) -> None:
        for value in (True, math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(RegimeFormulaError):
                    ma200_slope_1440_pct(value, 1.0)


class TestClassifiers(unittest.TestCase):
    def test_raw_bull(self) -> None:
        self.assertIs(
            classify_raw_regime(101.0, 100.0, 0.1),
            RegimeState.BULL,
        )

    def test_raw_bear(self) -> None:
        self.assertIs(
            classify_raw_regime(99.0, 100.0, -0.1),
            RegimeState.BEAR,
        )

    def test_raw_side_boundary_cases(self) -> None:
        cases = (
            (100.0, 100.0, 1.0),
            (101.0, 100.0, 0.0),
            (99.0, 100.0, 0.0),
            (101.0, 100.0, -1.0),
            (99.0, 100.0, 1.0),
        )
        for values in cases:
            with self.subTest(values=values):
                self.assertIs(
                    classify_raw_regime(*values), RegimeState.SIDE
                )

    def test_trend_strength_boundaries(self) -> None:
        cases = (
            (0.0, TrendStrength.WEAK),
            (15.0, TrendStrength.WEAK),
            (15.00001, TrendStrength.DEVELOPING),
            (25.0, TrendStrength.DEVELOPING),
            (25.00001, TrendStrength.STRONG),
            (100.0, TrendStrength.STRONG),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertIs(classify_trend_strength(value), expected)

    def test_trend_strength_range_rejected(self) -> None:
        for value in (-0.1, 100.1):
            with self.subTest(value=value):
                with self.assertRaises(RegimeFormulaError):
                    classify_trend_strength(value)

    def test_volatility_mapping(self) -> None:
        cases = (
            (-1, VolatilityRelative.BELOW_REFERENCE),
            (0, VolatilityRelative.AT_REFERENCE),
            (1, VolatilityRelative.ABOVE_REFERENCE),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertIs(
                    classify_volatility_relative(value), expected
                )

    def test_volatility_invalid_values_rejected(self) -> None:
        for value in (True, 2, -2, 0.0):
            with self.subTest(value=value):
                with self.assertRaises(RegimeFormulaError):
                    classify_volatility_relative(value)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
