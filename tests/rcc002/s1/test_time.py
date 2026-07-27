"""Unit tests for rcc002.s1.time."""

import unittest

from rcc002.s1.time import (
    UnknownCloseTimeConventionError,
    UnregisteredIntervalError,
    is_interval_aligned,
    require_interval_duration_ms,
    resolve_close_time_ms,
)


class RequireIntervalDurationTests(unittest.TestCase):
    def test_1m_registered_as_60000ms(self) -> None:
        self.assertEqual(require_interval_duration_ms("1m"), 60_000)

    def test_unregistered_interval_raises(self) -> None:
        with self.assertRaises(UnregisteredIntervalError):
            require_interval_duration_ms("5m")


class IsIntervalAlignedTests(unittest.TestCase):
    """`is_interval_aligned` is a pure predicate: no side effect, never
    raises for a misaligned (but registered-interval) value. Ownership of
    the *consequence* of misalignment (DV_TIME_MISALIGNED) belongs to S2 —
    see rcc002.s1.time module docstring and rcc002.s2."""

    def test_aligned_open_time_is_true(self) -> None:
        self.assertTrue(is_interval_aligned(60_000, "1m"))  # one minute after epoch

    def test_misaligned_open_time_is_false(self) -> None:
        self.assertFalse(is_interval_aligned(60_001, "1m"))

    def test_epoch_zero_is_aligned(self) -> None:
        self.assertTrue(is_interval_aligned(0, "1m"))

    def test_unregistered_interval_propagates(self) -> None:
        with self.assertRaises(UnregisteredIntervalError):
            is_interval_aligned(0, "1h")


class ResolveCloseTimeTests(unittest.TestCase):
    def test_source_close_time_is_passed_through(self) -> None:
        result = resolve_close_time_ms(60_000, "1m", source_close_time_ms=123_456)
        self.assertEqual(result, 123_456)

    def test_1m_formula_applied_when_no_source_close_time(self) -> None:
        result = resolve_close_time_ms(60_000, "1m", source_close_time_ms=None)
        self.assertEqual(result, 60_000 + 59_999)

    def test_other_interval_without_source_close_time_raises(self) -> None:
        with self.assertRaises(UnknownCloseTimeConventionError):
            resolve_close_time_ms(0, "5m", source_close_time_ms=None)

    def test_other_interval_with_source_close_time_is_fine(self) -> None:
        result = resolve_close_time_ms(0, "5m", source_close_time_ms=299_999)
        self.assertEqual(result, 299_999)


if __name__ == "__main__":
    unittest.main()
