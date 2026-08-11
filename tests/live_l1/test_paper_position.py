#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from live_l1.core.paper_economics import PaperEconomicsConfig
from live_l1.state.paper_artifacts import (
    ArtifactReasonCode,
    PaperArtifactError,
    PositionStateS2FlatV2,
    PositionStateS2V2,
    parse_position_artifact,
)
from live_l1.state.paper_position import (
    PaperPositionStore,
    PaperPositionStoreError,
    PaperPositionStoreReasonCode,
    SimulatedPositionTransitionInterruption,
)


D = Decimal


def make_config(**overrides: object) -> PaperEconomicsConfig:
    values: dict[str, object] = {
        "schema_version": 1,
        "economics_model_version": "PEE_V1",
        "economics_profile_id": "TEST_S2_V2_PROFILE",
        "quote_currency": "USDT",
        "starting_equity_quote": D("10000"),
        "risk_per_trade_rate": D("0.0025"),
        "max_position_notional_rate": D("0.10"),
        "entry_fee_rate": D("0.001"),
        "exit_fee_rate": D("0.001"),
        "entry_slippage_bps": D("2"),
        "exit_slippage_bps": D("2"),
        "quantity_step": D("0.001"),
        "min_quantity": D("0.001"),
        "min_notional_quote": D("5"),
        "max_daily_loss_rate": D("0.01"),
        "max_daily_fee_rate": D("0.0025"),
        "max_realized_drawdown_rate": D("0.05"),
    }
    values.update(overrides)
    return PaperEconomicsConfig(**values)


def make_flat(
    config: PaperEconomicsConfig,
    *,
    system_state_id: str = "SYSTEM-1",
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


def make_open(
    config: PaperEconomicsConfig,
    *,
    system_state_id: str = "SYSTEM-1",
    trade_id: str = "TRADE-1",
    position: str = "LONG",
) -> PositionStateS2V2:
    if position == "LONG":
        reference_price = D("100")
        fill_price = D("100.02")
        stop_price = D("85")
    else:
        reference_price = D("100")
        fill_price = D("99.98")
        stop_price = D("115")
    quantity = D("1")
    return PositionStateS2V2(
        schema_version=2,
        system_state_id=system_state_id,
        symbol="BTCUSDT",
        position=position,
        side=position,
        trade_id=trade_id,
        reference_entry_price=reference_price,
        modeled_entry_fill_price=fill_price,
        quantity=quantity,
        entry_notional_quote=quantity * fill_price,
        entry_fee_quote=D("0.10002"),
        risk_budget_quote=D("25"),
        modeled_stop_loss_quote=D("15.02") if position == "LONG" else D("14.98"),
        reference_stop_price=stop_price,
        entry_timestamp_utc="2026-08-09T10:00:00Z",
        entry_tick_id=100,
        economics_profile_id=config.economics_profile_id,
        economics_model_version=config.economics_model_version,
        config_fingerprint=config.config_fingerprint,
    )


class PositionStateS2V2ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = make_config()

    def test_flat_roundtrip_dispatch_and_fingerprint_are_stable(self) -> None:
        state = make_flat(self.config)
        record = state.to_record()

        restored = PositionStateS2FlatV2.from_record(record)

        self.assertEqual(restored, state)
        self.assertEqual(parse_position_artifact(record), state)
        self.assertEqual(restored.state_fingerprint, state.state_fingerprint)
        self.assertEqual(record["position"], "FLAT")
        self.assertEqual(record["side"], "")
        self.assertNotIn("entry_price", record)
        self.assertNotIn("quantity", record)

    def test_flat_rejects_side_and_nonflat_position(self) -> None:
        for changes in (
            {"side": "LONG"},
            {"position": "LONG"},
        ):
            with self.subTest(changes=changes):
                record = make_flat(self.config).to_record()
                record.update(changes)
                with self.assertRaises(PaperArtifactError) as caught:
                    PositionStateS2FlatV2.from_record(record)
                self.assertEqual(
                    caught.exception.reason_code,
                    ArtifactReasonCode.ARTIFACT_INVALID,
                )

    def test_open_state_fingerprint_is_stable(self) -> None:
        state = make_open(self.config)
        restored = PositionStateS2V2.from_record(state.to_record())

        self.assertEqual(restored, state)
        self.assertEqual(restored.state_fingerprint, state.state_fingerprint)

    def test_open_rejects_broken_economic_identities(self) -> None:
        state = make_open(self.config)
        cases = (
            {"entry_notional_quote": "999"},
            {"modeled_entry_fill_price": "99", "entry_notional_quote": "99"},
            {"modeled_stop_loss_quote": "26"},
        )
        for changes in cases:
            with self.subTest(changes=changes):
                record = state.to_record()
                record.update(changes)
                with self.assertRaises(PaperArtifactError) as caught:
                    PositionStateS2V2.from_record(record)
                self.assertEqual(
                    caught.exception.reason_code,
                    ArtifactReasonCode.ARTIFACT_INVALID,
                )

    def test_reader_rejects_unknown_v2_position(self) -> None:
        record = make_flat(self.config).to_record()
        record["position"] = "PAUSED"

        with self.assertRaises(PaperArtifactError) as caught:
            parse_position_artifact(record)

        self.assertEqual(
            caught.exception.reason_code,
            ArtifactReasonCode.ARTIFACT_INVALID,
        )

    def test_v2_schema_requires_an_integer_and_entry_time_requires_seconds(self) -> None:
        for state in (make_flat(self.config), make_open(self.config)):
            for invalid_version in (2.0, True):
                with self.subTest(state=state.position, version=invalid_version):
                    record = state.to_record()
                    record["schema_version"] = invalid_version
                    with self.assertRaises(PaperArtifactError):
                        parse_position_artifact(record)

        record = make_open(self.config).to_record()
        record["entry_timestamp_utc"] = "2026-08-09T10:00:00.001Z"
        with self.assertRaises(PaperArtifactError) as caught:
            PositionStateS2V2.from_record(record)
        self.assertEqual(
            caught.exception.reason_code,
            ArtifactReasonCode.ARTIFACT_INVALID,
        )


class PaperPositionStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-s2-v2-test-")
        self.root = Path(self.temporary_directory)
        self.config = make_config()
        self.initial = make_flat(self.config)
        self.open_state = make_open(self.config)
        self.store = PaperPositionStore(
            self.root,
            self.config,
            symbol="BTCUSDT",
        )
        self.store.initialize(self.initial)

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    def _open(self, **overrides: object):
        values = {
            "transition_event_id": "ENTRY-EVENT-1",
            "transition_timestamp_utc": "2026-08-09T10:00:00Z",
            "transition_tick_id": 100,
            "state_after": self.open_state,
        }
        values.update(overrides)
        return self.store.commit_transition(**values)

    def _close(self, open_state: PositionStateS2V2, **overrides: object):
        values = {
            "transition_event_id": "EXIT-EVENT-1",
            "transition_timestamp_utc": "2026-08-09T11:00:00Z",
            "transition_tick_id": 160,
            "state_after": make_flat(
                self.config,
                system_state_id="SYSTEM-2",
                last_closed_trade_id=open_state.trade_id,
            ),
        }
        values.update(overrides)
        return self.store.commit_transition(**values)

    def test_initialization_is_idempotent_and_requires_flat(self) -> None:
        self.assertEqual(self.store.initialize(self.initial), self.initial)

        with self.assertRaises(PaperPositionStoreError) as different:
            self.store.initialize(replace(self.initial, system_state_id="OTHER"))
        self.assertEqual(
            different.exception.reason_code,
            PaperPositionStoreReasonCode.STATE_ALREADY_INITIALIZED,
        )

        other_store = PaperPositionStore(
            self.root / "open-init",
            self.config,
            symbol="BTCUSDT",
        )
        with self.assertRaises(PaperPositionStoreError) as open_error:
            other_store.initialize(self.open_state)
        self.assertEqual(
            open_error.exception.reason_code,
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
        )

    def test_open_close_chain_roundtrips_after_restart(self) -> None:
        opened = self._open()
        closed = self._close(opened.state)
        restarted = PaperPositionStore(
            self.root,
            self.config,
            symbol="BTCUSDT",
        )

        report = restarted.reconciliation_report()

        self.assertTrue(opened.newly_committed)
        self.assertTrue(closed.newly_committed)
        self.assertIsInstance(closed.state, PositionStateS2FlatV2)
        self.assertEqual(closed.state.last_closed_trade_id, "TRADE-1")
        self.assertTrue(report.consistent)
        self.assertTrue(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(report.current_position, "FLAT")
        self.assertEqual(report.journal_transition_count, 2)
        self.assertEqual(restarted.load_state(), closed.state)
        self.assertEqual(len(list(self.store.transition_directory.glob("*.json"))), 2)

    def test_invalid_flat_to_flat_and_open_to_open_are_rejected(self) -> None:
        with self.assertRaises(PaperPositionStoreError) as flat_error:
            self.store.commit_transition(
                transition_event_id="BAD-FLAT",
                transition_timestamp_utc="2026-08-09T10:00:00Z",
                transition_tick_id=100,
                state_after=make_flat(self.config, system_state_id="SYSTEM-2"),
            )
        self.assertEqual(
            flat_error.exception.reason_code,
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
        )

        opened = self._open().state
        with self.assertRaises(PaperPositionStoreError) as open_error:
            self.store.commit_transition(
                transition_event_id="BAD-OPEN",
                transition_timestamp_utc="2026-08-09T10:01:00Z",
                transition_tick_id=101,
                state_after=replace(opened, trade_id="TRADE-2"),
            )
        self.assertEqual(
            open_error.exception.reason_code,
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
        )

    def test_close_requires_exact_open_trade_id(self) -> None:
        opened = self._open().state
        wrong_flat = make_flat(
            self.config,
            system_state_id="SYSTEM-2",
            last_closed_trade_id="OTHER-TRADE",
        )

        with self.assertRaises(PaperPositionStoreError) as caught:
            self._close(opened, state_after=wrong_flat)

        self.assertEqual(
            caught.exception.reason_code,
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
        )
        self.assertEqual(self.store.load_state(), opened)

    def test_interruption_is_recovered_exactly_once(self) -> None:
        with self.assertRaises(SimulatedPositionTransitionInterruption):
            self._open(simulate_interruption_after_journal=True)

        before = self.store.reconciliation_report()
        first = self.store.recover()
        second = self.store.recover()
        duplicate = self._open()

        self.assertFalse(before.consistent)
        self.assertFalse(before.entry_allowed)
        self.assertTrue(before.exit_allowed)
        self.assertEqual(
            before.reason_codes,
            (PaperPositionStoreReasonCode.RECOVERY_REQUIRED,),
        )
        self.assertEqual(first.recovered_transition_count, 1)
        self.assertEqual(second.recovered_transition_count, 0)
        self.assertTrue(duplicate.already_committed)
        self.assertEqual(first.state, self.open_state)
        self.assertEqual(second.state, self.open_state)

    def test_old_duplicate_after_close_is_idempotent(self) -> None:
        open_result = self._open()
        closed = self._close(open_result.state).state

        duplicate = self._open()

        self.assertTrue(duplicate.already_committed)
        self.assertEqual(duplicate.state, closed)
        self.assertEqual(self.store.load_state(), closed)

    def test_changed_duplicate_event_is_conflict(self) -> None:
        self._open()

        with self.assertRaises(PaperPositionStoreError) as caught:
            self._open(transition_tick_id=101)

        self.assertEqual(
            caught.exception.reason_code,
            PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
        )

    def test_trade_id_cannot_be_reopened(self) -> None:
        opened = self._open().state
        self._close(opened)
        duplicate_trade = replace(
            self.open_state,
            system_state_id="SYSTEM-3",
            entry_timestamp_utc="2026-08-09T12:00:00Z",
            entry_tick_id=200,
        )

        with self.assertRaises(PaperPositionStoreError) as caught:
            self.store.commit_transition(
                transition_event_id="ENTRY-EVENT-2",
                transition_timestamp_utc="2026-08-09T12:00:00Z",
                transition_tick_id=200,
                state_after=duplicate_trade,
            )

        self.assertEqual(
            caught.exception.reason_code,
            PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
        )

    def test_open_event_must_match_entry_time_and_tick(self) -> None:
        for changes in (
            {"transition_timestamp_utc": "2026-08-09T10:00:01Z"},
            {"transition_tick_id": 101},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(PaperPositionStoreError) as caught:
                    self._open(**changes)
                self.assertEqual(
                    caught.exception.reason_code,
                    PaperPositionStoreReasonCode.TRANSITION_INVALID,
                )

    def test_open_snapshot_without_transition_journal_fails_closed(self) -> None:
        self.store.state_path.write_text(
            json.dumps(self.open_state.to_record()),
            encoding="utf-8",
        )

        report = self.store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (PaperPositionStoreReasonCode.JOURNAL_CONFLICT,),
        )

    def test_transition_time_and_tick_cannot_regress(self) -> None:
        opened = self._open().state
        self._close(opened)
        earlier_open = replace(
            self.open_state,
            system_state_id="SYSTEM-3",
            trade_id="TRADE-2",
            entry_timestamp_utc="2026-08-09T10:30:00Z",
            entry_tick_id=150,
        )

        with self.assertRaises(PaperPositionStoreError) as caught:
            self.store.commit_transition(
                transition_event_id="ENTRY-EVENT-2",
                transition_timestamp_utc="2026-08-09T10:30:00Z",
                transition_tick_id=150,
                state_after=earlier_open,
            )

        self.assertEqual(
            caught.exception.reason_code,
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
        )

    def test_profile_mismatch_is_rejected_before_write(self) -> None:
        other_config = make_config(economics_profile_id="OTHER")
        mismatched = make_open(other_config)

        with self.assertRaises(PaperArtifactError) as caught:
            self._open(state_after=mismatched)

        self.assertEqual(
            caught.exception.reason_code,
            ArtifactReasonCode.CONFIG_MISMATCH,
        )
        self.assertEqual(len(list(self.store.transition_directory.glob("*.json"))), 0)

    def test_corrupt_snapshot_fails_closed_but_keeps_exit_permission(self) -> None:
        self.store.state_path.write_text("{broken", encoding="utf-8")

        report = self.store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (PaperPositionStoreReasonCode.JSON_INVALID,),
        )

    def test_legacy_snapshot_fails_closed_but_keeps_exit_permission(self) -> None:
        self.store.state_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "position": "LONG",
                    "entry_price": 100.0,
                }
            ),
            encoding="utf-8",
        )

        report = self.store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (ArtifactReasonCode.LEGACY_ECONOMICS_INCOMPLETE,),
        )

    def test_broken_journal_chain_fails_closed(self) -> None:
        opened = self._open().state
        close_result = self._close(opened)
        record = json.loads(close_result.journal_path.read_text(encoding="utf-8"))
        record["previous_transition_event_id"] = "WRONG"
        close_result.journal_path.write_text(json.dumps(record), encoding="utf-8")

        report = self.store.reconciliation_report()

        self.assertFalse(report.consistent)
        self.assertFalse(report.entry_allowed)
        self.assertTrue(report.exit_allowed)
        self.assertEqual(
            report.reason_codes,
            (PaperPositionStoreReasonCode.JOURNAL_GAP,),
        )

    def test_transition_timestamp_requires_utc_seconds(self) -> None:
        for timestamp in (
            "2026-08-09T10:00:00.123Z",
            "2026-08-09T10:00:00",
            "not-a-time",
        ):
            with self.subTest(timestamp=timestamp):
                with self.assertRaises(PaperPositionStoreError) as caught:
                    self._open(transition_timestamp_utc=timestamp)
                self.assertEqual(
                    caught.exception.reason_code,
                    PaperPositionStoreReasonCode.TRANSITION_INVALID,
                )

    def test_persisted_v2_state_contains_decimal_strings_not_floats(self) -> None:
        self._open()
        record = json.loads(self.store.state_path.read_text(encoding="utf-8"))

        self.assertEqual(record["quantity"], "1")
        self.assertEqual(record["modeled_entry_fill_price"], "100.02")
        self.assertFalse(any(isinstance(value, float) for value in record.values()))


if __name__ == "__main__":
    unittest.main()
