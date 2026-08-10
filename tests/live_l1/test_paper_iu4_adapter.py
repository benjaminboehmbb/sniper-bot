#!/usr/bin/env python3

from __future__ import annotations

import shutil
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from live_l1.core.paper_economics import PaperEconomicsConfig
from live_l1.core.paper_entry_throttle import (
    PaperEntryThrottlePolicy,
    PaperEntryThrottleState,
)
from live_l1.core.paper_iu4_adapter import (
    ACTION_CLOSE_LONG,
    ACTION_CLOSE_SHORT,
    ACTION_NOOP,
    ACTION_OPEN_LONG,
    ACTION_OPEN_SHORT,
    IU4AdapterReasonCode,
    IU4AdapterRequestV1,
    PaperIU4Adapter,
    PaperIU4AdapterError,
    STATUS_COMMITTED,
    STATUS_NOOP,
    STATUS_REJECTED,
)
from live_l1.state.paper_artifacts import (
    PaperAccountState,
    PositionStateS2FlatV2,
)
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator


D = Decimal


def make_config() -> PaperEconomicsConfig:
    return PaperEconomicsConfig(
        schema_version=1,
        economics_model_version="PEE_V1",
        economics_profile_id="TEST_IU4_ADAPTER",
        quote_currency="USDT",
        starting_equity_quote=D("10000"),
        risk_per_trade_rate=D("0.01"),
        max_position_notional_rate=D("0.05"),
        entry_fee_rate=D("0.0005"),
        exit_fee_rate=D("0.0005"),
        entry_slippage_bps=D("2"),
        exit_slippage_bps=D("2"),
        quantity_step=D("0.001"),
        min_quantity=D("0.001"),
        min_notional_quote=D("5"),
        max_daily_loss_rate=D("0.03"),
        max_daily_fee_rate=D("0.01"),
        max_realized_drawdown_rate=D("0.10"),
    )


def make_policy() -> PaperEntryThrottlePolicy:
    return PaperEntryThrottlePolicy(
        schema_version=1,
        policy_model_version="PEE_RATE_V1",
        policy_profile_id="TEST_IU4_RATE",
        max_entries_per_utc_day=10,
        max_entries_per_rolling_window=3,
        rolling_window_seconds=3600,
        min_reentry_cooldown_seconds=60,
    )


class PaperIU4AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-iu4-adapter-")
        self.root = Path(self.temporary_directory)
        self.config = make_config()
        self.policy = make_policy()
        flat = PositionStateS2FlatV2(
            schema_version=2,
            system_state_id="SYSTEM-0",
            symbol="BTCUSDT",
            position="FLAT",
            side="",
            last_closed_trade_id="",
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        account = PaperAccountState.initial(
            account_id="PAPER-IU4-BTCUSDT",
            quote_currency=self.config.quote_currency,
            starting_equity_quote=self.config.starting_equity_quote,
            utc_day="2026-08-09",
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        throttle = PaperEntryThrottleState.initial(
            self.policy,
            utc_day="2026-08-09",
        )
        self.coordinator = PaperAtomicCoordinator(
            self.root,
            self.config,
            self.policy,
            coordinator_id="IU4-ADAPTER-BTCUSDT",
            symbol="BTCUSDT",
        )
        self.coordinator.initialize(
            position=flat,
            account=account,
            throttle=throttle,
        )
        self.adapter = PaperIU4Adapter(self.coordinator)

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    def _request(self, **overrides: object) -> IU4AdapterRequestV1:
        state = self.coordinator.load_state()
        intent = str(overrides.get("intent", "BUY"))
        position_trade_id = (
            "" if state.position.position == "FLAT" else state.position.trade_id
        )
        default_trade_id = "TRADE-1" if state.position.position == "FLAT" else position_trade_id
        default_stop = D("95") if intent == "BUY" and state.position.position == "FLAT" else (
            D("105") if intent == "SELL" and state.position.position == "FLAT" else None
        )
        return IU4AdapterRequestV1(
            schema_version=1,
            request_id=str(overrides.get("request_id", "")),
            source_intent_id=str(overrides.get("source_intent_id", "INTENT-1")),
            intent_final=intent,
            intent_reason_code=str(overrides.get("reason", "FUSED_INTENT")),
            expected_state_fingerprint=str(
                overrides.get("expected_fingerprint", state.state_fingerprint)
            ),
            target_system_state_id=str(
                overrides.get("system_state_id", "SYSTEM-1")
            ),
            timestamp_utc=str(
                overrides.get("timestamp", "2026-08-09T10:00:00Z")
            ),
            tick_id=int(overrides.get("tick_id", 100)),
            reference_price=overrides.get("price", D("100")),
            reference_stop_price=overrides.get("stop", default_stop),
            trade_id=str(overrides.get("trade_id", default_trade_id)),
        )

    def _open_long(self):
        request = self._request()
        return request, self.adapter.execute(request)

    def _open_short(self):
        request = self._request(
            intent="SELL",
            source_intent_id="INTENT-SHORT-1",
            trade_id="TRADE-SHORT-1",
        )
        return request, self.adapter.execute(request)

    def test_request_is_content_addressed_and_roundtrips(self) -> None:
        request = self._request()
        restored = IU4AdapterRequestV1.from_record(request.to_record())

        self.assertEqual(restored, request)
        self.assertEqual(request.request_id, f"PEE-IU4-{request.request_fingerprint}")
        self.assertEqual(request.to_record()["reference_price"], "100")

    def test_request_rejects_float_unknown_field_and_changed_supplied_id(self) -> None:
        with self.assertRaises(PaperIU4AdapterError):
            self._request(price=100.0)

        record = self._request().to_record()
        record["unknown"] = True
        with self.assertRaises(PaperIU4AdapterError):
            IU4AdapterRequestV1.from_record(record)

        valid = self._request()
        with self.assertRaises(PaperIU4AdapterError):
            replace(valid, intent_reason_code="CHANGED")

    def test_flat_buy_commits_decimal_open_long_only_through_coordinator(self) -> None:
        request, result = self._open_long()

        self.assertEqual(result.status, STATUS_COMMITTED)
        self.assertEqual(result.schema_version, 1)
        self.assertEqual(result.action, ACTION_OPEN_LONG)
        self.assertEqual(result.state.position.position, "LONG")
        self.assertEqual(result.state.position.trade_id, "TRADE-1")
        self.assertIsInstance(result.state.position.quantity, Decimal)
        self.assertEqual(result.transaction_event_id, request.request_id)
        self.assertTrue(result.newly_committed)
        self.assertEqual(len(list(self.coordinator.transaction_directory.glob("*.json"))), 1)

    def test_flat_sell_commits_open_short(self) -> None:
        _, result = self._open_short()

        self.assertEqual(result.action, ACTION_OPEN_SHORT)
        self.assertEqual(result.state.position.position, "SHORT")
        self.assertEqual(result.state.position.trade_id, "TRADE-SHORT-1")

    def test_long_sell_closes_without_same_tick_reversal(self) -> None:
        self._open_long()
        request = self._request(
            intent="SELL",
            source_intent_id="INTENT-2",
            reason="EXIT_LONG_ON_1M_SELL",
            system_state_id="SYSTEM-2",
            timestamp="2026-08-09T11:00:00Z",
            tick_id=160,
            price=D("110"),
        )
        result = self.adapter.execute(request)

        self.assertEqual(result.action, ACTION_CLOSE_LONG)
        self.assertEqual(result.state.position.position, "FLAT")
        self.assertEqual(result.state.account.closed_trade_count, 1)
        self.assertEqual(result.state.account.last_settled_trade_id, "TRADE-1")
        self.assertEqual(result.state.transaction_sequence, 2)

    def test_short_buy_closes_without_same_tick_reversal(self) -> None:
        self._open_short()
        request = self._request(
            intent="BUY",
            source_intent_id="INTENT-SHORT-2",
            reason="EXIT_SHORT_ON_1M_BUY",
            system_state_id="SYSTEM-SHORT-2",
            timestamp="2026-08-09T11:00:00Z",
            tick_id=160,
            price=D("90"),
        )
        result = self.adapter.execute(request)

        self.assertEqual(result.action, ACTION_CLOSE_SHORT)
        self.assertEqual(result.state.position.position, "FLAT")
        self.assertEqual(result.state.account.closed_trade_count, 1)

    def test_hold_and_same_side_are_noop_without_journal_write(self) -> None:
        hold = self._request(
            intent="HOLD",
            source_intent_id="HOLD-1",
            system_state_id="SYSTEM-0",
            trade_id="",
        )
        hold_result = self.adapter.execute(hold)
        self.assertEqual(hold_result.status, STATUS_NOOP)
        self.assertEqual(hold_result.action, ACTION_NOOP)
        self.assertEqual(hold_result.reason_code, IU4AdapterReasonCode.HOLD)
        self.assertEqual(list(self.coordinator.transaction_directory.glob("*.json")), [])

        self._open_long()
        same_side = self._request(
            intent="BUY",
            source_intent_id="BUY-ALREADY-LONG",
            system_state_id="SYSTEM-1",
            stop=None,
        )
        same_side_result = self.adapter.execute(same_side)
        self.assertEqual(same_side_result.status, STATUS_NOOP)
        self.assertEqual(
            same_side_result.reason_code,
            IU4AdapterReasonCode.ALREADY_POSITIONED,
        )
        self.assertEqual(len(list(self.coordinator.transaction_directory.glob("*.json"))), 1)

    def test_kill_blocks_entry_without_wal_but_never_blocks_exit(self) -> None:
        self.coordinator.commit_kill_transition(
            transition_event_id="KILL-1",
            expected_from_kill_level="NONE",
            target_kill_level="HARD",
            reason_code="RISK_LIMIT",
            authorization_reference="AUTH-KILL-1",
            transition_timestamp_utc="2026-08-09T09:00:00Z",
            transition_tick_id=90,
        )
        blocked = self.adapter.execute(
            self._request(timestamp="2026-08-09T10:00:00Z", tick_id=100)
        )
        self.assertEqual(blocked.status, STATUS_REJECTED)
        self.assertEqual(blocked.reason_code, "PEE_S4_KILL_HARD")
        self.assertEqual(len(list(self.coordinator.transaction_directory.glob("*.json"))), 1)

        self.coordinator.commit_kill_transition(
            transition_event_id="KILL-2",
            expected_from_kill_level="HARD",
            target_kill_level="NONE",
            reason_code="TEST_CLEAR",
            authorization_reference="AUTH-KILL-2",
            transition_timestamp_utc="2026-08-09T10:05:00Z",
            transition_tick_id=105,
        )
        open_after_clear = self._request(
            source_intent_id="INTENT-AFTER-CLEAR",
            timestamp="2026-08-09T10:10:00Z",
            tick_id=110,
        )
        self.adapter.execute(open_after_clear)
        self.coordinator.commit_kill_transition(
            transition_event_id="KILL-3",
            expected_from_kill_level="NONE",
            target_kill_level="EMERGENCY",
            reason_code="EMERGENCY_TEST",
            authorization_reference="AUTH-KILL-3",
            transition_timestamp_utc="2026-08-09T10:30:00Z",
            transition_tick_id=130,
        )
        close = self._request(
            intent="SELL",
            source_intent_id="EXIT-DURING-KILL",
            reason="EXIT_LONG_DURING_KILL",
            system_state_id="SYSTEM-2",
            timestamp="2026-08-09T11:00:00Z",
            tick_id=160,
            price=D("110"),
        )
        closed = self.adapter.execute(close)
        self.assertEqual(closed.action, ACTION_CLOSE_LONG)
        self.assertTrue(closed.state.risk.exit_allowed)
        self.assertEqual(closed.state.risk.kill_level, "EMERGENCY")

    def test_stale_state_is_rejected_without_mutation(self) -> None:
        stale = self._request()
        self.coordinator.commit_kill_transition(
            transition_event_id="KILL-STALE",
            expected_from_kill_level="NONE",
            target_kill_level="SOFT",
            reason_code="TEST",
            authorization_reference="AUTH-STALE",
            transition_timestamp_utc="2026-08-09T09:00:00Z",
            transition_tick_id=90,
        )
        before = self.coordinator.load_state()
        result = self.adapter.execute(stale)

        self.assertEqual(result.status, STATUS_REJECTED)
        self.assertEqual(result.reason_code, IU4AdapterReasonCode.STATE_MISMATCH)
        self.assertEqual(self.coordinator.load_state(), before)

    def test_reentry_cooldown_blocks_adapter_open_without_new_wal(self) -> None:
        self._open_long()
        close = self._request(
            intent="SELL",
            source_intent_id="FAST-CLOSE",
            reason="FAST_TEST_EXIT",
            system_state_id="SYSTEM-2",
            timestamp="2026-08-09T10:00:30Z",
            tick_id=101,
            price=D("110"),
        )
        self.adapter.execute(close)
        second_open = self._request(
            source_intent_id="FAST-REENTRY",
            trade_id="TRADE-2",
            system_state_id="SYSTEM-3",
            timestamp="2026-08-09T10:00:40Z",
            tick_id=102,
        )
        rejected = self.adapter.execute(second_open)

        self.assertEqual(rejected.status, STATUS_REJECTED)
        self.assertEqual(rejected.reason_code, "PEE_RATE_REENTRY_COOLDOWN")
        self.assertEqual(rejected.state.position.position, "FLAT")
        self.assertEqual(len(list(self.coordinator.transaction_directory.glob("*.json"))), 2)

    def test_daily_loss_blocks_same_day_but_not_next_utc_day(self) -> None:
        self._open_long()
        close = self._request(
            intent="SELL",
            source_intent_id="LOSS-CLOSE",
            reason="LOSS_TEST_EXIT",
            system_state_id="SYSTEM-2",
            timestamp="2026-08-09T11:00:00Z",
            tick_id=160,
            price=D("1"),
        )
        closed = self.adapter.execute(close)
        same_day = self.adapter.execute(
            self._request(
                source_intent_id="SAME-DAY-OPEN",
                trade_id="TRADE-2",
                system_state_id="SYSTEM-3",
                timestamp="2026-08-09T12:00:00Z",
                tick_id=220,
            )
        )
        next_day = self.adapter.execute(
            self._request(
                source_intent_id="NEXT-DAY-OPEN",
                trade_id="TRADE-3",
                system_state_id="SYSTEM-4",
                timestamp="2026-08-10T00:00:00Z",
                tick_id=940,
            )
        )

        self.assertEqual(closed.status, STATUS_COMMITTED)
        self.assertEqual(same_day.status, STATUS_REJECTED)
        self.assertEqual(same_day.reason_code, "PEE_RISK_DAILY_LOSS_LIMIT")
        self.assertEqual(next_day.status, STATUS_COMMITTED)
        self.assertEqual(next_day.action, ACTION_OPEN_LONG)
        self.assertEqual(next_day.state.position.trade_id, "TRADE-3")

    def test_invalid_open_binding_and_economics_leave_state_unchanged(self) -> None:
        before = self.coordinator.load_state()
        with self.assertRaises(PaperIU4AdapterError):
            self.adapter.execute(self._request(trade_id=""))
        rejected = self.adapter.execute(self._request(stop=D("105")))

        self.assertEqual(rejected.status, STATUS_REJECTED)
        self.assertEqual(self.coordinator.load_state(), before)
        self.assertEqual(list(self.coordinator.transaction_directory.glob("*.json")), [])

    def test_exact_open_and_close_retries_are_idempotent(self) -> None:
        open_request, opened = self._open_long()
        open_retry = self.adapter.execute(open_request)
        self.assertTrue(open_retry.already_committed)
        self.assertEqual(open_retry.state, opened.state)

        close_request = self._request(
            intent="SELL",
            source_intent_id="INTENT-2",
            reason="EXIT_LONG_ON_1M_SELL",
            system_state_id="SYSTEM-2",
            timestamp="2026-08-09T11:00:00Z",
            tick_id=160,
            price=D("110"),
        )
        closed = self.adapter.execute(close_request)
        close_retry = self.adapter.execute(close_request)

        self.assertTrue(close_retry.already_committed)
        self.assertEqual(close_retry.state, closed.state)
        self.assertEqual(len(list(self.coordinator.transaction_directory.glob("*.json"))), 2)


if __name__ == "__main__":
    unittest.main()
