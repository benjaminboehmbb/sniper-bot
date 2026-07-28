"""Small deterministic golden fixtures for RCC-002 S5."""

from __future__ import annotations

import unittest

from rcc002.s4.compute import compute_signals
from rcc002.s5.compute import compute_regimes
from rcc002.s5.constants import RegimeState
from tests.rcc002.s4.test_compute import _make_row


class TestGoldenFixtures(unittest.TestCase):
    def test_bear_confirmation_fixture(self) -> None:
        source = [
            _make_row(
                index,
                close=50.0,
                indicator_overrides={
                    "sma_close_200": 100.0 - index / 20_000.0
                },
            )
            for index in range(1_443)
        ]
        result = compute_regimes(
            compute_signals(source).rows,
            parent_build_id="bear-fixture",
        )
        rows = result.rows
        self.assertEqual(
            tuple(row.regime_raw for row in rows[1_440:1_443]),
            (RegimeState.BEAR,) * 3,
        )
        self.assertIs(rows[1_442].regime_effective, RegimeState.BEAR)
        self.assertTrue(rows[1_442].regime_transition_flag)

    def test_unknown_resets_confirmed_state_fixture(self) -> None:
        source = [
            _make_row(index)
            for index in range(1_443)
        ]
        s4 = list(compute_signals(source).rows)
        confirmed = compute_regimes(
            s4, parent_build_id="unknown-fixture"
        )
        self.assertIs(
            confirmed.rows[-1].regime_effective, RegimeState.SIDE
        )

        bad = _make_row(
            1_443,
            quality_gate_pass=False,
            quality_status="ERROR",
            quality_reason_codes=("DV_NUMERIC_PARSE_FAILED",),
        )
        bad_s4 = compute_signals((bad,)).rows[0]
        resumed = compute_regimes(
            (bad_s4,),
            parent_build_id="unknown-fixture",
            prior_state=confirmed.final_state,
        )
        self.assertTrue(resumed.prior_state_accepted)
        self.assertIs(
            resumed.rows[0].regime_effective, RegimeState.UNKNOWN
        )
        self.assertTrue(resumed.rows[0].regime_transition_flag)
        self.assertIs(
            resumed.rows[0].regime_transition_from, RegimeState.SIDE
        )
        self.assertIs(
            resumed.rows[0].regime_transition_to, RegimeState.UNKNOWN
        )
        assert resumed.final_state is not None
        self.assertIs(
            resumed.final_state.regime_effective,
            RegimeState.UNKNOWN,
        )
        self.assertEqual(
            len(resumed.final_state.sma200_context_state), 1_440
        )

    def test_same_input_produces_identical_state_hash(self) -> None:
        rows = compute_signals(
            [_make_row(index) for index in range(10)]
        ).rows
        first = compute_regimes(
            rows, parent_build_id="deterministic"
        )
        second = compute_regimes(
            rows, parent_build_id="deterministic"
        )
        assert first.final_state is not None
        assert second.final_state is not None
        self.assertEqual(
            first.final_state.state_payload_sha256,
            second.final_state.state_payload_sha256,
        )


if __name__ == "__main__":
    unittest.main()
