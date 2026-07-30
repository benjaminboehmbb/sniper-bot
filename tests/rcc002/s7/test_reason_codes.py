"""S7 reason-code registry tests."""

from __future__ import annotations

import unittest

from rcc002.s7.constants import (
    REASON_CODE_REGISTRY,
    REASON_CODE_REGISTRY_VERSION,
)
from rcc002.s7.reason_codes import (
    LabelReasonCodeError,
    normalize_reason_codes,
)


class TestReasonCodes(unittest.TestCase):
    def test_exact_registry(self) -> None:
        self.assertEqual(REASON_CODE_REGISTRY_VERSION, "1.0.0")
        self.assertEqual(len(REASON_CODE_REGISTRY), 16)
        self.assertNotIn(
            "LBL_WINDOW_CROSSES_GAP", REASON_CODE_REGISTRY
        )

    def test_deduplicates_and_sorts(self) -> None:
        self.assertEqual(
            normalize_reason_codes(
                (
                    "LBL_ENTRY_PRICE_INVALID",
                    "LBL_INPUT_INVALID",
                    "LBL_ENTRY_PRICE_INVALID",
                )
            ),
            ("LBL_INPUT_INVALID", "LBL_ENTRY_PRICE_INVALID"),
        )

    def test_stage_and_unknown_codes_are_rejected_on_rows(self) -> None:
        for code in ("LBL_SCHEMA_MISMATCH", "LBL_UNKNOWN"):
            with self.subTest(code=code):
                with self.assertRaises(LabelReasonCodeError):
                    normalize_reason_codes((code,))


if __name__ == "__main__":
    unittest.main()
