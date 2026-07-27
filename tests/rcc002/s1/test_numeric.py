"""Unit tests for rcc002.s1.numeric."""

import math
import unittest

from rcc002.s1.numeric import (
    CRITICAL_NUMERIC_FIELDS,
    NumericParsingError,
    parse_integer_field,
    parse_numeric_field,
)


class ParseNumericFieldTests(unittest.TestCase):
    def test_parses_plain_float(self) -> None:
        self.assertEqual(parse_numeric_field("open", "123.45"), 123.45)

    def test_parses_integer_looking_value(self) -> None:
        self.assertEqual(parse_numeric_field("volume", "100"), 100.0)

    def test_recognizes_nan(self) -> None:
        self.assertTrue(math.isnan(parse_numeric_field("open", "NaN")))

    def test_recognizes_positive_infinity(self) -> None:
        self.assertEqual(parse_numeric_field("open", "+Inf"), float("inf"))

    def test_recognizes_negative_infinity(self) -> None:
        self.assertEqual(parse_numeric_field("open", "-Inf"), float("-inf"))

    def test_no_locale_thousands_separator_ambiguity(self) -> None:
        # A comma is never treated as a thousands separator or decimal
        # separator; such a string is a parsing error, not silently
        # reinterpreted.
        with self.assertRaises(NumericParsingError):
            parse_numeric_field("open", "1,234.5")

    def test_invalid_string_raises(self) -> None:
        with self.assertRaises(NumericParsingError):
            parse_numeric_field("open", "not-a-number")

    def test_ohlcv_field_parsing_error_is_critical(self) -> None:
        try:
            parse_numeric_field("close", "bad")
        except NumericParsingError as exc:
            self.assertTrue(exc.critical)
        else:
            self.fail("expected NumericParsingError")

    def test_no_rounding_applied(self) -> None:
        self.assertEqual(parse_numeric_field("open", "1.123456789"), 1.123456789)


class ParseIntegerFieldTests(unittest.TestCase):
    def test_parses_plain_integer(self) -> None:
        self.assertEqual(parse_integer_field("open_time", "1700000000000"), 1_700_000_000_000)

    def test_invalid_string_raises(self) -> None:
        with self.assertRaises(NumericParsingError):
            parse_integer_field("open_time", "not-a-time")

    def test_open_time_parsing_error_is_critical(self) -> None:
        # §14.1: nulls/invalid values in time fields are CRITICAL, same as
        # OHLCV, even though open_time is not itself an OHLCV field.
        try:
            parse_integer_field("open_time", "bad")
        except NumericParsingError as exc:
            self.assertTrue(exc.critical)
        else:
            self.fail("expected NumericParsingError")

    def test_close_time_parsing_error_is_critical(self) -> None:
        try:
            parse_integer_field("close_time", "bad")
        except NumericParsingError as exc:
            self.assertTrue(exc.critical)
        else:
            self.fail("expected NumericParsingError")


class CriticalFieldSetTests(unittest.TestCase):
    def test_critical_fields_include_ohlcv_and_time(self) -> None:
        self.assertEqual(
            CRITICAL_NUMERIC_FIELDS,
            {"open", "high", "low", "close", "volume", "open_time", "close_time"},
        )


if __name__ == "__main__":
    unittest.main()
