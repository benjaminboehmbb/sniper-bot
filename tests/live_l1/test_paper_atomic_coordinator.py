#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from live_l1.core.paper_economics import (
    EntryEconomicsQuote,
    PaperEconomicsConfig,
    authorize_entry,
    settle_trade,
)
from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    PaperEntryThrottlePolicy,
    PaperEntryThrottleState,
)
from live_l1.state.paper_artifacts import (
    PaperAccountState,
    PositionStateS2FlatV2,
    PositionStateS2V2,
    TradeRecordV2,
)
from live_l1.state.paper_atomic_coordinator import (
    AtomicCoordinatorReasonCode,
    AtomicPaperStateV1,
    PaperAtomicCoordinator,
    PaperAtomicCoordinatorError,
    POSITION_OPEN_REASON,
    SimulatedAtomicTransactionInterruption,
)


D = Decimal


def make_config(**overrides: object) -> PaperEconomicsConfig:
    values: dict[str, object] = {
        "schema_version": 1,
        "economics_model_version": "PEE_V1",
        "economics_profile_id": "TEST_ATOMIC_PROFILE",
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


def make_policy(**overrides: object) -> PaperEntryThrottlePolicy:
    values: dict[str, object] = {
        "schema_version": 1,
        "policy_model_version": "PEE_RATE_V1",
        "policy_profile_id": "TEST_ATOMIC_RATE",
        "max_entries_per_utc_day": 10,
        "max_entries_per_rolling_window": 3,
        "rolling_window_seconds": 3600,
        "min_reentry_cooldown_seconds": 60,
    }
    values.update(overrides)
    return PaperEntryThrottlePolicy(**values)


def make_flat(
    config: PaperEconomicsConfig,
    *,
    system_state_id: str,
    last_closed_trade_id: str = "",
) -> PositionStateS2FlatV2:
    return PositionStateS2FlatV2(
        schema_version=2,
        system_state_id=system_state_id,
        symbol="BTCUSDT",
        position="FLAT",
        side="",
        last_closed_trade_id=last_closed_trade_id,
        economics_profile_id=config.economics_profile_id,
        economics_model_version=config.economics_model_version,
        config_fingerprint=config.config_fingerprint,
    )


def make_account(config: PaperEconomicsConfig) -> PaperAccountState:
    return PaperAccountState.initial(
        account_id="PAPER-BTCUSDT-ATOMIC",
        quote_currency=config.quote_currency,
        starting_equity_quote=config.starting_equity_quote,
        utc_day="2026-08-09",
        economics_profile_id=config.economics_profile_id,
        economics_model_version=config.economics_model_version,
        config_fingerprint=config.config_fingerprint,
    )


def make_entry_event(
    throttle: PaperEntryThrottleState,
    policy: PaperEntryThrottlePolicy,
    *,
    event_id: str,
    timestamp: str,
) -> AcceptedEntryEventV1:
    return AcceptedEntryEventV1(
        schema_version=1,
        entry_sequence=throttle.total_accepted_entry_count + 1,
        entry_event_id=event_id,
        previous_entry_event_id=throttle.last_entry_event_id,
        entry_timestamp_utc=timestamp,
        policy_model_version=policy.policy_model_version,
        policy_profile_id=policy.policy_profile_id,
        policy_fingerprint=policy.policy_fingerprint,
    )


def make_open(
    account: PaperAccountState,
    config: PaperEconomicsConfig,
    *,
    trade_id: str,
    system_state_id: str,
    timestamp: str,
    tick_id: int,
) -> tuple[PositionStateS2V2, EntryEconomicsQuote]:
    decision = authorize_entry(
        side="LONG",
        realized_equity_quote=account.realized_equity_quote,
        reference_entry_price=D("100"),
        reference_stop_price=D("95"),
        config=config,
    )
    if not decision.allowed or decision.quote is None:
        raise AssertionError(f"test entry was not authorized: {decision}")
    quote = decision.quote
    return (
        PositionStateS2V2(
            schema_version=2,
            system_state_id=system_state_id,
            symbol="BTCUSDT",
            position="LONG",
            side="LONG",
            trade_id=trade_id,
            reference_entry_price=quote.reference_entry_price,
            modeled_entry_fill_price=quote.modeled_entry_fill_price,
            quantity=quote.quantity,
            entry_notional_quote=quote.entry_notional_quote,
            entry_fee_quote=quote.entry_fee_quote,
            risk_budget_quote=quote.risk_budget_quote,
            modeled_stop_loss_quote=quote.modeled_stop_loss_quote,
            reference_stop_price=quote.reference_stop_price,
            entry_timestamp_utc=timestamp,
            entry_tick_id=tick_id,
            economics_profile_id=config.economics_profile_id,
            economics_model_version=config.economics_model_version,
            config_fingerprint=config.config_fingerprint,
        ),
        quote,
    )


def make_trade(
    account: PaperAccountState,
    config: PaperEconomicsConfig,
    quote: EntryEconomicsQuote,
    *,
    trade_id: str,
    event_id: str,
    system_state_id: str,
    entry_timestamp: str,
    exit_timestamp: str,
    entry_tick_id: int,
    exit_tick_id: int,
) -> TradeRecordV2:
    settlement = settle_trade(
        entry_quote=quote,
        reference_exit_price=D("110"),
        equity_before_quote=account.realized_equity_quote,
        peak_realized_equity_before_quote=account.peak_realized_equity_quote,
        config=config,
    )
    return TradeRecordV2.from_economics(
        trade_id=trade_id,
        settlement_sequence=account.closed_trade_count + 1,
        previous_settled_trade_id=account.last_settled_trade_id,
        settlement_event_id=event_id,
        settlement_utc_day="2026-08-09",
        system_state_id=system_state_id,
        symbol="BTCUSDT",
        quote_currency=config.quote_currency,
        entry_timestamp_utc=entry_timestamp,
        exit_timestamp_utc=exit_timestamp,
        entry_tick_id=entry_tick_id,
        exit_tick_id=exit_tick_id,
        exit_reason="TEST_EXIT",
        entry_quote=quote,
        settlement=settlement,
    )


def contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_float(item) for item in value)
    return False


class PaperAtomicCoordinatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-atomic-test-")
        self.root = Path(self.temporary_directory)
        self.config = make_config()
        self.policy = make_policy()
        self.initial_flat = make_flat(self.config, system_state_id="SYSTEM-0")
        self.initial_account = make_account(self.config)
        self.initial_throttle = PaperEntryThrottleState.initial(
            self.policy,
            utc_day="2026-08-09",
        )
        self.coordinator = PaperAtomicCoordinator(
            self.root,
            self.config,
            self.policy,
            coordinator_id="PAPER-ATOMIC-BTCUSDT",
            symbol="BTCUSDT",
        )
        self.initial = self.coordinator.initialize(
            position=self.initial_flat,
            account=self.initial_account,
            throttle=self.initial_throttle,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    def _open_values(
        self,
        *,
        event_id: str = "ENTRY-1",
        trade_id: str = "TRADE-1",
        timestamp: str = "2026-08-09T10:00:00Z",
        tick_id: int = 100,
        system_state_id: str = "SYSTEM-1",
    ) -> tuple[PositionStateS2V2, EntryEconomicsQuote, AcceptedEntryEventV1]:
        current = self.coordinator.load_state()
        position, quote = make_open(
            current.account,
            self.config,
            trade_id=trade_id,
            system_state_id=system_state_id,
            timestamp=timestamp,
            tick_id=tick_id,
        )
        event = make_entry_event(
            current.throttle,
            self.policy,
            event_id=event_id,
            timestamp=timestamp,
        )
        return position, quote, event

    def _commit_open(self, **overrides: object):
        position, quote, event = self._open_values(
            **{
                key: value
                for key, value in overrides.items()
                if key
                in {
                    "event_id",
                    "trade_id",
                    "timestamp",
                    "tick_id",
                    "system_state_id",
                }
            }
        )
        result = self.coordinator.commit_open(
            position_after=position,
            accepted_entry_event=event,
            transition_tick_id=position.entry_tick_id,
            simulate_interruption_after_journal=bool(
                overrides.get("simulate_interruption_after_journal", False)
            ),
        )
        return result, quote, event

    def _close_values(
        self,
        quote: EntryEconomicsQuote,
        *,
        event_id: str = "SETTLE-1",
        exit_timestamp: str = "2026-08-09T11:00:00Z",
        exit_tick_id: int = 160,
        system_state_id: str = "SYSTEM-2",
    ) -> tuple[PositionStateS2FlatV2, TradeRecordV2]:
        current = self.coordinator.load_state()
        if not isinstance(current.position, PositionStateS2V2):
            raise AssertionError("test close requires OPEN state")
        trade = make_trade(
            current.account,
            self.config,
            quote,
            trade_id=current.position.trade_id,
            event_id=event_id,
            system_state_id=system_state_id,
            entry_timestamp=current.position.entry_timestamp_utc,
            exit_timestamp=exit_timestamp,
            entry_tick_id=current.position.entry_tick_id,
            exit_tick_id=exit_tick_id,
        )
        flat = make_flat(
            self.config,
            system_state_id=system_state_id,
            last_closed_trade_id=trade.trade_id,
        )
        return flat, trade

    def _commit_close(self, quote: EntryEconomicsQuote, **overrides: object):
        flat, trade = self._close_values(
            quote,
            **{
                key: value
                for key, value in overrides.items()
                if key
                in {
                    "event_id",
                    "exit_timestamp",
                    "exit_tick_id",
                    "system_state_id",
                }
            },
        )
        result = self.coordinator.commit_close(
            position_after=flat,
            trade=trade,
            simulate_interruption_after_journal=bool(
                overrides.get("simulate_interruption_after_journal", False)
            ),
        )
        return result, flat, trade

    def _commit_kill(self, **overrides: object):
        return self.coordinator.commit_kill_transition(
            transition_event_id=str(overrides.get("event_id", "KILL-1")),
            expected_from_kill_level=str(overrides.get("from_level", "NONE")),
            target_kill_level=str(overrides.get("to_level", "HARD")),
            reason_code=str(overrides.get("reason_code", "RISK_LIMIT_BREACH")),
            authorization_reference=str(
                overrides.get("authorization_reference", "AUTH-S4-TEST-1")
            ),
            transition_timestamp_utc=str(
                overrides.get("timestamp", "2026-08-09T10:00:00Z")
            ),
            transition_tick_id=int(overrides.get("tick_id", 100)),
            simulate_interruption_after_journal=bool(
                overrides.get("simulate_interruption_after_journal", False)
            ),
        )

    def test_initial_state_roundtrip_binds_all_component_fingerprints(self) -> None:
        restored = AtomicPaperStateV1.from_record(self.initial.to_record())

        self.assertEqual(restored, self.initial)
        self.assertEqual(restored.transaction_sequence, 0)
        self.assertTrue(restored.risk.entry_allowed)
        self.assertTrue(restored.risk.exit_allowed)
        self.assertEqual(
            restored.risk.position_fingerprint,
            restored.position.state_fingerprint,
        )
        self.assertEqual(
            restored.risk.account_fingerprint,
            restored.account.state_fingerprint,
        )
        self.assertEqual(
            restored.risk.throttle_fingerprint,
            restored.throttle.state_fingerprint,
        )

    def test_open_close_is_one_cross_component_transaction_chain(self) -> None:
        opened, quote, _ = self._commit_open()
        closed, _, trade = self._commit_close(quote)
        report = self.coordinator.reconciliation_report()

        self.assertEqual(opened.state.transaction_sequence, 1)
        self.assertEqual(opened.state.throttle.total_accepted_entry_count, 1)
        self.assertEqual(opened.state.account.closed_trade_count, 0)
        self.assertEqual(opened.state.position.trade_id, "TRADE-1")
        self.assertFalse(opened.state.risk.entry_allowed)
        self.assertIn(POSITION_OPEN_REASON, opened.state.risk.reason_codes)
        self.assertEqual(closed.state.transaction_sequence, 2)
        self.assertEqual(closed.state.account.closed_trade_count, 1)
        self.assertEqual(closed.state.account.last_settled_trade_id, trade.trade_id)
        self.assertEqual(closed.state.throttle.total_accepted_entry_count, 1)
        self.assertEqual(closed.state.position.last_closed_trade_id, trade.trade_id)
        self.assertTrue(closed.state.risk.entry_allowed)
        self.assertTrue(report.consistent)
        self.assertTrue(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(report.snapshot_transaction_sequence, 2)
        self.assertEqual(report.journal_transaction_count, 2)

    def test_open_interruption_recovers_complete_state_exactly_once(self) -> None:
        position, _, event = self._open_values()
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.commit_open(
                position_after=position,
                accepted_entry_event=event,
                transition_tick_id=position.entry_tick_id,
                simulate_interruption_after_journal=True,
            )

        before = self.coordinator.reconciliation_report()
        first = self.coordinator.recover()
        second = self.coordinator.recover()
        duplicate = self.coordinator.commit_open(
            position_after=position,
            accepted_entry_event=event,
            transition_tick_id=position.entry_tick_id,
        )

        self.assertFalse(before.consistent)
        self.assertFalse(before.entry_allowed)
        self.assertTrue(before.exit_allowed)
        self.assertEqual(
            before.reason_codes,
            (AtomicCoordinatorReasonCode.RECOVERY_REQUIRED,),
        )
        self.assertEqual(first.recovered_transaction_count, 1)
        self.assertEqual(second.recovered_transaction_count, 0)
        self.assertTrue(duplicate.already_committed)
        self.assertEqual(first.state, duplicate.state)

    def test_close_interruption_recovers_position_account_and_s4_together(self) -> None:
        _, quote, _ = self._commit_open()
        flat, trade = self._close_values(quote)
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.commit_close(
                position_after=flat,
                trade=trade,
                simulate_interruption_after_journal=True,
            )

        state_before_recovery = self.coordinator.load_state()
        recovered = self.coordinator.recover().state
        duplicate = self.coordinator.commit_close(
            position_after=flat,
            trade=trade,
        )

        self.assertEqual(state_before_recovery.position.position, "LONG")
        self.assertEqual(state_before_recovery.account.closed_trade_count, 0)
        self.assertEqual(recovered.position.position, "FLAT")
        self.assertEqual(recovered.account.closed_trade_count, 1)
        self.assertEqual(recovered.risk.account_fingerprint, recovered.account.state_fingerprint)
        self.assertTrue(duplicate.already_committed)

    def test_changed_duplicate_open_event_is_rejected(self) -> None:
        opened, _, event = self._commit_open()
        changed_position = replace(opened.state.position, system_state_id="OTHER")

        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.commit_open(
                position_after=changed_position,
                accepted_entry_event=event,
                transition_tick_id=changed_position.entry_tick_id,
            )

        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
        )

    def test_mismatched_settlement_trade_cannot_close_open_position(self) -> None:
        _, quote, _ = self._commit_open()
        flat, trade = self._close_values(quote)
        mismatched_trade = replace(trade, trade_id="OTHER-TRADE")
        mismatched_flat = replace(flat, last_closed_trade_id="OTHER-TRADE")

        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.commit_close(
                position_after=mismatched_flat,
                trade=mismatched_trade,
            )

        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
        )
        self.assertEqual(self.coordinator.load_state().position.position, "LONG")

    def test_s4_kill_level_blocks_open_without_journal_write(self) -> None:
        other_root = self.root / "killed"
        killed = PaperAtomicCoordinator(
            other_root,
            self.config,
            self.policy,
            coordinator_id="KILLED",
            symbol="BTCUSDT",
        )
        killed.initialize(
            position=self.initial_flat,
            account=self.initial_account,
            throttle=self.initial_throttle,
            kill_level="HARD",
        )
        position, _ = make_open(
            self.initial_account,
            self.config,
            trade_id="TRADE-KILLED",
            system_state_id="SYSTEM-KILLED",
            timestamp="2026-08-09T10:00:00Z",
            tick_id=100,
        )
        event = make_entry_event(
            self.initial_throttle,
            self.policy,
            event_id="ENTRY-KILLED",
            timestamp="2026-08-09T10:00:00Z",
        )

        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            killed.commit_open(
                position_after=position,
                accepted_entry_event=event,
                transition_tick_id=100,
            )

        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
        )
        self.assertEqual(list(killed.transaction_directory.glob("*.json")), [])

    def test_explicit_kill_transition_blocks_entry_and_preserves_exit(self) -> None:
        before = self.coordinator.load_state()
        result = self._commit_kill()

        self.assertEqual(result.state.transaction_sequence, 1)
        self.assertEqual(result.state.kill_transition_count, 1)
        self.assertEqual(result.state.risk.kill_level, "HARD")
        self.assertFalse(result.state.risk.entry_allowed)
        self.assertTrue(result.state.risk.exit_allowed)
        self.assertIn("PEE_S4_KILL_HARD", result.state.risk.reason_codes)
        self.assertEqual(result.state.position, before.position)
        self.assertEqual(result.state.account, before.account)
        self.assertEqual(result.state.throttle, before.throttle)

    def test_authorized_kill_deescalation_restores_flat_entry_permission(self) -> None:
        self._commit_kill()
        result = self._commit_kill(
            event_id="KILL-2",
            from_level="HARD",
            to_level="NONE",
            reason_code="MANUAL_RISK_CLEARANCE",
            authorization_reference="AUTH-S4-CLEAR-1",
            timestamp="2026-08-09T10:05:00Z",
            tick_id=105,
        )

        self.assertEqual(result.state.kill_transition_count, 2)
        self.assertEqual(result.state.risk.kill_level, "NONE")
        self.assertTrue(result.state.risk.entry_allowed)
        self.assertTrue(result.state.risk.exit_allowed)

    def test_kill_transition_while_open_never_blocks_exit(self) -> None:
        opened, _, _ = self._commit_open()
        result = self._commit_kill(
            event_id="KILL-OPEN-1",
            timestamp="2026-08-09T10:30:00Z",
            tick_id=130,
        )

        self.assertEqual(result.state.position, opened.state.position)
        self.assertEqual(result.state.account, opened.state.account)
        self.assertEqual(result.state.throttle, opened.state.throttle)
        self.assertEqual(result.state.kill_transition_count, 1)
        self.assertFalse(result.state.risk.entry_allowed)
        self.assertTrue(result.state.risk.exit_allowed)

    def test_kill_transition_requires_change_reason_and_authorization(self) -> None:
        invalid_values = (
            {"to_level": "NONE"},
            {"reason_code": ""},
            {"authorization_reference": ""},
        )
        for values in invalid_values:
            with self.subTest(values=values):
                with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                    self._commit_kill(**values)
                self.assertEqual(
                    caught.exception.reason_code,
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                )
        self.assertEqual(list(self.coordinator.transaction_directory.glob("*.json")), [])

    def test_kill_transition_rejects_stale_expected_level(self) -> None:
        self._commit_kill()

        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self._commit_kill(
                event_id="KILL-2",
                from_level="NONE",
                to_level="SOFT",
                timestamp="2026-08-09T10:05:00Z",
                tick_id=105,
            )

        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
        )
        self.assertEqual(self.coordinator.load_state().risk.kill_level, "HARD")

    def test_kill_interruption_recovers_exactly_once_and_is_idempotent(self) -> None:
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self._commit_kill(simulate_interruption_after_journal=True)

        before = self.coordinator.reconciliation_report()
        recovered = self.coordinator.recover()
        duplicate = self._commit_kill()

        self.assertFalse(before.consistent)
        self.assertFalse(before.entry_allowed)
        self.assertTrue(before.exit_allowed)
        self.assertEqual(recovered.recovered_transaction_count, 1)
        self.assertEqual(recovered.state.risk.kill_level, "HARD")
        self.assertTrue(duplicate.already_committed)
        self.assertEqual(duplicate.state, recovered.state)

    def test_changed_duplicate_kill_event_is_rejected(self) -> None:
        self._commit_kill()

        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self._commit_kill(reason_code="DIFFERENT_REASON")

        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
        )

    def test_open_record_without_optional_kill_payload_remains_readable(self) -> None:
        opened, _, _ = self._commit_open()
        record = json.loads(opened.journal_path.read_text(encoding="utf-8"))
        record.pop("kill_transition")
        opened.journal_path.write_text(json.dumps(record), encoding="utf-8")

        report = self.coordinator.reconciliation_report()

        self.assertTrue(report.consistent)
        self.assertEqual(report.snapshot_transaction_sequence, 1)
        self.assertTrue(report.exit_allowed)

    def test_corrupt_kill_transition_journal_fails_closed(self) -> None:
        result = self._commit_kill()
        record = json.loads(result.journal_path.read_text(encoding="utf-8"))
        record["kill_transition"]["authorization_reference"] = ""
        result.journal_path.write_text(json.dumps(record), encoding="utf-8")

        report = self.coordinator.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (AtomicCoordinatorReasonCode.TRANSACTION_INVALID,),
        )

    def test_throttle_limit_blocks_second_open_without_partial_state(self) -> None:
        limited_policy = make_policy(max_entries_per_utc_day=1)
        other_root = self.root / "limited"
        limited = PaperAtomicCoordinator(
            other_root,
            self.config,
            limited_policy,
            coordinator_id="LIMITED",
            symbol="BTCUSDT",
        )
        limited_throttle = PaperEntryThrottleState.initial(
            limited_policy,
            utc_day="2026-08-09",
        )
        limited.initialize(
            position=self.initial_flat,
            account=self.initial_account,
            throttle=limited_throttle,
        )
        first_position, first_quote = make_open(
            self.initial_account,
            self.config,
            trade_id="TRADE-1",
            system_state_id="SYSTEM-1",
            timestamp="2026-08-09T10:00:00Z",
            tick_id=100,
        )
        first_event = make_entry_event(
            limited_throttle,
            limited_policy,
            event_id="ENTRY-1",
            timestamp="2026-08-09T10:00:00Z",
        )
        limited.commit_open(
            position_after=first_position,
            accepted_entry_event=first_event,
            transition_tick_id=100,
        )
        current = limited.load_state()
        first_trade = make_trade(
            current.account,
            self.config,
            first_quote,
            trade_id="TRADE-1",
            event_id="SETTLE-1",
            system_state_id="SYSTEM-2",
            entry_timestamp="2026-08-09T10:00:00Z",
            exit_timestamp="2026-08-09T11:00:00Z",
            entry_tick_id=100,
            exit_tick_id=160,
        )
        limited.commit_close(
            position_after=make_flat(
                self.config,
                system_state_id="SYSTEM-2",
                last_closed_trade_id="TRADE-1",
            ),
            trade=first_trade,
        )
        before = limited.load_state()
        second_position, _ = make_open(
            before.account,
            self.config,
            trade_id="TRADE-2",
            system_state_id="SYSTEM-3",
            timestamp="2026-08-09T12:00:00Z",
            tick_id=200,
        )
        second_event = make_entry_event(
            before.throttle,
            limited_policy,
            event_id="ENTRY-2",
            timestamp="2026-08-09T12:00:00Z",
        )

        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            limited.commit_open(
                position_after=second_position,
                accepted_entry_event=second_event,
                transition_tick_id=200,
            )

        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
        )
        self.assertEqual(limited.load_state(), before)
        self.assertEqual(len(list(limited.transaction_directory.glob("*.json"))), 2)

    def test_corrupt_s4_binding_fails_closed_but_keeps_exit_permission(self) -> None:
        self._commit_open()
        record = json.loads(self.coordinator.state_path.read_text(encoding="utf-8"))
        record["risk"]["position_fingerprint"] = "0" * 64
        self.coordinator.state_path.write_text(json.dumps(record), encoding="utf-8")

        report = self.coordinator.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,),
        )

    def test_corrupt_journal_chain_fails_closed(self) -> None:
        opened, quote, _ = self._commit_open()
        closed, _, _ = self._commit_close(quote)
        record = json.loads(closed.journal_path.read_text(encoding="utf-8"))
        record["previous_transaction_event_id"] = "WRONG"
        closed.journal_path.write_text(json.dumps(record), encoding="utf-8")

        report = self.coordinator.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertIn(
            report.reason_codes[0],
            {
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                AtomicCoordinatorReasonCode.JOURNAL_GAP,
            },
        )
        self.assertEqual(opened.state.position.position, "LONG")

    def test_snapshot_ahead_of_deleted_journal_is_not_recoverable(self) -> None:
        opened, _, _ = self._commit_open()
        opened.journal_path.unlink()

        report = self.coordinator.reconciliation_report()
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.recover()

        self.assertFalse(report.consistent)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (AtomicCoordinatorReasonCode.STATE_AHEAD_OF_JOURNAL,),
        )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.STATE_AHEAD_OF_JOURNAL,
        )

    def test_transaction_time_and_tick_cannot_regress(self) -> None:
        _, quote, _ = self._commit_open()
        self._commit_close(quote)
        position, _, event = self._open_values(
            event_id="ENTRY-2",
            trade_id="TRADE-2",
            timestamp="2026-08-09T10:30:00Z",
            tick_id=150,
            system_state_id="SYSTEM-3",
        )

        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.commit_open(
                position_after=position,
                accepted_entry_event=event,
                transition_tick_id=150,
            )

        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
        )
        self.assertEqual(self.coordinator.load_state().transaction_sequence, 2)

    def test_persisted_aggregate_contains_no_binary_floats(self) -> None:
        self._commit_open()
        record = json.loads(self.coordinator.state_path.read_text(encoding="utf-8"))

        self.assertFalse(contains_float(record))
        self.assertIsInstance(record["position"]["quantity"], str)
        self.assertIsInstance(record["account"]["realized_equity_quote"], str)

    def test_initialization_is_idempotent_and_rejects_nonempty_components(self) -> None:
        self.assertEqual(
            self.coordinator.initialize(
                position=self.initial_flat,
                account=self.initial_account,
                throttle=self.initial_throttle,
            ),
            self.initial,
        )
        nonempty_flat = make_flat(
            self.config,
            system_state_id="SYSTEM-OLD",
            last_closed_trade_id="OLD-TRADE",
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.initialize(
                position=nonempty_flat,
                account=self.initial_account,
                throttle=self.initial_throttle,
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
        )


if __name__ == "__main__":
    unittest.main()
