from __future__ import annotations

import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from live_l1.core.paper_economics import (
    PaperEconomicsConfig,
    ReasonCode,
    authorize_entry,
    settle_trade,
)
from live_l1.core.paper_economics_shadow import MODE_SHADOW
from live_l1.tools.paper_economics_shadow_sidecar import load_settings_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    PROJECT_ROOT
    / "config"
    / "pee"
    / "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json"
)
EXPECTED_FINGERPRINT = (
    "ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1"
)
D = Decimal


def load_candidate_config() -> PaperEconomicsConfig:
    settings = load_settings_json(PROFILE_PATH)
    if settings.config is None:
        raise AssertionError("candidate profile did not load a configuration")
    return settings.config


class PaperEconomicsProfileCandidateTests(unittest.TestCase):
    def test_candidate_is_valid_shadow_only_configuration(self) -> None:
        settings = load_settings_json(PROFILE_PATH)

        self.assertEqual(settings.mode, MODE_SHADOW)
        self.assertTrue(settings.ready)
        self.assertIsNotNone(settings.config)
        self.assertEqual(
            settings.config.economics_profile_id,
            "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001",
        )
        self.assertEqual(settings.config.quote_currency, "USDT")
        self.assertEqual(settings.config.config_fingerprint, EXPECTED_FINGERPRINT)

    def test_candidate_preserves_conservative_caps(self) -> None:
        config = load_candidate_config()

        self.assertEqual(str(config.risk_per_trade_rate), "0.0025")
        self.assertEqual(str(config.max_position_notional_rate), "0.10")
        self.assertEqual(str(config.max_daily_loss_rate), "0.01")
        self.assertEqual(str(config.max_realized_drawdown_rate), "0.05")

    def test_candidate_authorizes_long_and_short_within_both_caps(self) -> None:
        config = load_candidate_config()
        equity = D("10000")

        for side, stop_price in (("LONG", D("98500")), ("SHORT", D("101500"))):
            with self.subTest(side=side):
                decision = authorize_entry(
                    side=side,
                    realized_equity_quote=equity,
                    reference_entry_price=D("100000"),
                    reference_stop_price=stop_price,
                    config=config,
                )

                self.assertTrue(decision.allowed)
                self.assertIsNotNone(decision.quote)
                quote = decision.quote
                assert quote is not None
                self.assertLessEqual(
                    quote.entry_notional_quote,
                    equity * config.max_position_notional_rate,
                )
                self.assertLessEqual(
                    quote.modeled_stop_loss_quote,
                    equity * config.risk_per_trade_rate,
                )
                self.assertEqual(decision.quantity % config.quantity_step, D("0"))

    def test_stress_costs_reduce_quantity_and_net_pnl(self) -> None:
        baseline_config = load_candidate_config()
        stress_config = replace(
            baseline_config,
            economics_profile_id="PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001_STRESS",
            entry_fee_rate=D("0.002"),
            exit_fee_rate=D("0.002"),
            entry_slippage_bps=D("20"),
            exit_slippage_bps=D("20"),
        )

        baseline = authorize_entry(
            side="LONG",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100000"),
            reference_stop_price=D("98500"),
            config=baseline_config,
        )
        stress = authorize_entry(
            side="LONG",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100000"),
            reference_stop_price=D("98500"),
            config=stress_config,
        )

        self.assertTrue(baseline.allowed)
        self.assertTrue(stress.allowed)
        self.assertLessEqual(stress.quantity, baseline.quantity)
        assert baseline.quote is not None
        assert stress.quote is not None

        baseline_settlement = settle_trade(
            entry_quote=baseline.quote,
            reference_exit_price=D("102000"),
            equity_before_quote=D("10000"),
            peak_realized_equity_before_quote=D("10000"),
            config=baseline_config,
        )
        stress_settlement = settle_trade(
            entry_quote=stress.quote,
            reference_exit_price=D("102000"),
            equity_before_quote=D("10000"),
            peak_realized_equity_before_quote=D("10000"),
            config=stress_config,
        )

        self.assertLess(
            stress_settlement.net_pnl_quote,
            baseline_settlement.net_pnl_quote,
        )

    def test_candidate_rejects_tiny_equity_below_quantity_step(self) -> None:
        decision = authorize_entry(
            side="LONG",
            realized_equity_quote=D("1"),
            reference_entry_price=D("100000"),
            reference_stop_price=D("98500"),
            config=load_candidate_config(),
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, ReasonCode.QUANTITY_ZERO)

    def test_candidate_flat_exit_is_negative_after_costs(self) -> None:
        config = load_candidate_config()
        decision = authorize_entry(
            side="LONG",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100000"),
            reference_stop_price=D("98500"),
            config=config,
        )
        self.assertTrue(decision.allowed)
        assert decision.quote is not None

        settlement = settle_trade(
            entry_quote=decision.quote,
            reference_exit_price=D("100000"),
            equity_before_quote=D("10000"),
            peak_realized_equity_before_quote=D("10000"),
            config=config,
        )

        self.assertGreater(settlement.total_fees_quote, D("0"))
        self.assertGreater(settlement.slippage_cost_quote, D("0"))
        self.assertLess(settlement.net_pnl_quote, D("0"))


if __name__ == "__main__":
    unittest.main()
