"""Unit tests for rcc002.s2.invariants."""

import math
import unittest

from rcc002.s2.invariants import check_ohlcv_invariants


def check(**overrides):
    fields = dict(open=1.0, high=2.0, low=0.5, close=1.5, volume=100.0)
    fields.update(overrides)
    return check_ohlcv_invariants(**fields)


class ValidRowTests(unittest.TestCase):
    def test_valid_row_passes_all(self) -> None:
        result = check()
        self.assertTrue(result.ohlc_valid)
        self.assertTrue(result.volume_valid)
        self.assertFalse(result.ohlc_invariant_violated)
        self.assertFalse(result.volume_negative)
        self.assertFalse(result.volume_zero_observed)
        self.assertEqual(result.nonfinite_fields, ())


class OhlcHardRuleTests(unittest.TestCase):
    def test_open_not_positive_invalid(self) -> None:
        self.assertTrue(check(open=0.0).ohlc_invariant_violated)

    def test_high_not_positive_invalid(self) -> None:
        self.assertTrue(check(high=0.0).ohlc_invariant_violated)

    def test_low_not_positive_invalid(self) -> None:
        self.assertTrue(check(low=0.0).ohlc_invariant_violated)

    def test_close_not_positive_invalid(self) -> None:
        self.assertTrue(check(close=0.0).ohlc_invariant_violated)

    def test_high_less_than_open_invalid(self) -> None:
        self.assertTrue(check(high=0.5, open=1.0).ohlc_invariant_violated)

    def test_high_less_than_close_invalid(self) -> None:
        self.assertTrue(check(high=0.5, close=1.0).ohlc_invariant_violated)

    def test_high_less_than_low_invalid(self) -> None:
        self.assertTrue(check(high=0.4, low=0.5).ohlc_invariant_violated)

    def test_low_greater_than_open_invalid(self) -> None:
        self.assertTrue(check(low=2.0, open=1.0, high=3.0).ohlc_invariant_violated)

    def test_low_greater_than_close_invalid(self) -> None:
        self.assertTrue(check(low=2.0, close=1.0, high=3.0).ohlc_invariant_violated)

    def test_violation_marks_ohlc_invalid(self) -> None:
        self.assertFalse(check(open=0.0).ohlc_valid)


class VolumeRuleTests(unittest.TestCase):
    def test_negative_volume_invalid(self) -> None:
        result = check(volume=-1.0)
        self.assertTrue(result.volume_negative)
        self.assertFalse(result.volume_valid)

    def test_zero_volume_observed_but_valid(self) -> None:
        result = check(volume=0.0)
        self.assertTrue(result.volume_zero_observed)
        self.assertTrue(result.volume_valid)
        self.assertFalse(result.volume_negative)

    def test_positive_volume_no_flags(self) -> None:
        result = check(volume=5.0)
        self.assertFalse(result.volume_zero_observed)
        self.assertFalse(result.volume_negative)


class NonfiniteTests(unittest.TestCase):
    def test_nan_close_flagged_and_ohlc_invalid(self) -> None:
        result = check(close=math.nan)
        self.assertIn("close", result.nonfinite_fields)
        self.assertFalse(result.ohlc_valid)
        self.assertFalse(result.ohlc_invariant_violated)  # skipped, not evaluated

    def test_inf_volume_flagged_and_volume_invalid(self) -> None:
        result = check(volume=math.inf)
        self.assertIn("volume", result.nonfinite_fields)
        self.assertFalse(result.volume_valid)
        self.assertFalse(result.volume_negative)
        self.assertFalse(result.volume_zero_observed)

    def test_negative_inf_open_flagged(self) -> None:
        result = check(open=-math.inf)
        self.assertIn("open", result.nonfinite_fields)
        self.assertFalse(result.ohlc_valid)


if __name__ == "__main__":
    unittest.main()
