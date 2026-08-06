from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from live_l1.core.paper_economics import (
    PaperEconomicsConfig,
    authorize_entry,
    settle_trade,
)
from live_l1.state.paper_account import (
    AccountStoreReasonCode,
    PaperAccountStore,
    PaperAccountStoreError,
    SettlementEnvelopeV1,
    SimulatedSettlementInterruption,
)
from live_l1.state.paper_artifacts import (
    AccountGuardReasonCode,
    ArtifactReasonCode,
    LegacyArtifact,
    PaperAccountState,
    PaperArtifactError,
    PositionStateS2V2,
    TradeRecordV2,
    apply_trade_to_account,
    evaluate_account_entry_guard,
    parse_position_artifact,
    parse_trade_artifact,
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


def make_initial_account(
    config: PaperEconomicsConfig,
    *,
    utc_day: str = "2026-08-06",
) -> PaperAccountState:
    return PaperAccountState.initial(
        account_id="PAPER-BTCUSDT-1",
        quote_currency=config.quote_currency,
        starting_equity_quote=config.starting_equity_quote,
        utc_day=utc_day,
        economics_profile_id=config.economics_profile_id,
        economics_model_version=config.economics_model_version,
        config_fingerprint=config.config_fingerprint,
    )


def make_trade(
    account: PaperAccountState,
    config: PaperEconomicsConfig,
    *,
    trade_id: str,
    settlement_event_id: str,
    settlement_utc_day: str,
    side: str = "LONG",
    entry_price: str = "100",
    stop_price: str = "95",
    exit_price: str = "110",
) -> TradeRecordV2:
    decision = authorize_entry(
        side=side,
        realized_equity_quote=account.realized_equity_quote,
        reference_entry_price=D(entry_price),
        reference_stop_price=D(stop_price),
        config=config,
    )
    if not decision.allowed or decision.quote is None:
        raise AssertionError(f"test trade was not authorized: {decision}")
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
        settlement_event_id=settlement_event_id,
        settlement_utc_day=settlement_utc_day,
        system_state_id="SYSTEM-1",
        symbol="BTCUSDT",
        quote_currency=config.quote_currency,
        entry_timestamp_utc=f"{settlement_utc_day}T10:00:00Z",
        exit_timestamp_utc=f"{settlement_utc_day}T11:00:00Z",
        entry_tick_id=sequence * 10,
        exit_tick_id=sequence * 10 + 5,
        exit_reason="TEST_EXIT",
        entry_quote=decision.quote,
        settlement=settlement,
    )


class AccountEntryGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = make_config()
        self.account = make_initial_account(self.config)

    def test_config_mismatch_fails_closed_for_entry_only(self) -> None:
        changed_config = replace(
            self.config,
            max_daily_loss_rate=D("0.04"),
        )

        decision = evaluate_account_entry_guard(self.account, changed_config)

        self.assertFalse(decision.entry_allowed)
        self.assertTrue(decision.exit_allowed)
        self.assertEqual(
            decision.reason_codes,
            (ArtifactReasonCode.CONFIG_MISMATCH,),
        )

    def test_non_positive_equity_fails_closed_for_entry_only(self) -> None:
        depleted = replace(
            self.account,
            realized_equity_quote=D("0"),
            cumulative_net_pnl_quote=D("-10000"),
            realized_drawdown_quote=D("10000"),
            realized_drawdown_rate=D("1"),
            daily_net_pnl_quote=D("-10000"),
        )

        decision = evaluate_account_entry_guard(depleted, self.config)

        self.assertFalse(decision.entry_allowed)
        self.assertTrue(decision.exit_allowed)
        self.assertEqual(
            decision.reason_codes,
            (AccountGuardReasonCode.EQUITY_NON_POSITIVE,),
        )


class ArtifactSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = make_config()
        self.account = make_initial_account(self.config)
        self.trade = make_trade(
            self.account,
            self.config,
            trade_id="TRADE-1",
            settlement_event_id="EVENT-1",
            settlement_utc_day="2026-08-06",
        )

    def test_legacy_position_is_readable_but_blocks_entries(self) -> None:
        artifact = parse_position_artifact(
            {
                "schema_version": 1,
                "position": "LONG",
                "entry_price": 100.0,
                "position_size": 1.0,
            }
        )

        self.assertIsInstance(artifact, LegacyArtifact)
        self.assertFalse(artifact.economics_complete)
        self.assertFalse(artifact.entry_allowed)
        self.assertTrue(artifact.exit_allowed)
        self.assertEqual(
            artifact.reason_code,
            ArtifactReasonCode.LEGACY_ECONOMICS_INCOMPLETE,
        )

    def test_schema_zero_without_version_remains_explicit_legacy(self) -> None:
        artifact = parse_trade_artifact({"trade_id": "OLD-1", "pnl": 1.0})

        self.assertIsInstance(artifact, LegacyArtifact)
        self.assertEqual(artifact.schema_version, 0)

    def test_unknown_and_malformed_versions_fail_closed(self) -> None:
        cases = ({"schema_version": 3}, {"schema_version": "2"})
        expected_codes = (
            ArtifactReasonCode.SCHEMA_UNSUPPORTED,
            ArtifactReasonCode.SCHEMA_MALFORMED,
        )
        for record, expected_code in zip(cases, expected_codes):
            with self.subTest(record=record):
                with self.assertRaises(PaperArtifactError) as caught:
                    parse_position_artifact(record)
                self.assertEqual(caught.exception.reason_code, expected_code)

    def test_s2_v2_roundtrip_preserves_decimal_strings(self) -> None:
        state = PositionStateS2V2(
            schema_version=2,
            system_state_id="SYSTEM-1",
            symbol="BTCUSDT",
            position="LONG",
            side="LONG",
            trade_id="TRADE-OPEN",
            reference_entry_price=D("100.10"),
            modeled_entry_fill_price=D("100.12"),
            quantity=D("0.123"),
            entry_notional_quote=D("12.31476"),
            entry_fee_quote=D("0.00615738"),
            risk_budget_quote=D("100"),
            modeled_stop_loss_quote=D("0.75"),
            reference_stop_price=D("95"),
            entry_timestamp_utc="2026-08-06T10:00:00Z",
            entry_tick_id=100,
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        record = state.to_record()

        self.assertIsInstance(record["quantity"], str)
        self.assertEqual(PositionStateS2V2.from_record(record), state)
        self.assertEqual(parse_position_artifact(record), state)

    def test_s2_v2_rejects_wrong_stop_direction(self) -> None:
        with self.assertRaises(PaperArtifactError):
            PositionStateS2V2(
                schema_version=2,
                system_state_id="SYSTEM-1",
                symbol="BTCUSDT",
                position="LONG",
                side="LONG",
                trade_id="TRADE-OPEN",
                reference_entry_price=D("100"),
                modeled_entry_fill_price=D("100.02"),
                quantity=D("1"),
                entry_notional_quote=D("100.02"),
                entry_fee_quote=D("0.05"),
                risk_budget_quote=D("100"),
                modeled_stop_loss_quote=D("5"),
                reference_stop_price=D("105"),
                entry_timestamp_utc="2026-08-06T10:00:00Z",
                entry_tick_id=100,
                economics_profile_id=self.config.economics_profile_id,
                economics_model_version=self.config.economics_model_version,
                config_fingerprint=self.config.config_fingerprint,
            )

    def test_trade_v2_roundtrip_and_fingerprint_are_stable(self) -> None:
        record = self.trade.to_record()
        restored = TradeRecordV2.from_record(record)

        self.assertEqual(restored, self.trade)
        self.assertEqual(restored.record_fingerprint, self.trade.record_fingerprint)
        self.assertEqual(parse_trade_artifact(record), self.trade)

    def test_trade_v2_rejects_broken_net_pnl_identity(self) -> None:
        record = self.trade.to_record()
        record["net_pnl_quote"] = "999"

        with self.assertRaises(PaperArtifactError) as caught:
            TradeRecordV2.from_record(record)

        self.assertEqual(caught.exception.reason_code, ArtifactReasonCode.ARTIFACT_INVALID)

    def test_account_roundtrip_and_fingerprint_are_stable(self) -> None:
        record = self.account.to_record()
        restored = PaperAccountState.from_record(record)

        self.assertEqual(restored, self.account)
        self.assertEqual(restored.state_fingerprint, self.account.state_fingerprint)
        self.assertTrue(all(not isinstance(value, float) for value in record.values()))

    def test_account_rejects_broken_equity_identity(self) -> None:
        record = self.account.to_record()
        record["realized_equity_quote"] = "9999"

        with self.assertRaises(PaperArtifactError) as caught:
            PaperAccountState.from_record(record)

        self.assertEqual(caught.exception.reason_code, ArtifactReasonCode.ARTIFACT_INVALID)

    def test_apply_trade_rejects_wrong_config_and_sequence(self) -> None:
        wrong_config_account = replace(self.account, config_fingerprint="f" * 64)
        with self.assertRaises(PaperArtifactError) as config_error:
            apply_trade_to_account(wrong_config_account, self.trade)
        self.assertEqual(config_error.exception.reason_code, ArtifactReasonCode.CONFIG_MISMATCH)

        wrong_sequence = replace(self.trade, settlement_sequence=2)
        with self.assertRaises(PaperArtifactError) as sequence_error:
            apply_trade_to_account(self.account, wrong_sequence)
        self.assertEqual(
            sequence_error.exception.reason_code,
            ArtifactReasonCode.SEQUENCE_MISMATCH,
        )


class PaperAccountStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-iu2-test-")
        self.root = Path(self.temporary_directory)
        self.config = make_config()
        self.initial = make_initial_account(self.config)
        self.store = PaperAccountStore(self.root)
        self.store.initialize(self.initial)

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    def _first_trade(self, **overrides: object) -> TradeRecordV2:
        values = {
            "trade_id": "TRADE-1",
            "settlement_event_id": "EVENT-1",
            "settlement_utc_day": "2026-08-06",
        }
        values.update(overrides)
        return make_trade(self.initial, self.config, **values)

    def test_initialization_is_idempotent_only_for_identical_state(self) -> None:
        self.assertEqual(self.store.initialize(self.initial), self.initial)

        with self.assertRaises(PaperAccountStoreError) as caught:
            self.store.initialize(replace(self.initial, account_id="OTHER"))
        self.assertEqual(
            caught.exception.reason_code,
            AccountStoreReasonCode.ACCOUNT_ALREADY_INITIALIZED,
        )

    def test_commit_writes_journal_then_account_once(self) -> None:
        trade = self._first_trade()
        first = self.store.commit_trade(trade)
        second = self.store.commit_trade(trade)

        self.assertTrue(first.newly_committed)
        self.assertTrue(second.already_committed)
        self.assertEqual(first.account, second.account)
        self.assertEqual(second.account.closed_trade_count, 1)
        self.assertEqual(second.account.last_settled_trade_id, "TRADE-1")
        self.assertEqual(len(list((self.root / "settlements").glob("*.json"))), 1)
        self.assertEqual(list(self.root.rglob("*.tmp")), [])

    def test_interruption_after_journal_is_recovered_exactly_once(self) -> None:
        trade = self._first_trade()
        with self.assertRaises(SimulatedSettlementInterruption):
            self.store.commit_trade(
                trade,
                simulate_interruption_after_journal=True,
            )

        account_before_recovery = self.store.load_account()
        report_before = self.store.reconciliation_report()
        self.assertEqual(account_before_recovery, self.initial)
        self.assertFalse(report_before.consistent)
        self.assertFalse(report_before.entry_allowed)
        self.assertTrue(report_before.exit_allowed)
        self.assertEqual(
            report_before.reason_codes,
            (AccountStoreReasonCode.RECOVERY_REQUIRED,),
        )

        first_recovery = self.store.recover()
        second_recovery = self.store.recover()
        duplicate_commit = self.store.commit_trade(trade)

        self.assertEqual(first_recovery.recovered_settlement_count, 1)
        self.assertEqual(second_recovery.recovered_settlement_count, 0)
        self.assertTrue(duplicate_commit.already_committed)
        self.assertEqual(first_recovery.account.closed_trade_count, 1)
        self.assertEqual(first_recovery.account, second_recovery.account)
        self.assertEqual(first_recovery.account, duplicate_commit.account)

    def test_repeated_commit_with_changed_trade_data_is_conflict(self) -> None:
        trade = self._first_trade()
        self.store.commit_trade(trade)
        conflicting = replace(trade, exit_reason="DIFFERENT_EXIT_REASON")

        with self.assertRaises(PaperAccountStoreError) as caught:
            self.store.commit_trade(conflicting)

        self.assertEqual(
            caught.exception.reason_code,
            AccountStoreReasonCode.JOURNAL_CONFLICT,
        )
        self.assertEqual(self.store.load_account().closed_trade_count, 1)

    def test_two_trade_chain_and_daily_reset(self) -> None:
        first = self.store.commit_trade(self._first_trade()).account
        second_trade = make_trade(
            first,
            self.config,
            trade_id="TRADE-2",
            settlement_event_id="EVENT-2",
            settlement_utc_day="2026-08-07",
            side="SHORT",
            entry_price="100",
            stop_price="105",
            exit_price="90",
        )
        second = self.store.commit_trade(second_trade).account

        self.assertEqual(second.closed_trade_count, 2)
        self.assertEqual(second.last_settled_trade_id, "TRADE-2")
        self.assertEqual(second.utc_day, "2026-08-07")
        self.assertEqual(second.daily_net_pnl_quote, second_trade.net_pnl_quote)
        self.assertEqual(second.daily_fees_quote, second_trade.total_fees_quote)
        self.assertEqual(self.store.recover().recovered_settlement_count, 0)
        self.assertTrue(self.store.reconciliation_report().consistent)

    def test_missing_account_fails_closed_but_keeps_exit_permission(self) -> None:
        missing_store = PaperAccountStore(self.root / "missing")
        report = missing_store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(report.reason_codes, (AccountStoreReasonCode.ACCOUNT_MISSING,))

    def test_corrupt_account_json_fails_closed(self) -> None:
        self.store.account_path.write_text("{broken", encoding="utf-8")
        report = self.store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(report.reason_codes, (AccountStoreReasonCode.JSON_INVALID,))

    def test_unknown_journal_schema_fails_closed(self) -> None:
        trade = self._first_trade()
        result = self.store.commit_trade(trade)
        record = json.loads(result.journal_path.read_text(encoding="utf-8"))
        record["schema_version"] = 2
        result.journal_path.write_text(json.dumps(record), encoding="utf-8")

        report = self.store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (ArtifactReasonCode.SCHEMA_UNSUPPORTED,),
        )

    def test_account_ahead_of_empty_journal_is_rejected(self) -> None:
        trade = self._first_trade()
        account_after = apply_trade_to_account(self.initial, trade)
        self.store.account_path.write_text(
            json.dumps(account_after.to_record()),
            encoding="utf-8",
        )

        report = self.store.reconciliation_report()
        self.assertFalse(report.consistent)
        self.assertEqual(
            report.reason_codes,
            (AccountStoreReasonCode.ACCOUNT_AHEAD_OF_JOURNAL,),
        )
        with self.assertRaises(PaperAccountStoreError) as caught:
            self.store.recover()
        self.assertEqual(
            caught.exception.reason_code,
            AccountStoreReasonCode.ACCOUNT_AHEAD_OF_JOURNAL,
        )

    def test_envelope_roundtrip_preserves_full_trade_and_account(self) -> None:
        trade = self._first_trade()
        account_after = apply_trade_to_account(self.initial, trade)
        envelope = SettlementEnvelopeV1(
            schema_version=1,
            account_before_fingerprint=self.initial.state_fingerprint,
            trade=trade,
            account_after=account_after,
        )

        restored = SettlementEnvelopeV1.from_record(envelope.to_record())

        self.assertEqual(restored, envelope)
        self.assertEqual(restored.envelope_fingerprint, envelope.envelope_fingerprint)


if __name__ == "__main__":
    unittest.main()
