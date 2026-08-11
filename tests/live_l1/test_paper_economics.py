from __future__ import annotations

import unittest
from dataclasses import replace
from decimal import Decimal

from live_l1.core.paper_economics import (
    PaperEconomicsConfig,
    PaperEconomicsError,
    ReasonCode,
    authorize_entry,
    calculate_fee_quote,
    floor_quantity_to_step,
    model_fill_price,
    settle_trade,
)


D = Decimal


def make_config(**overrides: object) -> PaperEconomicsConfig:
    values: dict[str, object] = {
        "schema_version": 1,
        "economics_model_version": "PEE_V1",
        "economics_profile_id": "TEST_ONLY_CONSERVATIVE",
        "quote_currency": "USDT",
        "starting_equity_quote": D("10000"),
        "risk_per_trade_rate": D("0.01"),
        "max_position_notional_rate": D("0.05"),
        "entry_fee_rate": D("0.0005"),
        "exit_fee_rate": D("0.0005"),
        "entry_slippage_bps": D("2"),
        "exit_slippage_bps": D("2"),
        "quantity_step": D("0.001"),
        "min_quantity": D("0.001"),
        "min_notional_quote": D("5"),
        "max_daily_loss_rate": D("0.03"),
        "max_daily_fee_rate": D("0.01"),
        "max_realized_drawdown_rate": D("0.10"),
    }
    values.update(overrides)
    return PaperEconomicsConfig(**values)


class ConfigTests(unittest.TestCase):
    def test_equivalent_decimal_spellings_have_same_fingerprint(self) -> None:
        first = make_config(entry_fee_rate=D("0.000500"))
        second = make_config(entry_fee_rate=D("0.0005"))

        self.assertEqual(first.config_fingerprint, second.config_fingerprint)
        self.assertEqual(len(first.config_fingerprint), 64)

    def test_semantic_change_changes_fingerprint(self) -> None:
        first = make_config(entry_slippage_bps=D("2"))
        second = make_config(entry_slippage_bps=D("3"))

        self.assertNotEqual(first.config_fingerprint, second.config_fingerprint)

    def test_float_input_is_rejected_at_boundary(self) -> None:
        with self.assertRaises(PaperEconomicsError) as caught:
            make_config(entry_fee_rate=0.0005)

        self.assertEqual(
            caught.exception.reason_code,
            ReasonCode.INPUT_FLOAT_NOT_ALLOWED,
        )

    def test_non_finite_and_out_of_range_values_are_rejected(self) -> None:
        cases = (
            {"starting_equity_quote": D("NaN")},
            {"risk_per_trade_rate": D("0")},
            {"max_position_notional_rate": D("1.01")},
            {"entry_slippage_bps": D("10000")},
            {"quantity_step": D("0")},
        )
        for override in cases:
            with self.subTest(override=override):
                with self.assertRaises(PaperEconomicsError):
                    make_config(**override)


class PrimitiveCalculationTests(unittest.TestCase):
    def test_adverse_fill_formulas(self) -> None:
        cases = (
            ("LONG", "ENTRY", "100.02"),
            ("LONG", "EXIT", "99.98"),
            ("SHORT", "ENTRY", "99.98"),
            ("SHORT", "EXIT", "100.02"),
        )
        for side, phase, expected in cases:
            with self.subTest(side=side, phase=phase):
                actual = model_fill_price(
                    side=side,
                    phase=phase,
                    reference_price=D("100"),
                    slippage_bps=D("2"),
                )
                self.assertEqual(actual, D(expected))

    def test_fee_scales_with_executed_notional(self) -> None:
        first = calculate_fee_quote(
            notional_quote=D("1000"),
            fee_rate=D("0.0005"),
        )
        second = calculate_fee_quote(
            notional_quote=D("2000"),
            fee_rate=D("0.0005"),
        )

        self.assertEqual(first, D("0.5"))
        self.assertEqual(second, first * 2)

    def test_quantity_is_always_rounded_down(self) -> None:
        self.assertEqual(
            floor_quantity_to_step(
                quantity=D("1.2399"),
                quantity_step=D("0.01"),
            ),
            D("1.23"),
        )
        self.assertEqual(
            floor_quantity_to_step(
                quantity=D("0.009"),
                quantity_step=D("0.01"),
            ),
            D("0"),
        )

    def test_invalid_side_phase_and_float_are_rejected(self) -> None:
        cases = (
            {"side": "BUY", "phase": "ENTRY", "reference_price": D("100")},
            {"side": "LONG", "phase": "OPEN", "reference_price": D("100")},
            {"side": "LONG", "phase": "ENTRY", "reference_price": 100.0},
        )
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(PaperEconomicsError):
                    model_fill_price(
                        side=case["side"],
                        phase=case["phase"],
                        reference_price=case["reference_price"],
                        slippage_bps=D("2"),
                    )


class EntryAuthorizationTests(unittest.TestCase):
    def test_authorized_quantity_respects_risk_notional_and_step(self) -> None:
        config = make_config()
        decision = authorize_entry(
            side="LONG",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100"),
            reference_stop_price=D("95"),
            config=config,
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason_code, ReasonCode.AUTHORIZED)
        self.assertIsNotNone(decision.quote)
        quote = decision.quote
        assert quote is not None
        self.assertEqual(
            quote.quantity,
            floor_quantity_to_step(
                quantity=quote.raw_quantity,
                quantity_step=config.quantity_step,
            ),
        )
        self.assertLessEqual(quote.modeled_stop_loss_quote, quote.risk_budget_quote)
        self.assertLessEqual(quote.entry_notional_quote, quote.notional_cap_quote)

    def test_larger_stop_distance_reduces_risk_limited_quantity(self) -> None:
        config = make_config(max_position_notional_rate=D("1"))
        close_stop = authorize_entry(
            side="LONG",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100"),
            reference_stop_price=D("98"),
            config=config,
        )
        far_stop = authorize_entry(
            side="LONG",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100"),
            reference_stop_price=D("90"),
            config=config,
        )

        self.assertTrue(close_stop.allowed)
        self.assertTrue(far_stop.allowed)
        self.assertGreater(close_stop.quantity, far_stop.quantity)

    def test_higher_costs_never_increase_risk_limited_quantity(self) -> None:
        low_cost = make_config(
            max_position_notional_rate=D("1"),
            entry_fee_rate=D("0"),
            exit_fee_rate=D("0"),
            entry_slippage_bps=D("0"),
            exit_slippage_bps=D("0"),
        )
        high_cost = replace(
            low_cost,
            entry_fee_rate=D("0.002"),
            exit_fee_rate=D("0.002"),
            entry_slippage_bps=D("10"),
            exit_slippage_bps=D("10"),
        )
        low = authorize_entry(
            side="SHORT",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100"),
            reference_stop_price=D("105"),
            config=low_cost,
        )
        high = authorize_entry(
            side="SHORT",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100"),
            reference_stop_price=D("105"),
            config=high_cost,
        )

        self.assertTrue(low.allowed)
        self.assertTrue(high.allowed)
        self.assertLessEqual(high.quantity, low.quantity)

    def test_notional_cap_is_enforced_at_modeled_entry_fill(self) -> None:
        config = make_config(
            risk_per_trade_rate=D("1"),
            max_position_notional_rate=D("0.05"),
        )
        decision = authorize_entry(
            side="SHORT",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100"),
            reference_stop_price=D("100.01"),
            config=config,
        )

        self.assertTrue(decision.allowed)
        assert decision.quote is not None
        self.assertLessEqual(
            decision.quote.entry_notional_quote,
            D("10000") * D("0.05"),
        )

    def test_invalid_stop_returns_stable_rejection(self) -> None:
        decision = authorize_entry(
            side="LONG",
            realized_equity_quote=D("10000"),
            reference_entry_price=D("100"),
            reference_stop_price=D("101"),
            config=make_config(),
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, ReasonCode.STOP_DIRECTION_INVALID)
        self.assertIsNone(decision.quote)

    def test_minimum_notional_rejects_without_fallback_quantity(self) -> None:
        config = make_config(min_notional_quote=D("1000"))
        decision = authorize_entry(
            side="LONG",
            realized_equity_quote=D("1000"),
            reference_entry_price=D("100"),
            reference_stop_price=D("95"),
            config=config,
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason_code, ReasonCode.NOTIONAL_BELOW_MIN)
        self.assertNotEqual(decision.quantity, D("1"))


class SettlementTests(unittest.TestCase):
    def _authorized_quote(
        self,
        *,
        side: str = "LONG",
        entry: str = "100",
        stop: str = "95",
        config: PaperEconomicsConfig,
    ):
        decision = authorize_entry(
            side=side,
            realized_equity_quote=D("10000"),
            reference_entry_price=D(entry),
            reference_stop_price=D(stop),
            config=config,
        )
        self.assertTrue(decision.allowed)
        self.assertIsNotNone(decision.quote)
        return decision.quote

    def test_zero_price_movement_with_costs_has_negative_net_pnl(self) -> None:
        config = make_config()
        quote = self._authorized_quote(config=config)
        settlement = settle_trade(
            entry_quote=quote,
            reference_exit_price=D("100"),
            equity_before_quote=D("10000"),
            peak_realized_equity_before_quote=D("10000"),
            config=config,
        )

        self.assertEqual(settlement.reference_pnl_quote, D("0"))
        self.assertLess(settlement.execution_gross_pnl_quote, D("0"))
        self.assertLess(settlement.net_pnl_quote, settlement.execution_gross_pnl_quote)
        self.assertEqual(
            settlement.net_pnl_quote,
            settlement.execution_gross_pnl_quote - settlement.total_fees_quote,
        )

    def test_zero_costs_make_reference_execution_and_net_pnl_equal(self) -> None:
        config = make_config(
            entry_fee_rate=D("0"),
            exit_fee_rate=D("0"),
            entry_slippage_bps=D("0"),
            exit_slippage_bps=D("0"),
        )
        quote = self._authorized_quote(config=config)
        settlement = settle_trade(
            entry_quote=quote,
            reference_exit_price=D("110"),
            equity_before_quote=D("10000"),
            peak_realized_equity_before_quote=D("10000"),
            config=config,
        )

        self.assertEqual(
            settlement.reference_pnl_quote,
            settlement.execution_gross_pnl_quote,
        )
        self.assertEqual(settlement.slippage_cost_quote, D("0"))
        self.assertEqual(settlement.total_fees_quote, D("0"))
        self.assertEqual(settlement.net_pnl_quote, settlement.reference_pnl_quote)

    def test_slippage_is_present_once_in_net_pnl_identity(self) -> None:
        config = make_config(entry_fee_rate=D("0"), exit_fee_rate=D("0"))
        quote = self._authorized_quote(config=config)
        settlement = settle_trade(
            entry_quote=quote,
            reference_exit_price=D("110"),
            equity_before_quote=D("10000"),
            peak_realized_equity_before_quote=D("10000"),
            config=config,
        )

        self.assertGreater(settlement.slippage_cost_quote, D("0"))
        self.assertEqual(
            settlement.execution_gross_pnl_quote,
            settlement.reference_pnl_quote - settlement.slippage_cost_quote,
        )
        self.assertEqual(
            settlement.net_pnl_quote,
            settlement.execution_gross_pnl_quote,
        )

    def test_swapped_long_short_paths_are_symmetric(self) -> None:
        config = make_config(
            risk_per_trade_rate=D("0.01"),
            max_position_notional_rate=D("1"),
            min_quantity=D("0"),
            min_notional_quote=D("0"),
        )
        long_quote = self._authorized_quote(
            side="LONG",
            entry="100",
            stop="90",
            config=config,
        )
        short_quote = self._authorized_quote(
            side="SHORT",
            entry="90",
            stop="100",
            config=config,
        )
        long_result = settle_trade(
            entry_quote=long_quote,
            reference_exit_price=D("90"),
            equity_before_quote=D("10000"),
            peak_realized_equity_before_quote=D("10000"),
            config=config,
        )
        short_result = settle_trade(
            entry_quote=short_quote,
            reference_exit_price=D("100"),
            equity_before_quote=D("10000"),
            peak_realized_equity_before_quote=D("10000"),
            config=config,
        )

        self.assertEqual(long_result.quantity, short_result.quantity)
        self.assertEqual(
            long_result.execution_gross_pnl_quote,
            short_result.execution_gross_pnl_quote,
        )
        self.assertEqual(long_result.total_fees_quote, short_result.total_fees_quote)
        self.assertEqual(long_result.net_pnl_quote, short_result.net_pnl_quote)

    def test_settlement_is_deterministic_and_tracks_drawdown(self) -> None:
        config = make_config()
        quote = self._authorized_quote(config=config)
        inputs = {
            "entry_quote": quote,
            "reference_exit_price": D("90"),
            "equity_before_quote": D("10000"),
            "peak_realized_equity_before_quote": D("10500"),
            "config": config,
        }

        first = settle_trade(**inputs)
        second = settle_trade(**inputs)

        self.assertEqual(first, second)
        self.assertEqual(first.equity_after_quote, D("10000") + first.net_pnl_quote)
        self.assertEqual(first.peak_realized_equity_after_quote, D("10500"))
        self.assertEqual(
            first.realized_drawdown_quote,
            first.peak_realized_equity_after_quote - first.equity_after_quote,
        )

    def test_config_mismatch_blocks_settlement(self) -> None:
        config = make_config()
        quote = self._authorized_quote(config=config)
        changed = replace(config, exit_fee_rate=D("0.0006"))

        with self.assertRaises(PaperEconomicsError) as caught:
            settle_trade(
                entry_quote=quote,
                reference_exit_price=D("110"),
                equity_before_quote=D("10000"),
                peak_realized_equity_before_quote=D("10000"),
                config=changed,
            )

        self.assertEqual(
            caught.exception.reason_code,
            ReasonCode.CONFIG_FINGERPRINT_MISMATCH,
        )


if __name__ == "__main__":
    unittest.main()
