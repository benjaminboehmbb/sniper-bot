"""Small immutable golden fixtures for canonical S7 outputs."""

from __future__ import annotations

import unittest

from rcc002.s7.compute import compute_labels
from rcc002.s7.constants import BarrierOutcome
from tests.rcc002.s7._helpers import make_s6_rows


class TestGoldenFixtures(unittest.TestCase):
    def test_flat_h001_fixture(self) -> None:
        rows = make_s6_rows(
            (100.0, 100.0),
            opens=(100.0, 100.0),
            highs=(100.0, 101.0),
            lows=(100.0, 99.0),
        )
        labels = compute_labels(rows, output_row_count=1).rows[0].horizons[
            "H001"
        ]
        expected = {
            "fwd_cc_long_ret": 0.0,
            "fwd_cc_short_ret": 0.0,
            "fwd_noc_long_ret": 0.0,
            "fwd_noc_short_ret": 0.0,
            "fwd_noc_long_net_proxy_fee_rt_0004": -0.0004,
            "fwd_noc_short_net_proxy_fee_rt_0004": -0.0004,
            "label_cc_long_direction": 0,
            "label_cc_short_direction": 0,
            "label_noc_long_direction": 0,
            "label_noc_short_direction": 0,
            "label_noc_long_net_proxy_fee_rt_0004_direction": -1,
            "label_noc_short_net_proxy_fee_rt_0004_direction": -1,
            "barrier_long_outcome_tp050_sl020": (
                BarrierOutcome.TIMEOUT
            ),
            "barrier_short_outcome_tp050_sl020": (
                BarrierOutcome.TIMEOUT
            ),
            "barrier_reason_codes": ("LBL_BARRIER_TIMEOUT",),
        }
        for name, value in expected.items():
            with self.subTest(name=name):
                self.assertEqual(getattr(labels, name), value)

    def test_tail_fixture_is_all_family_invalid(self) -> None:
        row = compute_labels(make_s6_rows((100.0,))).rows[0]
        for labels in row.horizons.values():
            self.assertFalse(labels.fwd_cc_valid)
            self.assertFalse(labels.fwd_noc_valid)
            self.assertFalse(labels.fwd_excursion_valid)
            self.assertFalse(labels.label_cc_direction_valid)
            self.assertFalse(labels.label_noc_direction_valid)
            self.assertFalse(labels.barrier_valid)
            self.assertEqual(
                labels.fwd_cc_reason_codes,
                ("LBL_FUTURE_HORIZON_INCOMPLETE",),
            )


if __name__ == "__main__":
    unittest.main()
