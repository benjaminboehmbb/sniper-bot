"""Hand-calculated S7 formula and barrier tests."""

from __future__ import annotations

import math
import unittest

from rcc002.s7.constants import BarrierOutcome
from rcc002.s7.formulas import (
    barrier_outcomes,
    direction_label,
    excursion_values,
    linear_returns,
    log_returns,
    net_proxy_return,
)


class TestReturns(unittest.TestCase):
    def test_linear_long_short_identity(self) -> None:
        long_return, short_return = linear_returns(100.0, 110.0)
        self.assertAlmostEqual(long_return, 0.1, places=15)
        self.assertAlmostEqual(short_return, -0.1, places=15)
        self.assertAlmostEqual(short_return, -long_return, places=15)

    def test_falling_and_unchanged_prices(self) -> None:
        falling = linear_returns(100.0, 90.0)
        self.assertAlmostEqual(falling[0], -0.1, places=15)
        self.assertEqual(falling[1], -falling[0])
        self.assertEqual(linear_returns(100.0, 100.0), (0.0, 0.0))
        self.assertEqual(direction_label(0.0), 0)
        self.assertEqual(direction_label(1e-20), 1)
        self.assertEqual(direction_label(-1e-20), -1)

    def test_log_and_cost_proxy(self) -> None:
        long_return, short_return = log_returns(100.0, 110.0)
        self.assertEqual(short_return, -long_return)
        self.assertAlmostEqual(long_return, math.log(1.1), places=15)
        self.assertAlmostEqual(net_proxy_return(0.01), 0.0096, places=15)

    def test_nonpositive_price_is_rejected(self) -> None:
        for value in (0.0, -1.0, math.inf, math.nan):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    linear_returns(value, 1.0)


class TestExcursions(unittest.TestCase):
    def test_values_and_first_repeated_extreme(self) -> None:
        values = excursion_values(
            entry_price=100.0,
            highs=(105.0, 110.0, 110.0),
            lows=(99.0, 95.0, 95.0),
        )
        self.assertEqual(values[4:], (2, 2, 2, 2))
        self.assertAlmostEqual(values[0], 0.1, places=15)
        self.assertAlmostEqual(values[1], -0.05, places=15)
        self.assertAlmostEqual(values[2], 0.05, places=15)
        self.assertAlmostEqual(values[3], -0.1, places=15)


class TestBarriers(unittest.TestCase):
    @staticmethod
    def _evaluate(
        rows: tuple[tuple[float, float, float, int], ...]
    ) -> tuple[object, ...]:
        return barrier_outcomes(entry_price=100.0, future_rows=rows)

    def test_exact_tp_and_sl_hits(self) -> None:
        result = self._evaluate(((100.0, 105.0, 99.0, 1),))
        self.assertIs(result[0], BarrierOutcome.TP_FIRST)
        result = self._evaluate(((100.0, 101.0, 98.0, 1),))
        self.assertIs(result[0], BarrierOutcome.SL_FIRST)

    def test_both_hit_is_ambiguous(self) -> None:
        result = self._evaluate(((100.0, 105.0, 98.0, 1),))
        self.assertIs(
            result[0], BarrierOutcome.AMBIGUOUS_BOTH_HIT
        )
        self.assertEqual((result[2], result[4]), (1, 1))

    def test_open_gap_has_priority(self) -> None:
        long_gap = self._evaluate(((106.0, 106.0, 97.0, 1),))
        self.assertIs(long_gap[0], BarrierOutcome.TP_FIRST)
        short_gap = self._evaluate(((94.0, 103.0, 94.0, 1),))
        self.assertIs(short_gap[1], BarrierOutcome.TP_FIRST)

    def test_short_exact_tp_and_sl_hits(self) -> None:
        tp = self._evaluate(((100.0, 101.0, 95.0, 1),))
        self.assertIs(tp[1], BarrierOutcome.TP_FIRST)
        sl = self._evaluate(((100.0, 102.0, 99.0, 1),))
        self.assertIs(sl[1], BarrierOutcome.SL_FIRST)

    def test_short_both_hit_is_ambiguous(self) -> None:
        result = self._evaluate(((100.0, 102.0, 95.0, 1),))
        self.assertIs(
            result[1], BarrierOutcome.AMBIGUOUS_BOTH_HIT
        )

    def test_chronology_and_timeout(self) -> None:
        result = self._evaluate(
            (
                (100.0, 101.0, 99.0, 1),
                (100.0, 105.0, 99.0, 2),
                (100.0, 101.0, 98.0, 3),
            )
        )
        self.assertIs(result[0], BarrierOutcome.TP_FIRST)
        self.assertEqual(result[2], 2)
        timeout = self._evaluate(((100.0, 101.0, 99.0, 1),))
        self.assertIs(timeout[0], BarrierOutcome.TIMEOUT)
        self.assertIsNone(timeout[2])

    def test_sl_then_tp_across_bars_remains_sl_first(self) -> None:
        result = self._evaluate(
            (
                (100.0, 101.0, 98.0, 1),
                (100.0, 105.0, 99.0, 2),
            )
        )
        self.assertIs(result[0], BarrierOutcome.SL_FIRST)
        self.assertEqual(result[2], 1)


if __name__ == "__main__":
    unittest.main()
