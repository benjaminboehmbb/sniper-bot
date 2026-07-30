"""S6 reason-code registry tests."""

from __future__ import annotations

import unittest

from rcc002.s6.constants import (
    REASON_CODE_REGISTRY,
    REASON_CODE_REGISTRY_VERSION,
)
from rcc002.s6.reason_codes import (
    GateReasonCodeError,
    normalize_direction_reason_codes,
    normalize_reason_codes,
)


class TestReasonCodes(unittest.TestCase):
    def test_registry_version_and_exact_priorities(self) -> None:
        self.assertEqual(REASON_CODE_REGISTRY_VERSION, "1.0.0")
        self.assertEqual(len(REASON_CODE_REGISTRY), 19)
        self.assertEqual(
            tuple(item.priority for item in REASON_CODE_REGISTRY.values()),
            tuple(range(30, 220, 10)),
        )

    def test_normalization_deduplicates_and_sorts(self) -> None:
        self.assertEqual(
            normalize_reason_codes(
                (
                    "GATE_LONG_ALLOWED_BULL",
                    "GATE_WARMUP_INCOMPLETE",
                    "GATE_LONG_ALLOWED_BULL",
                )
            ),
            (
                "GATE_WARMUP_INCOMPLETE",
                "GATE_LONG_ALLOWED_BULL",
            ),
        )

    def test_none_normalizes_to_empty_tuple(self) -> None:
        self.assertEqual(normalize_reason_codes(None), ())

    def test_unknown_code_rejected(self) -> None:
        with self.assertRaises(GateReasonCodeError):
            normalize_reason_codes(("GATE_NOT_REGISTERED",))

    def test_long_code_rejected_from_short_list(self) -> None:
        with self.assertRaises(GateReasonCodeError):
            normalize_direction_reason_codes(
                ("GATE_LONG_BLOCKED_BEAR",), direction="SHORT"
            )

    def test_short_code_rejected_from_long_list(self) -> None:
        with self.assertRaises(GateReasonCodeError):
            normalize_direction_reason_codes(
                ("GATE_SHORT_BLOCKED_BULL",), direction="LONG"
            )

    def test_neutral_codes_allowed_in_both_lists(self) -> None:
        for direction in ("LONG", "SHORT"):
            self.assertEqual(
                normalize_direction_reason_codes(
                    ("GATE_REGIME_UNKNOWN",), direction=direction
                ),
                ("GATE_REGIME_UNKNOWN",),
            )


if __name__ == "__main__":
    unittest.main()
