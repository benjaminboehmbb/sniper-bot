"""Schema and registry tests for RCC-002 S5."""

from __future__ import annotations

import dataclasses
import unittest

from rcc002.s4.compute import compute_signals
from rcc002.s5.compute import compute_regimes
from rcc002.s5.constants import (
    REASON_CODE_REGISTRY,
    REGIME_EXTENSION_FIELDS,
    REGIME_SCHEMA_REF,
    RegimeState,
    TrendStrength,
)
from rcc002.s5.reason_codes import (
    RegimeReasonCodeError,
    normalize_reason_codes,
)
from tests.rcc002.s4.test_compute import _make_rows


class TestSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        s4 = compute_signals(_make_rows(1_443)).rows
        cls.valid = compute_regimes(
            s4, parent_build_id="schema-build"
        ).rows[-1]

    def test_extension_has_exact_21_field_order(self) -> None:
        self.assertEqual(len(REGIME_EXTENSION_FIELDS), 21)
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(type(self.valid))[-21:]
            ),
            REGIME_EXTENSION_FIELDS,
        )

    def test_metadata_is_canonical(self) -> None:
        self.assertEqual(self.valid.regime_schema_ref, REGIME_SCHEMA_REF)

    def test_valid_row_contract(self) -> None:
        self.assertTrue(self.valid.regime_valid)
        self.assertIsNot(self.valid.regime_raw, RegimeState.UNKNOWN)
        self.assertEqual(self.valid.regime_reason_codes, ())

    def test_invalid_row_requires_reason(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                regime_valid=False,
                regime_reason_codes=(),
            )

    def test_valid_row_cannot_have_reason(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                regime_reason_codes=("REG_INPUT_INVALID",),
            )

    def test_candidate_count_rejects_bool_and_out_of_range(self) -> None:
        for value in (True, -1, 4):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    dataclasses.replace(
                        self.valid, regime_candidate_count=value
                    )

    def test_nontransition_requires_unknown_endpoints(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                regime_transition_flag=False,
                regime_transition_from=RegimeState.BEAR,
                regime_transition_to=None,
            )

    def test_invalid_trend_strength_is_unknown(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                trend_strength_valid=False,
                trend_strength=TrendStrength.STRONG,
                trend_strength_reason_codes=(
                    "REG_TREND_STRENGTH_INPUT_INVALID",
                ),
            )

    def test_invalid_context_requires_field_local_reason(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                trend_strength_valid=False,
                trend_strength=TrendStrength.UNKNOWN,
                trend_strength_reason_codes=(),
            )

    def test_context_reason_not_allowed_in_regime_reasons(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                regime_raw=RegimeState.UNKNOWN,
                regime_valid=False,
                regime_reason_codes=(
                    "REG_TREND_STRENGTH_INPUT_INVALID",
                ),
            )

    def test_nonfinite_slope_rejected(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid, ma200_slope_1440_pct=float("nan")
            )

    def test_reason_registry_exact(self) -> None:
        self.assertEqual(len(REASON_CODE_REGISTRY), 10)
        self.assertEqual(
            tuple(item.priority for item in REASON_CODE_REGISTRY.values()),
            (30, 40, 50, 60, 70, 80, 90, 100, 110, 120),
        )

    def test_reason_normalization(self) -> None:
        self.assertEqual(
            normalize_reason_codes(
                (
                    "REG_EFFECTIVE_UNCONFIRMED",
                    "REG_INPUT_INVALID",
                    "REG_INPUT_INVALID",
                )
            ),
            ("REG_INPUT_INVALID", "REG_EFFECTIVE_UNCONFIRMED"),
        )

    def test_unknown_reason_rejected(self) -> None:
        with self.assertRaises(RegimeReasonCodeError):
            normalize_reason_codes(("NOT_REGISTERED",))


if __name__ == "__main__":
    unittest.main()
