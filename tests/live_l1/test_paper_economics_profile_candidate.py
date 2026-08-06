from __future__ import annotations

import tempfile
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
from live_l1.state.paper_account import (
    PaperAccountStore,
    SimulatedSettlementInterruption,
)
from live_l1.state.paper_artifacts import (
    AccountGuardReasonCode,
    PaperAccountState,
    TradeRecordV2,
    evaluate_account_entry_guard,
)
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


def initial_candidate_account(config: PaperEconomicsConfig) -> PaperAccountState:
    return PaperAccountState.initial(
        account_id="PAPER-BTCUSDT-CANDIDATE-001",
        quote_currency=config.quote_currency,
        starting_equity_quote=config.starting_equity_quote,
        utc_day="2026-08-06",
        economics_profile_id=config.economics_profile_id,
        economics_model_version=config.economics_model_version,
        config_fingerprint=config.config_fingerprint,
    )


def candidate_trade(
    account: PaperAccountState,
    config: PaperEconomicsConfig,
    *,
    trade_id: str,
    event_id: str,
    utc_day: str,
    side: str,
    entry_price: str,
    stop_price: str,
    exit_price: str,
) -> TradeRecordV2:
    decision = authorize_entry(
        side=side,
        realized_equity_quote=account.realized_equity_quote,
        reference_entry_price=D(entry_price),
        reference_stop_price=D(stop_price),
        config=config,
    )
    if not decision.allowed or decision.quote is None:
        raise AssertionError(f"candidate trade was not authorized: {decision}")
    settlement = settle_trade(
        entry_quote=decision.quote,
        reference_exit_price=D(exit_price),
        equity_before_quote=account.realized_equity_quote,
        peak_realized_equity_before_quote=account.peak_realized_equity_quote,
        config=config,
    )
    sequence = account.closed_trade_count + 1
    return TradeRecordV2.from_economics(
        trade_id=trade_id,
        settlement_sequence=sequence,
        previous_settled_trade_id=account.last_settled_trade_id,
        settlement_event_id=event_id,
        settlement_utc_day=utc_day,
        system_state_id="SYSTEM-CANDIDATE-001",
        symbol="BTCUSDT",
        quote_currency=config.quote_currency,
        entry_timestamp_utc=f"{utc_day}T10:00:00Z",
        exit_timestamp_utc=f"{utc_day}T11:00:00Z",
        entry_tick_id=sequence * 10,
        exit_tick_id=sequence * 10 + 5,
        exit_reason="CANDIDATE_TEST_EXIT",
        entry_quote=decision.quote,
        settlement=settlement,
    )


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

    def test_candidate_account_limits_block_entries_but_not_exits(self) -> None:
        config = load_candidate_config()
        initial = initial_candidate_account(config)
        cases = (
            (
                replace(
                    initial,
                    realized_equity_quote=D("9900"),
                    cumulative_net_pnl_quote=D("-100"),
                    realized_drawdown_quote=D("100"),
                    realized_drawdown_rate=D("0.01"),
                    daily_net_pnl_quote=D("-100"),
                ),
                AccountGuardReasonCode.DAILY_LOSS_LIMIT,
            ),
            (
                replace(initial, daily_fees_quote=D("25")),
                AccountGuardReasonCode.DAILY_FEE_LIMIT,
            ),
            (
                replace(
                    initial,
                    realized_equity_quote=D("9500"),
                    cumulative_net_pnl_quote=D("-500"),
                    realized_drawdown_quote=D("500"),
                    realized_drawdown_rate=D("0.05"),
                ),
                AccountGuardReasonCode.REALIZED_DRAWDOWN_LIMIT,
            ),
        )

        for account, expected_reason in cases:
            with self.subTest(expected_reason=expected_reason):
                decision = evaluate_account_entry_guard(account, config)
                self.assertFalse(decision.entry_allowed)
                self.assertTrue(decision.exit_allowed)
                self.assertEqual(decision.reason_codes, (expected_reason,))

    def test_candidate_account_below_limits_allows_entry_and_exit(self) -> None:
        config = load_candidate_config()
        decision = evaluate_account_entry_guard(
            initial_candidate_account(config),
            config,
        )

        self.assertTrue(decision.entry_allowed)
        self.assertTrue(decision.exit_allowed)
        self.assertEqual(decision.reason_codes, ())

    def test_candidate_restart_and_utc_day_reset_are_idempotent(self) -> None:
        config = load_candidate_config()
        initial = initial_candidate_account(config)
        first_trade = candidate_trade(
            initial,
            config,
            trade_id="CANDIDATE-TRADE-1",
            event_id="CANDIDATE-EVENT-1",
            utc_day="2026-08-06",
            side="LONG",
            entry_price="100000",
            stop_price="98500",
            exit_price="99000",
        )

        with tempfile.TemporaryDirectory(prefix="pee-candidate-recovery-") as root:
            store = PaperAccountStore(root)
            store.initialize(initial)
            with self.assertRaises(SimulatedSettlementInterruption):
                store.commit_trade(
                    first_trade,
                    simulate_interruption_after_journal=True,
                )

            restarted_store = PaperAccountStore(root)
            first_recovery = restarted_store.recover()
            second_recovery = restarted_store.recover()
            self.assertEqual(first_recovery.recovered_settlement_count, 1)
            self.assertEqual(second_recovery.recovered_settlement_count, 0)

            first_account = first_recovery.account
            second_trade = candidate_trade(
                first_account,
                config,
                trade_id="CANDIDATE-TRADE-2",
                event_id="CANDIDATE-EVENT-2",
                utc_day="2026-08-07",
                side="SHORT",
                entry_price="100000",
                stop_price="101500",
                exit_price="99000",
            )
            second_account = restarted_store.commit_trade(second_trade).account

            self.assertEqual(second_account.utc_day, "2026-08-07")
            self.assertEqual(
                second_account.daily_net_pnl_quote,
                second_trade.net_pnl_quote,
            )
            self.assertEqual(
                second_account.daily_fees_quote,
                second_trade.total_fees_quote,
            )
            self.assertEqual(second_account.closed_trade_count, 2)
            self.assertEqual(restarted_store.recover().recovered_settlement_count, 0)


if __name__ == "__main__":
    unittest.main()
