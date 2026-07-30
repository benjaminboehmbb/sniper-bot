"""Pure S6 truth-rule tests."""

from __future__ import annotations

import unittest

from rcc002.s6.constants import GateState
from rcc002.s6.formulas import derive_gate_state


class TestDeriveGateState(unittest.TestCase):
    def test_complete_truth_table(self) -> None:
        cases = (
            (True, True, True, GateState.ALLOW_BOTH),
            (True, True, False, GateState.ALLOW_LONG_ONLY),
            (True, False, True, GateState.ALLOW_SHORT_ONLY),
            (True, False, False, GateState.BLOCK_BOTH),
            (False, False, False, GateState.INVALID),
        )
        for valid, long, short, expected in cases:
            with self.subTest(
                valid=valid, allow_long=long, allow_short=short
            ):
                self.assertIs(
                    derive_gate_state(
                        gate_valid=valid,
                        allow_long=long,
                        allow_short=short,
                    ),
                    expected,
                )

    def test_invalid_gate_cannot_allow_direction(self) -> None:
        for allow_long, allow_short in (
            (True, False),
            (False, True),
            (True, True),
        ):
            with self.assertRaises(ValueError):
                derive_gate_state(
                    gate_valid=False,
                    allow_long=allow_long,
                    allow_short=allow_short,
                )

    def test_rejects_non_boolean_input(self) -> None:
        with self.assertRaises(ValueError):
            derive_gate_state(
                gate_valid=1,
                allow_long=False,
                allow_short=False,
            )


if __name__ == "__main__":
    unittest.main()
