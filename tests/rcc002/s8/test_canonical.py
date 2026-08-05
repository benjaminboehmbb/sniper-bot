"""Golden and oracle tests for rcc002.s8.canonical.

Mandatory S8 test items 7 (independent canonicalization/identity-preimage
oracles) and 8 (JCS, NFC, decimal, timestamp, non-finite golden cases).

This file is ASCII-only: every non-ASCII test value is written as an
explicit \\uXXXX escape sequence rather than a literal character.
"""

from __future__ import annotations

import datetime
import decimal
import hashlib
import json
import unittest

from rcc002.s8.canonical import (
    canonical_bytes,
    canonical_sha256,
    format_canonical_decimal,
    format_utc_timestamp,
    reject_non_finite,
    sha256_hex,
)
from rcc002.s8.reason_codes import CanonicalizationError


class TestJcsGoldenCases(unittest.TestCase):
    """Item 8: RFC 8785/JCS golden cases."""

    def test_key_sorting_and_compact_separators(self) -> None:
        self.assertEqual(
            canonical_bytes({"b": 2, "a": 1}),
            b'{"a":1,"b":2}',
        )

    def test_nested_object_and_array_preserve_array_order(self) -> None:
        value = {"z": [3, 1, 2], "a": {"y": True, "x": None}}
        self.assertEqual(
            canonical_bytes(value),
            b'{"a":{"x":null,"y":true},"z":[3,1,2]}',
        )

    def test_empty_object_and_array(self) -> None:
        self.assertEqual(canonical_bytes({}), b"{}")
        self.assertEqual(canonical_bytes([]), b"[]")

    def test_no_insignificant_whitespace(self) -> None:
        data = canonical_bytes({"a": [1, 2], "b": "x"})
        self.assertNotIn(b" ", data)
        self.assertNotIn(b"\n", data)

    def test_duplicate_canonicalization_is_deterministic(self) -> None:
        value = {"k" + str(i): i for i in range(20)}
        self.assertEqual(canonical_bytes(value), canonical_bytes(dict(value)))


class TestNfcGoldenCases(unittest.TestCase):
    """Item 8: Unicode NFC normalization golden cases."""

    def test_combining_accent_normalizes_to_precomposed(self) -> None:
        # "e" + COMBINING ACUTE ACCENT (U+0065 U+0301) versus the
        # precomposed LATIN SMALL LETTER E WITH ACUTE (U+00E9).
        decomposed = "e" + "\u0301"
        precomposed = "\u00e9"
        self.assertEqual(
            canonical_bytes({"name": decomposed}),
            canonical_bytes({"name": precomposed}),
        )
        self.assertEqual(
            canonical_bytes({"name": decomposed}),
            f'{{"name":"{precomposed}"}}'.encode("utf-8"),
        )

    def test_nfc_applies_to_object_keys_too(self) -> None:
        decomposed_key = "e" + "\u0301" + "tat"
        precomposed_key = "\u00e9tat"
        self.assertEqual(
            canonical_bytes({decomposed_key: 1}),
            canonical_bytes({precomposed_key: 1}),
        )


class TestDecimalGoldenCases(unittest.TestCase):
    """Item 8: canonical decimal string golden cases (Spec SS6.3)."""

    def test_golden_table(self) -> None:
        cases = [
            (decimal.Decimal("-0"), "0"),
            (decimal.Decimal("0"), "0"),
            ("3.140", "3.14"),
            (100, "100"),
            ("0.05", "0.05"),
            ("-1.500", "-1.5"),
            ("-0.0", "0"),
            ("007", "7"),
            (decimal.Decimal("1E+2"), "100"),
            ("0.00", "0"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(format_canonical_decimal(raw), expected)

    def test_rejects_leading_plus_input_is_still_normalized(self) -> None:
        # decimal.Decimal accepts a leading '+' on parse; the canonical
        # *output* must never carry one.
        self.assertEqual(format_canonical_decimal("+5.5"), "5.5")

    def test_rejects_binary_float(self) -> None:
        with self.assertRaises(CanonicalizationError):
            format_canonical_decimal(1.5)

    def test_rejects_boolean(self) -> None:
        with self.assertRaises(CanonicalizationError):
            format_canonical_decimal(True)

    def test_rejects_non_numeral_string(self) -> None:
        with self.assertRaises(CanonicalizationError):
            format_canonical_decimal("not-a-number")


class TestTimestampGoldenCases(unittest.TestCase):
    """Item 8: UTC timestamp golden cases (Spec SS6.8)."""

    def test_second_precision(self) -> None:
        moment = datetime.datetime(2026, 8, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(format_utc_timestamp(moment), "2026-08-01T12:00:00Z")

    def test_microsecond_precision(self) -> None:
        moment = datetime.datetime(
            2026, 8, 1, 12, 0, 0, 123456, tzinfo=datetime.timezone.utc
        )
        self.assertEqual(
            format_utc_timestamp(moment), "2026-08-01T12:00:00.123456Z"
        )

    def test_rejects_naive_datetime(self) -> None:
        with self.assertRaises(CanonicalizationError):
            format_utc_timestamp(datetime.datetime(2026, 8, 1, 12, 0, 0))

    def test_rejects_non_utc_offset(self) -> None:
        tz = datetime.timezone(datetime.timedelta(hours=2))
        moment = datetime.datetime(2026, 8, 1, 12, 0, 0, tzinfo=tz)
        with self.assertRaises(CanonicalizationError):
            format_utc_timestamp(moment)


class TestNonFiniteGoldenCases(unittest.TestCase):
    """Item 8: non-finite number rejection golden cases."""

    def test_nan_rejected_in_preimage(self) -> None:
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"x": float("nan")})

    def test_positive_infinity_rejected_in_preimage(self) -> None:
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"x": float("inf")})

    def test_negative_infinity_rejected_in_preimage(self) -> None:
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"x": float("-inf")})

    def test_finite_float_also_rejected(self) -> None:
        # Binary floats are never accepted directly; domain decimals must
        # be pre-formatted via format_canonical_decimal.
        with self.assertRaises(CanonicalizationError):
            canonical_bytes({"x": 1.5})

    def test_reject_non_finite_helper(self) -> None:
        reject_non_finite(1.5)  # finite: no raise
        with self.assertRaises(CanonicalizationError):
            reject_non_finite(float("nan"))


class TestIndependentOracle(unittest.TestCase):
    """Item 7: an independent canonicalization/hash oracle.

    Re-implements a minimal JCS-compatible encoder for the restricted
    value domain this package emits (str/int/bool/None/list/dict, sorted
    keys, compact separators) from first principles -- not by calling
    ``rcc002.s8.canonical`` -- and cross-checks byte-for-byte against it
    for a battery of representative preimages, including a full
    identity-style nested preimage shape.
    """

    @staticmethod
    def _oracle_canonical_bytes(value: object) -> bytes:
        def encode(v: object) -> str:
            if v is None:
                return "null"
            if isinstance(v, bool):
                return "true" if v else "false"
            if isinstance(v, int):
                return str(v)
            if isinstance(v, str):
                return json.dumps(v, ensure_ascii=False)
            if isinstance(v, list):
                return "[" + ",".join(encode(item) for item in v) + "]"
            if isinstance(v, dict):
                items = sorted(v.items(), key=lambda kv: kv[0])
                return (
                    "{"
                    + ",".join(
                        f"{json.dumps(k, ensure_ascii=False)}:{encode(val)}"
                        for k, val in items
                    )
                    + "}"
                )
            raise TypeError(f"oracle cannot encode {type(v)!r}")

        return encode(value).encode("utf-8")

    def test_oracle_matches_implementation_on_scalars_and_containers(self) -> None:
        cases = [
            {"a": 1, "b": [1, 2, 3], "c": {"y": 2, "x": 1}},
            {"nested": {"deep": {"deeper": [1, {"k": "v"}, None, True, False]}}},
            {"": "empty key"},
            {"unicode": "caf\u00e9"},
            [],
            {},
            {"list_of_objects": [{"b": 1, "a": 2}, {"d": 3, "c": 4}]},
        ]
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(
                    self._oracle_canonical_bytes(case), canonical_bytes(case)
                )

    def test_oracle_matches_on_identity_style_preimage(self) -> None:
        preimage = {
            "identity_profile_id": "RCC002_EXAMPLE_ID_V1",
            "ordered_parents": ["build:sha256:aa", "build:sha256:bb"],
            "flags": {"clean": True, "note": None},
            "count": 42,
        }
        oracle_digest = hashlib.sha256(
            self._oracle_canonical_bytes(preimage)
        ).hexdigest()
        self.assertEqual(oracle_digest, canonical_sha256(preimage))

    def test_sha256_hex_matches_stdlib(self) -> None:
        data = b"rcc002-s8-oracle"
        self.assertEqual(sha256_hex(data), hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    unittest.main()
