"""S6 schema and invariant tests."""

from __future__ import annotations

import dataclasses
import unittest

from rcc002.s6.compute import compute_gates
from rcc002.s6.constants import (
    GATE_EXTENSION_FIELDS,
    GATE_SCHEMA_REF,
    GateState,
)
from tests.rcc002.s6._helpers import valid_s5_row


class TestS6Schema(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid = compute_gates((valid_s5_row(),)).rows[0]

    def test_extension_has_exact_13_field_order(self) -> None:
        self.assertEqual(len(GATE_EXTENSION_FIELDS), 13)
        self.assertEqual(
            tuple(
                field.name
                for field in dataclasses.fields(type(self.valid))[-13:]
            ),
            GATE_EXTENSION_FIELDS,
        )

    def test_metadata_and_evaluation_time_are_canonical(self) -> None:
        self.assertEqual(self.valid.gate_schema_ref, GATE_SCHEMA_REF)
        self.assertEqual(
            self.valid.gate_evaluated_at, self.valid.close_time
        )

    def test_gate_state_must_match_booleans(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid, gate_state=GateState.BLOCK_BOTH
            )

    def test_invalid_gate_cannot_allow_direction(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                gate_valid=False,
                gate_state=GateState.INVALID,
            )

    def test_data_gate_must_equal_quality_gate(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(self.valid, data_gate_pass=False)

    def test_gate_evaluated_at_must_equal_close_time(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                gate_evaluated_at=self.valid.close_time + 1,
            )

    def test_opposite_direction_reason_rejected(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                gate_reason_codes_long=(
                    "GATE_SHORT_ALLOWED_RESEARCH_OPEN",
                ),
            )

    def test_allowed_direction_requires_allow_reason(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid, gate_reason_codes_long=()
            )

    def test_blocked_direction_cannot_contain_allow_reason(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid,
                allow_short=False,
                gate_state=GateState.ALLOW_LONG_ONLY,
            )

    def test_unregistered_profile_rejected(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(
                self.valid, gate_profile_id="GATE_UNKNOWN"
            )

    def test_boolean_fields_reject_integer_aliases(self) -> None:
        with self.assertRaises(ValueError):
            dataclasses.replace(self.valid, allow_long=1)


if __name__ == "__main__":
    unittest.main()
