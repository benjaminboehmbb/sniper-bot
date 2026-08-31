#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import errno
import json
import shutil
import tempfile
import threading
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from live_l1.core.paper_economics import (
    PaperEconomicsConfig,
    authorize_entry,
    settle_trade,
)
from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    PaperEntryThrottlePolicy,
    PaperEntryThrottleState,
    apply_accepted_entry,
)
from live_l1.state.iu4_lifecycle_ledger import (
    IU4LifecycleLedgerV1,
    authority_generation_id,
    fingerprint as lifecycle_fingerprint,
)
from live_l1.state.loss_cluster import (
    LossClusterStateError,
    LossClusterStateV2,
    apply_loss_cluster_close,
    apply_loss_cluster_entry_veto,
)
from live_l1.state.paper_artifacts import (
    EntryEconomicsQuoteArtifactV1,
    PaperAccountState,
    PaperArtifactError,
    PaperRiskStateS4V2,
    PositionStateS2FlatV2,
    PositionStateS2V2,
    TradeRecordV2,
    apply_trade_to_account,
    canonical_json_sha256,
)
from live_l1.state.paper_atomic_coordinator import (
    AtomicCoordinatorReasonCode,
    AtomicEntryDenialProvenanceV1,
    AtomicEntryVetoCandidateV1,
    AtomicPaperStateV2,
    AtomicPaperTransactionV2,
    AtomicProgressCursorV1,
    AtomicV1ToV2MigrationArtifactV1,
    PaperAtomicCoordinator,
    PaperAtomicCoordinatorError,
    PaperAtomicCoordinatorV2,
    SimulatedAtomicTransactionInterruption,
)


D = Decimal


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_float(item) for item in value)
    return False


def make_config() -> PaperEconomicsConfig:
    return PaperEconomicsConfig(
        schema_version=1,
        economics_model_version="PEE_V1",
        economics_profile_id="I3-ECONOMICS",
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
        policy_profile_id="I3-THROTTLE",
        max_entries_per_utc_day=10,
        max_entries_per_rolling_window=3,
        rolling_window_seconds=3600,
        min_reentry_cooldown_seconds=60,
    )


class AtomicV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="iu4-i3-v2-"))
        self.config = make_config()
        self.policy = make_policy()
        self.runtime_control_profile_id = "IU4-CONTROL-I3"
        self.runtime_control_fingerprint = digest("runtime-control")
        self.loss_policy_id = "IU4-LOSS-I3"
        self.loss_policy_fingerprint = digest("loss-policy")
        self.authority_generation_id = "IU4-AUTHORITY-GENERATION-I3"
        self.authority_prepare_fingerprint = digest("authority-prepare")
        self.authority_manifest_id = "IU4-I3-SYNTHETIC-GENESIS"
        self.authority_manifest_fingerprint = digest("authority-manifest")
        self.initial_state = self._make_initial_state()
        self.coordinator = self._make_coordinator(self.temp / "atomic")
        self.coordinator.initialize(
            self.initial_state,
            committed_authority_target_state_fingerprint=(
                self.initial_state.state_fingerprint
            ),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def _make_coordinator(self, root: Path) -> PaperAtomicCoordinatorV2:
        return PaperAtomicCoordinatorV2(
            root,
            self.config,
            self.policy,
            coordinator_id="PAPER-ATOMIC-I3",
            symbol="BTCUSDT",
            runtime_control_profile_id=self.runtime_control_profile_id,
            runtime_control_fingerprint=self.runtime_control_fingerprint,
            loss_cluster_policy_id=self.loss_policy_id,
            loss_cluster_policy_fingerprint=self.loss_policy_fingerprint,
        )

    def _make_initial_state(
        self,
        *,
        authority_generation_id: str | None = None,
        authority_prepare_fingerprint: str | None = None,
    ) -> AtomicPaperStateV2:
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
            account_id="PAPER-I3",
            quote_currency="USDT",
            starting_equity_quote=self.config.starting_equity_quote,
            utc_day="2026-08-20",
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        throttle = PaperEntryThrottleState.initial(
            self.policy,
            utc_day="2026-08-20",
        )
        loss = LossClusterStateV2(
            schema_version=2,
            revision=0,
            recent_closed_trade_pnls=(),
            pause_entries_remaining=0,
            updated_utc="2026-08-20T00:00:00Z",
        )
        cursor = AtomicProgressCursorV1.initial()
        generation = authority_generation_id or self.authority_generation_id
        prepare = (
            authority_prepare_fingerprint
            or self.authority_prepare_fingerprint
        )
        risk = PaperRiskStateS4V2(
            schema_version=2,
            system_state_id=flat.system_state_id,
            kill_level="NONE",
            cooldown_until_utc="",
            trades_today=0,
            loss_today=D("0"),
            anomaly_counter=0,
            trades_6h=0,
            last_trade_timestamp_utc="",
            entry_allowed=True,
            exit_evaluation_allowed=True,
            runtime_directive="CONTINUE",
            reason_codes=(),
            position_fingerprint=flat.state_fingerprint,
            account_fingerprint=account.state_fingerprint,
            throttle_fingerprint=throttle.state_fingerprint,
            loss_cluster_fingerprint=loss.state_fingerprint,
            progress_cursor_fingerprint=cursor.cursor_fingerprint,
            runtime_control_profile_id=self.runtime_control_profile_id,
            runtime_control_fingerprint=self.runtime_control_fingerprint,
            loss_cluster_policy_id=self.loss_policy_id,
            loss_cluster_policy_fingerprint=self.loss_policy_fingerprint,
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
            throttle_policy_profile_id=self.policy.policy_profile_id,
            throttle_policy_model_version=self.policy.policy_model_version,
            throttle_policy_fingerprint=self.policy.policy_fingerprint,
            authority_generation_id=generation,
            transaction_sequence=0,
            journal_head="EMPTY",
            last_transaction_event_id="",
            last_transaction_timestamp_utc="",
            last_transaction_tick_id=0,
        )
        return AtomicPaperStateV2(
            schema_version=2,
            coordinator_id="PAPER-ATOMIC-I3",
            system_state_id=flat.system_state_id,
            transaction_sequence=0,
            journal_head="EMPTY",
            last_transaction_event_id="",
            position=flat,
            account=account,
            throttle=throttle,
            loss_cluster=loss,
            progress_cursor=cursor,
            risk=risk,
            entry_quote=None,
            runtime_control_profile_id=self.runtime_control_profile_id,
            runtime_control_fingerprint=self.runtime_control_fingerprint,
            loss_cluster_policy_id=self.loss_policy_id,
            loss_cluster_policy_fingerprint=self.loss_policy_fingerprint,
            state_owner_epoch="PEE",
            authority_generation_id=generation,
            authority_prepare_record_fingerprint=prepare,
            authority_manifest_id=self.authority_manifest_id,
            authority_manifest_fingerprint=self.authority_manifest_fingerprint,
        )

    def _quote_and_open(
        self,
        *,
        event_id: str = "OPEN-1",
        timestamp: str = "2026-08-20T10:00:00Z",
        tick_id: int = 100,
        coordinator: PaperAtomicCoordinatorV2 | None = None,
    ) -> tuple[
        EntryEconomicsQuoteArtifactV1,
        PositionStateS2V2,
        AcceptedEntryEventV1,
        AtomicProgressCursorV1,
    ]:
        current = (coordinator or self.coordinator).load_state()
        decision = authorize_entry(
            side="LONG",
            realized_equity_quote=current.account.realized_equity_quote,
            reference_entry_price=D("100"),
            reference_stop_price=D("95"),
            config=self.config,
        )
        self.assertTrue(decision.allowed)
        assert decision.quote is not None
        quote = EntryEconomicsQuoteArtifactV1.from_quote(decision.quote)
        position = PositionStateS2V2(
            schema_version=2,
            system_state_id="SYSTEM-1",
            symbol="BTCUSDT",
            position="LONG",
            side="LONG",
            trade_id="TRADE-1",
            reference_entry_price=decision.quote.reference_entry_price,
            modeled_entry_fill_price=decision.quote.modeled_entry_fill_price,
            quantity=decision.quote.quantity,
            entry_notional_quote=decision.quote.entry_notional_quote,
            entry_fee_quote=decision.quote.entry_fee_quote,
            risk_budget_quote=decision.quote.risk_budget_quote,
            modeled_stop_loss_quote=decision.quote.modeled_stop_loss_quote,
            reference_stop_price=decision.quote.reference_stop_price,
            entry_timestamp_utc=timestamp,
            entry_tick_id=tick_id,
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        event = AcceptedEntryEventV1(
            schema_version=1,
            entry_sequence=current.throttle.total_accepted_entry_count + 1,
            entry_event_id=event_id,
            previous_entry_event_id=current.throttle.last_entry_event_id,
            entry_timestamp_utc=timestamp,
            policy_model_version=self.policy.policy_model_version,
            policy_profile_id=self.policy.policy_profile_id,
            policy_fingerprint=self.policy.policy_fingerprint,
        )
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-OPEN-1",
            timestamp_utc=timestamp,
            tick_id=tick_id,
            intent_id="INTENT-OPEN-1",
        )
        return quote, position, event, cursor

    def _commit_open(self):
        quote, position, event, cursor = self._quote_and_open()
        result = self.coordinator.commit_open(
            position_after=position,
            entry_quote=quote,
            accepted_entry_event=event,
            progress_cursor=cursor,
        )
        return result, quote

    @staticmethod
    def _entry_veto_candidate(
        *,
        cursor: AtomicProgressCursorV1,
        event_id: str,
        loss_state: LossClusterStateV2,
        intent_action: str = "OPEN_LONG",
    ) -> AtomicEntryVetoCandidateV1:
        return AtomicEntryVetoCandidateV1(
            schema_version=1,
            candidate_id="",
            entry_veto_event_id=event_id,
            snapshot_id=cursor.snapshot_id,
            timestamp_utc=cursor.timestamp_utc,
            tick_id=cursor.tick_id,
            intent_id=cursor.intent_id,
            intent_action=intent_action,
            symbol="BTCUSDT",
            side="LONG" if intent_action == "OPEN_LONG" else "SHORT",
            loss_cluster_state_fingerprint=loss_state.state_fingerprint,
            denial_reason_code="PEE_LOSS_CLUSTER_ENTRY_VETO",
        )

    @staticmethod
    def _entry_denial_provenance(
        *,
        state: AtomicPaperStateV2,
        cursor: AtomicProgressCursorV1,
        event_id: str,
        origin: str = "RUNTIME_GATE_CAPABILITY",
        capability: bool = False,
        action: str = "OPEN_LONG",
    ) -> AtomicEntryDenialProvenanceV1:
        return AtomicEntryDenialProvenanceV1(
            schema_version=1,
            artifact_type="atomic_entry_denial_provenance_v1",
            transaction_event_id=event_id,
            snapshot_id=cursor.snapshot_id,
            timestamp_utc=cursor.timestamp_utc,
            tick_id=cursor.tick_id,
            intent_id=cursor.intent_id,
            intent_action=action,
            state_before_fingerprint=state.state_fingerprint,
            denial_origin=origin,
            denial_reason_code="PEE_IU4_ENTRY_BLOCKED",
            entry_capability_allowed=capability,
        )

    def _close_values(
        self,
        quote: EntryEconomicsQuoteArtifactV1,
        *,
        coordinator: PaperAtomicCoordinatorV2 | None = None,
    ) -> tuple[PositionStateS2FlatV2, TradeRecordV2, AtomicProgressCursorV1]:
        current = (coordinator or self.coordinator).load_state()
        self.assertIsInstance(current.position, PositionStateS2V2)
        settlement = settle_trade(
            entry_quote=quote.to_quote(),
            reference_exit_price=D("90"),
            equity_before_quote=current.account.realized_equity_quote,
            peak_realized_equity_before_quote=(
                current.account.peak_realized_equity_quote
            ),
            config=self.config,
        )
        trade = TradeRecordV2.from_economics(
            trade_id="TRADE-1",
            settlement_sequence=1,
            previous_settled_trade_id="",
            settlement_event_id="CLOSE-1",
            settlement_utc_day="2026-08-20",
            system_state_id="SYSTEM-2",
            symbol="BTCUSDT",
            quote_currency="USDT",
            entry_timestamp_utc=current.position.entry_timestamp_utc,
            exit_timestamp_utc="2026-08-20T11:00:00Z",
            entry_tick_id=current.position.entry_tick_id,
            exit_tick_id=200,
            exit_reason="TEST_CLOSE",
            entry_quote=quote.to_quote(),
            settlement=settlement,
        )
        flat = PositionStateS2FlatV2(
            schema_version=2,
            system_state_id="SYSTEM-2",
            symbol="BTCUSDT",
            position="FLAT",
            side="",
            last_closed_trade_id="TRADE-1",
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-CLOSE-1",
            timestamp_utc="2026-08-20T11:00:00Z",
            tick_id=200,
            intent_id="INTENT-CLOSE-1",
        )
        return flat, trade, cursor

    def _migration_artifact(
        self,
        *,
        migration_id: str,
        source_state,
        source_state_path: Path,
        source_loss_path: Path,
        target_state: AtomicPaperStateV2,
        target_path: Path,
        ledger: IU4LifecycleLedgerV1,
    ) -> AtomicV1ToV2MigrationArtifactV1:
        approval_fingerprint = digest(f"approval:{migration_id}")
        source_generation = f"SOURCE-GENERATION-{migration_id}"
        source_anchor = digest(f"source-anchor:{migration_id}")
        target_business = target_state.business_payload()
        generation = authority_generation_id(
            operation="ATOMIC_V1_TO_V2_MIGRATION",
            source_authority_generation_id=source_generation,
            source_authority_commit_anchor=source_anchor,
            manifest_fingerprint=self.authority_manifest_fingerprint,
            approval_fingerprint=approval_fingerprint,
            target_business_payload=target_business,
        )
        owner = ledger.view().owner_epoch
        return AtomicV1ToV2MigrationArtifactV1(
            schema_version=1,
            migration_id=migration_id,
            source_state_path=str(source_state_path),
            source_state_fingerprint=source_state.state_fingerprint,
            source_state_sha256=hashlib.sha256(source_state_path.read_bytes()).hexdigest(),
            source_loss_cluster_path=str(source_loss_path),
            source_loss_cluster_fingerprint=target_state.loss_cluster.state_fingerprint,
            source_loss_cluster_sha256=hashlib.sha256(source_loss_path.read_bytes()).hexdigest(),
            target_state_path=str(target_path),
            target_business_fingerprint=canonical_json_sha256(target_business),
            target_state_core_fingerprint=lifecycle_fingerprint(
                {
                    "target_business_payload": target_business,
                    "authority_generation_id": generation,
                }
            ),
            target_system_state_id=target_state.system_state_id,
            target_position_fingerprint=target_state.position.state_fingerprint,
            target_account_fingerprint=target_state.account.state_fingerprint,
            target_throttle_fingerprint=target_state.throttle.state_fingerprint,
            target_loss_cluster_fingerprint=target_state.loss_cluster.state_fingerprint,
            target_progress_cursor_fingerprint=target_state.progress_cursor.cursor_fingerprint,
            target_risk_business_fingerprint=canonical_json_sha256(
                target_state.risk.business_payload()
            ),
            target_state_owner_epoch=target_state.state_owner_epoch,
            runtime_control_profile_id=target_state.runtime_control_profile_id,
            runtime_control_fingerprint=target_state.runtime_control_fingerprint,
            loss_cluster_policy_id=target_state.loss_cluster_policy_id,
            loss_cluster_policy_fingerprint=target_state.loss_cluster_policy_fingerprint,
            economics_profile_id=target_state.account.economics_profile_id,
            economics_model_version=target_state.account.economics_model_version,
            config_fingerprint=target_state.account.config_fingerprint,
            throttle_policy_profile_id=target_state.throttle.policy_profile_id,
            throttle_policy_model_version=target_state.throttle.policy_model_version,
            throttle_policy_fingerprint=target_state.throttle.policy_fingerprint,
            previous_owner_epoch=owner,
            new_owner_epoch=owner + 1,
            manifest_id=self.authority_manifest_id,
            manifest_fingerprint=self.authority_manifest_fingerprint,
            approval_id=f"APPROVAL-{migration_id}",
            approval_fingerprint=approval_fingerprint,
            source_authority_generation_id=source_generation,
            source_authority_commit_anchor=source_anchor,
            operator="I3-TEST",
            migration_timestamp_utc="2026-08-20T12:00:00Z",
        )

    def _migration_fixture(self, suffix: str):
        source_root = self.temp / f"source-v1-{suffix}"
        source_coordinator = PaperAtomicCoordinator(
            source_root,
            self.config,
            self.policy,
            coordinator_id=f"SOURCE-V1-{suffix}",
            symbol="BTCUSDT",
        )
        source_state = source_coordinator.initialize(
            position=replace(
                self.initial_state.position,
                system_state_id=f"V1-SYSTEM-{suffix}",
            ),
            account=self.initial_state.account,
            throttle=self.initial_state.throttle,
        )
        source_state_path = source_root / "paper_atomic_state.json"
        source_loss_path = self.temp / f"source-loss-{suffix}.json"
        source_loss_path.write_text(
            json.dumps(
                self.initial_state.loss_cluster.to_record(),
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="ascii",
        )
        target = self._make_initial_state(
            authority_generation_id=f"PROVISIONAL-{suffix}",
            authority_prepare_fingerprint=digest(f"provisional:{suffix}"),
        )
        ledger = IU4LifecycleLedgerV1(self.temp / f"ledger-{suffix}")
        artifact = self._migration_artifact(
            migration_id=f"I3-MIGRATION-{suffix}",
            source_state=source_state,
            source_state_path=source_state_path,
            source_loss_path=source_loss_path,
            target_state=target,
            target_path=self.temp / f"target-{suffix}" / "paper_atomic_state_v2.json",
            ledger=ledger,
        )
        return (
            source_coordinator,
            source_state,
            source_state_path,
            source_loss_path,
            target,
            ledger,
            artifact,
        )

    def _consume_migration_completion(
        self,
        *,
        ledger: IU4LifecycleLedgerV1,
        artifact: AtomicV1ToV2MigrationArtifactV1,
        source_state,
        target: AtomicPaperStateV2,
        attempt_suffix: str = "",
    ) -> str:
        prepare = next(
            record
            for record in ledger.records()
            if record.lifecycle_event_id == f"{artifact.migration_id}:PREPARE"
        )
        generation = authority_generation_id(
            operation="ATOMIC_V1_TO_V2_MIGRATION",
            source_authority_generation_id=artifact.source_authority_generation_id,
            source_authority_commit_anchor=artifact.source_authority_commit_anchor,
            manifest_fingerprint=artifact.manifest_fingerprint,
            approval_fingerprint=artifact.approval_fingerprint,
            target_business_payload=target.business_payload(),
        )
        view = ledger.view()
        suffix = f"-{attempt_suffix}" if attempt_suffix else ""
        record = ledger.consume_restart_authorization(
            lifecycle_event_id=f"{artifact.migration_id}:COMPLETE-AUTH{suffix}",
            authorization_id=f"AUTH-{artifact.migration_id}{suffix}",
            authorization_fingerprint=digest(
                f"completion-auth:{artifact.migration_id}{suffix}"
            ),
            operation="COMPLETE_AUTHORITY_PREPARE",
            operator="I3-TEST",
            startup_attempt_id=f"ATTEMPT-{artifact.migration_id}{suffix}",
            pre_state_fingerprint=source_state.state_fingerprint,
            pre_journal_head="EMPTY",
            pre_attempt_ledger_tip=view.ledger_tip,
            source_authority_generation_id=(
                artifact.source_authority_generation_id
            ),
            source_authority_commit_anchor=artifact.source_authority_commit_anchor,
            consumption_timestamp_utc=(
                "2026-08-20T12:00:01Z"
                if not attempt_suffix
                else "2026-08-20T12:00:02Z"
            ),
            completion_prepare_event_id=prepare.lifecycle_event_id,
            completion_prepare_fingerprint=prepare.record_fingerprint,
            target_authority_generation_id=generation,
        )
        return record.record_fingerprint

    def test_entry_quote_roundtrip_is_exact_and_float_free(self) -> None:
        quote, _, _, _ = self._quote_and_open()
        record = quote.to_record()
        restored = EntryEconomicsQuoteArtifactV1.from_record(record)

        self.assertEqual(restored, quote)
        self.assertEqual(restored.to_quote(), quote.to_quote())
        self.assertFalse(contains_float(record))
        self.assertEqual(record["quote_fingerprint"], quote.quote_fingerprint)

    def test_entry_quote_rejects_unknown_tamper_and_float(self) -> None:
        quote, _, _, _ = self._quote_and_open()
        unknown = quote.to_record()
        unknown["unknown"] = True
        with self.assertRaises(PaperArtifactError):
            EntryEconomicsQuoteArtifactV1.from_record(unknown)

        tampered = quote.to_record()
        tampered["quantity"] = "999"
        with self.assertRaises(PaperArtifactError):
            EntryEconomicsQuoteArtifactV1.from_record(tampered)

        with self.assertRaises(PaperArtifactError):
            EntryEconomicsQuoteArtifactV1(
                **{
                    **{
                        name: getattr(quote, name)
                        for name in quote.__dataclass_fields__
                    },
                    "quantity": 1.0,
                }
            )

    def test_s4_v2_exact_capability_matrix(self) -> None:
        expected = {
            "NONE": (True, True, "CONTINUE"),
            "SOFT": (False, True, "CONTINUE"),
            "HARD": (False, False, "STOP_LOOP"),
            "EMERGENCY": (False, False, "EXIT_PROCESS"),
        }
        base = self.initial_state.risk
        for level, capabilities in expected.items():
            entry, exit_evaluation, directive = capabilities
            reasons = () if entry else (f"PEE_S4_KILL_{level}",)
            risk = replace(
                base,
                kill_level=level,
                entry_allowed=entry,
                exit_evaluation_allowed=exit_evaluation,
                runtime_directive=directive,
                reason_codes=reasons,
            )
            self.assertEqual(
                PaperRiskStateS4V2.from_record(risk.to_record()),
                risk,
            )

        with self.assertRaises(PaperArtifactError):
            replace(
                base,
                kill_level="HARD",
                entry_allowed=False,
                exit_evaluation_allowed=True,
                runtime_directive="CONTINUE",
                reason_codes=("BAD",),
            )

    def test_loss_cluster_transitions_are_pure_decimal_values(self) -> None:
        initial = self.initial_state.loss_cluster
        state = initial
        for index in range(5):
            state = apply_loss_cluster_close(
                state,
                net_pnl_quote=D("-1"),
                updated_utc=f"2026-08-20T00:00:0{index + 1}Z",
                policy_id=self.loss_policy_id,
                policy_fingerprint=self.loss_policy_fingerprint,
                lookback=10,
                loss_threshold=5,
                pause_entries=3,
            )
        self.assertEqual(initial.revision, 0)
        self.assertEqual(state.revision, 5)
        self.assertEqual(state.pause_entries_remaining, 3)
        self.assertEqual(state.recent_closed_trade_pnls, ())

        vetoed = apply_loss_cluster_entry_veto(
            state,
            updated_utc="2026-08-20T00:01:00Z",
            policy_id=self.loss_policy_id,
            policy_fingerprint=self.loss_policy_fingerprint,
        )
        self.assertEqual(vetoed.pause_entries_remaining, 2)
        self.assertEqual(vetoed.revision, 6)
        with self.assertRaises(LossClusterStateError):
            apply_loss_cluster_close(
                initial,
                net_pnl_quote=1.0,
                updated_utc="2026-08-20T00:00:01Z",
                policy_id=self.loss_policy_id,
                policy_fingerprint=self.loss_policy_fingerprint,
            )

    def test_atomic_state_roundtrip_binds_every_component_and_root(self) -> None:
        record = self.initial_state.to_record()
        restored = AtomicPaperStateV2.from_record(record)

        self.assertEqual(restored, self.initial_state)
        self.assertEqual(record["state_fingerprint"], restored.state_fingerprint)
        self.assertNotIn("ledger_tip", json.dumps(record))
        self.assertNotIn("authority_commit_anchor", json.dumps(record))
        self.assertFalse(contains_float(record))

        wrong_root = record.copy()
        wrong_root["authority_prepare_record_fingerprint"] = digest("wrong")
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicPaperStateV2.from_record(wrong_root)

    def test_open_requires_exact_entry_quote_and_commits_one_cursor(self) -> None:
        result, quote = self._commit_open()
        state = result.state

        self.assertTrue(result.newly_committed)
        self.assertEqual(state.transaction_sequence, 1)
        self.assertEqual(state.progress_cursor.tick_id, 100)
        self.assertEqual(state.entry_quote, quote)
        self.assertEqual(state.throttle.total_accepted_entry_count, 1)
        self.assertEqual(state.account, self.initial_state.account)
        self.assertEqual(state.loss_cluster, self.initial_state.loss_cluster)

        record = state.to_record()
        record["entry_quote"] = None
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicPaperStateV2.from_record(record)

    def test_close_is_one_atomic_decimal_transaction(self) -> None:
        _, quote = self._commit_open()
        flat, trade, cursor = self._close_values(quote)
        result = self.coordinator.commit_close(
            position_after=flat,
            trade=trade,
            progress_cursor=cursor,
            loss_updated_utc="2026-08-20T11:00:00Z",
        )

        state = result.state
        self.assertEqual(state.position.position, "FLAT")
        self.assertIsNone(state.entry_quote)
        self.assertEqual(state.account.closed_trade_count, 1)
        self.assertEqual(state.loss_cluster.revision, 1)
        self.assertEqual(
            state.loss_cluster.recent_closed_trade_pnls,
            (trade.net_pnl_quote,),
        )
        self.assertEqual(state.progress_cursor, cursor)

        duplicate = self.coordinator.commit_close(
            position_after=flat,
            trade=trade,
            progress_cursor=cursor,
            loss_updated_utc="2026-08-20T11:00:00Z",
        )
        self.assertTrue(duplicate.already_committed)
        self.assertEqual(duplicate.state.loss_cluster.revision, 1)

    def test_progress_changes_only_cursor_and_bound_risk(self) -> None:
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-PROGRESS-1",
            timestamp_utc="2026-08-20T09:00:00Z",
            tick_id=90,
            intent_id="INTENT-HOLD-1",
        )
        result = self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="PROGRESS-1",
        )
        before = self.initial_state
        after = result.state

        self.assertEqual(after.position, before.position)
        self.assertEqual(after.account, before.account)
        self.assertEqual(after.throttle, before.throttle)
        self.assertEqual(after.loss_cluster, before.loss_cluster)
        self.assertIsNone(after.entry_quote)
        self.assertEqual(after.progress_cursor, cursor)

        duplicate = self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="PROGRESS-1",
        )
        self.assertTrue(duplicate.already_committed)
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.commit_progress(
                progress_cursor=replace(cursor, intent_id="DIFFERENT"),
                transaction_event_id="PROGRESS-1",
            )

    def test_entry_veto_decrements_once_and_other_components_stay_equal(self) -> None:
        paused_loss = replace(
            self.initial_state.loss_cluster,
            pause_entries_remaining=2,
        )
        risk = replace(
            self.initial_state.risk,
            entry_allowed=False,
            reason_codes=("LOSS_CLUSTER_PAUSE",),
            loss_cluster_fingerprint=paused_loss.state_fingerprint,
        )
        paused = replace(
            self.initial_state,
            loss_cluster=paused_loss,
            risk=risk,
        )
        root = self.temp / "veto"
        coordinator = self._make_coordinator(root)
        coordinator.initialize(
            paused,
            committed_authority_target_state_fingerprint=paused.state_fingerprint,
        )
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-VETO-1",
            timestamp_utc="2026-08-20T09:30:00Z",
            tick_id=95,
            intent_id="INTENT-BUY-1",
        )
        candidate = self._entry_veto_candidate(
            cursor=cursor,
            event_id="ENTRY-VETO-1",
            loss_state=paused_loss,
        )
        result = coordinator.commit_entry_veto(
            progress_cursor=cursor,
            entry_candidate=candidate,
            transaction_event_id="ENTRY-VETO-1",
            loss_updated_utc=cursor.timestamp_utc,
        )

        self.assertEqual(result.state.loss_cluster.pause_entries_remaining, 1)
        self.assertEqual(result.state.position, paused.position)
        self.assertEqual(result.state.account, paused.account)
        self.assertEqual(result.state.throttle, paused.throttle)
        duplicate = coordinator.commit_entry_veto(
            progress_cursor=cursor,
            entry_candidate=candidate,
            transaction_event_id="ENTRY-VETO-1",
            loss_updated_utc=cursor.timestamp_utc,
        )
        self.assertTrue(duplicate.already_committed)
        self.assertEqual(duplicate.state.loss_cluster.pause_entries_remaining, 1)

    def test_entry_veto_candidate_is_strict_and_causally_bound(self) -> None:
        paused_loss = replace(
            self.initial_state.loss_cluster,
            pause_entries_remaining=2,
        )
        paused = replace(
            self.initial_state,
            loss_cluster=paused_loss,
            risk=replace(
                self.initial_state.risk,
                entry_allowed=False,
                reason_codes=("LOSS_CLUSTER_PAUSE",),
                loss_cluster_fingerprint=paused_loss.state_fingerprint,
            ),
        )
        coordinator = self._make_coordinator(self.temp / "veto-binding")
        coordinator.initialize(
            paused,
            committed_authority_target_state_fingerprint=paused.state_fingerprint,
        )
        cursor = AtomicProgressCursorV1(
            1,
            "VETO-CANDIDATE-SNAPSHOT",
            "2026-08-20T09:31:00Z",
            96,
            "VETO-CANDIDATE-OPEN-INTENT",
        )
        candidate = self._entry_veto_candidate(
            cursor=cursor,
            event_id="VETO-CANDIDATE-EVENT",
            loss_state=paused_loss,
        )
        self.assertEqual(
            AtomicEntryVetoCandidateV1.from_record(candidate.to_record()),
            candidate,
        )
        tampered = candidate.to_record()
        tampered["snapshot_id"] = "OTHER-SNAPSHOT"
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicEntryVetoCandidateV1.from_record(tampered)
        with self.assertRaises(PaperAtomicCoordinatorError):
            self._entry_veto_candidate(
                cursor=cursor,
                event_id="VETO-HOLD",
                loss_state=paused_loss,
                intent_action="HOLD",
            )
        different_cursor = replace(cursor, snapshot_id="OTHER-SNAPSHOT")
        different_candidate = self._entry_veto_candidate(
            cursor=different_cursor,
            event_id="VETO-CANDIDATE-EVENT",
            loss_state=paused_loss,
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            coordinator.commit_entry_veto(
                progress_cursor=cursor,
                entry_candidate=different_candidate,
                transaction_event_id="VETO-CANDIDATE-EVENT",
                loss_updated_utc=cursor.timestamp_utc,
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
        )
        self.assertEqual(coordinator._transactions(), [])

    def test_open_close_outer_event_and_causal_time_are_exact(self) -> None:
        quote, position, event, cursor = self._quote_and_open()
        current = self.coordinator.load_state()
        throttle_after = apply_accepted_entry(current.throttle, self.policy, event)
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator._build_transaction(
                current,
                event_id="OUTER-OPEN-DIFFERS",
                ordering_space="TICK",
                effect="OPEN",
                timestamp=cursor.timestamp_utc,
                tick_id=cursor.tick_id,
                position_after=position,
                account_after=current.account,
                throttle_after=throttle_after,
                loss_after=current.loss_cluster,
                cursor_after=cursor,
                quote_after=quote,
                accepted_entry_event=event,
                effect_position=position,
                effect_entry_quote=quote,
                effect_progress_cursor=cursor,
                effect_throttle_policy=self.policy,
            )
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.commit_open(
                position_after=position,
                entry_quote=quote,
                accepted_entry_event=replace(
                    event,
                    entry_timestamp_utc="2026-08-20T09:00:00Z",
                ),
                progress_cursor=cursor,
            )
        self.assertEqual(self.coordinator._transactions(), [])

        self.coordinator.commit_open(
            position_after=position,
            entry_quote=quote,
            accepted_entry_event=event,
            progress_cursor=cursor,
        )
        flat, trade, close_cursor = self._close_values(quote)
        current = self.coordinator.load_state()
        account_after = apply_trade_to_account(current.account, trade)
        loss_after = apply_loss_cluster_close(
            current.loss_cluster,
            net_pnl_quote=trade.net_pnl_quote,
            updated_utc=close_cursor.timestamp_utc,
            policy_id=self.loss_policy_id,
            policy_fingerprint=self.loss_policy_fingerprint,
            lookback=10,
            loss_threshold=5,
            pause_entries=3,
        )
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator._build_transaction(
                current,
                event_id="OUTER-CLOSE-DIFFERS",
                ordering_space="TICK",
                effect="CLOSE",
                timestamp=close_cursor.timestamp_utc,
                tick_id=close_cursor.tick_id,
                position_after=flat,
                account_after=account_after,
                throttle_after=current.throttle,
                loss_after=loss_after,
                cursor_after=close_cursor,
                quote_after=None,
                trade=trade,
                effect_progress_cursor=close_cursor,
                loss_transition_updated_utc=close_cursor.timestamp_utc,
                loss_transition_policy_id=self.loss_policy_id,
                loss_transition_policy_fingerprint=self.loss_policy_fingerprint,
                loss_transition_lookback=10,
                loss_transition_threshold=5,
                loss_transition_pause_entries=3,
            )
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.commit_close(
                position_after=flat,
                trade=replace(
                    trade,
                    exit_timestamp_utc="2026-08-20T10:59:00Z",
                ),
                progress_cursor=close_cursor,
                loss_updated_utc=close_cursor.timestamp_utc,
            )
        self.assertEqual(len(self.coordinator._transactions()), 1)

    def test_kill_is_control_order_without_cursor(self) -> None:
        cursor_before = self.initial_state.progress_cursor
        result = self.coordinator.commit_kill(
            transaction_event_id="KILL-1",
            target_kill_level="HARD",
            reason_code="PEE_S4_KILL_HARD",
            authorization_reference="AUTH-KILL-I3",
            transaction_timestamp_utc="2026-08-20T09:45:00Z",
            causal_tick_id=99,
        )

        self.assertEqual(result.state.progress_cursor, cursor_before)
        self.assertEqual(result.state.risk.kill_level, "HARD")
        self.assertFalse(result.state.risk.exit_evaluation_allowed)
        transaction = AtomicPaperTransactionV2.from_record(
            json.loads(result.journal_path.read_text(encoding="utf-8"))
        )
        self.assertEqual(transaction.ordering_space, "CONTROL")
        self.assertEqual(transaction.primary_effect, "KILL")

    def test_tick_risk_escalation_allows_only_none_to_soft(self) -> None:
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-SOFT-1",
            timestamp_utc="2026-08-20T09:50:00Z",
            tick_id=99,
            intent_id="INTENT-HOLD-SOFT",
        )
        result = self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="PROGRESS-SOFT-1",
            risk_escalation="NONE_TO_SOFT",
        )
        self.assertEqual(result.state.risk.kill_level, "SOFT")
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.commit_progress(
                progress_cursor=replace(
                    cursor,
                    snapshot_id="SNAPSHOT-DEESCALATE",
                    tick_id=100,
                ),
                transaction_event_id="PROGRESS-DEESCALATE",
                risk_escalation="SOFT_TO_NONE",
            )

    def test_durable_journal_recovers_without_redecision(self) -> None:
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-RECOVERY-1",
            timestamp_utc="2026-08-20T09:55:00Z",
            tick_id=99,
            intent_id="INTENT-HOLD-RECOVERY",
        )
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.commit_progress(
                progress_cursor=cursor,
                transaction_event_id="PROGRESS-RECOVERY-1",
                simulate_interruption_after_journal=True,
            )
        self.assertEqual(self.coordinator.load_state(), self.initial_state)

        recovered = self.coordinator.recover()
        self.assertEqual(recovered.recovered_transaction_count, 1)
        self.assertEqual(recovered.state.progress_cursor, cursor)
        self.assertEqual(self.coordinator.recover().recovered_transaction_count, 0)

    def test_corrupt_journal_and_snapshot_ahead_fail_closed(self) -> None:
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-CORRUPT-1",
            timestamp_utc="2026-08-20T09:56:00Z",
            tick_id=99,
            intent_id="INTENT-HOLD-CORRUPT",
        )
        result = self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="PROGRESS-CORRUPT-1",
        )
        result.journal_path.write_text("{}\n", encoding="ascii")
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.recover()

    def test_strict_cursor_state_and_transaction_schemas_reject_tamper(self) -> None:
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-STRICT-1",
            timestamp_utc="2026-08-20T09:57:00Z",
            tick_id=99,
            intent_id="INTENT-STRICT-1",
        )
        cursor_record = cursor.to_record()
        cursor_record["unknown"] = "x"
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicProgressCursorV1.from_record(cursor_record)

        state_record = self.initial_state.to_record()
        state_record["ledger_tip"] = digest("forbidden-ledger-tip")
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicPaperStateV2.from_record(state_record)

        result = self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="PROGRESS-STRICT-1",
        )
        transaction_record = json.loads(result.journal_path.read_text(encoding="ascii"))
        transaction_record["primary_effect"] = "OPEN"
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicPaperTransactionV2.from_record(transaction_record)

    def test_open_journal_interruption_recovers_exactly_once(self) -> None:
        quote, position, event, cursor = self._quote_and_open()
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.commit_open(
                position_after=position,
                entry_quote=quote,
                accepted_entry_event=event,
                progress_cursor=cursor,
                simulate_interruption_after_journal=True,
            )
        self.assertEqual(self.coordinator.load_state(), self.initial_state)
        recovered = self.coordinator.recover()
        self.assertEqual(recovered.recovered_transaction_count, 1)
        self.assertEqual(recovered.state.entry_quote, quote)
        self.assertEqual(self.coordinator.recover().recovered_transaction_count, 0)

    def test_close_journal_interruption_recovers_exactly_once(self) -> None:
        opened, quote = self._commit_open()
        flat, trade, cursor = self._close_values(quote)
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.commit_close(
                position_after=flat,
                trade=trade,
                progress_cursor=cursor,
                loss_updated_utc=cursor.timestamp_utc,
                simulate_interruption_after_journal=True,
            )
        self.assertEqual(self.coordinator.load_state(), opened.state)
        recovered = self.coordinator.recover()
        self.assertEqual(recovered.recovered_transaction_count, 1)
        self.assertEqual(recovered.state.account.closed_trade_count, 1)
        self.assertEqual(recovered.state.loss_cluster.revision, 1)

    def test_kill_journal_interruption_recovers_without_cursor(self) -> None:
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.commit_kill(
                transaction_event_id="KILL-RECOVERY-1",
                target_kill_level="EMERGENCY",
                reason_code="PEE_S4_KILL_EMERGENCY",
                authorization_reference="AUTH-KILL-RECOVERY",
                transaction_timestamp_utc="2026-08-20T09:58:00Z",
                causal_tick_id=99,
                simulate_interruption_after_journal=True,
            )
        recovered = self.coordinator.recover()
        self.assertEqual(recovered.state.risk.kill_level, "EMERGENCY")
        self.assertEqual(
            recovered.state.progress_cursor,
            self.initial_state.progress_cursor,
        )

    def test_entry_veto_journal_interruption_recovers_one_decrement(self) -> None:
        paused_loss = replace(
            self.initial_state.loss_cluster,
            pause_entries_remaining=1,
        )
        paused_risk = replace(
            self.initial_state.risk,
            entry_allowed=False,
            reason_codes=("LOSS_CLUSTER_PAUSE",),
            loss_cluster_fingerprint=paused_loss.state_fingerprint,
        )
        paused = replace(
            self.initial_state,
            loss_cluster=paused_loss,
            risk=paused_risk,
        )
        coordinator = self._make_coordinator(self.temp / "veto-recovery")
        coordinator.initialize(
            paused,
            committed_authority_target_state_fingerprint=paused.state_fingerprint,
        )
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-VETO-RECOVERY",
            timestamp_utc="2026-08-20T09:59:00Z",
            tick_id=99,
            intent_id="INTENT-VETO-RECOVERY",
        )
        candidate = self._entry_veto_candidate(
            cursor=cursor,
            event_id="ENTRY-VETO-RECOVERY",
            loss_state=paused_loss,
        )
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            coordinator.commit_entry_veto(
                progress_cursor=cursor,
                entry_candidate=candidate,
                transaction_event_id="ENTRY-VETO-RECOVERY",
                loss_updated_utc=cursor.timestamp_utc,
                simulate_interruption_after_journal=True,
            )
        recovered = coordinator.recover()
        self.assertEqual(recovered.state.loss_cluster.pause_entries_remaining, 0)
        self.assertEqual(recovered.state.loss_cluster.revision, 1)

    def test_terminal_kill_blocks_every_later_tick_transaction(self) -> None:
        self.coordinator.commit_kill(
            transaction_event_id="KILL-TERMINAL-1",
            target_kill_level="HARD",
            reason_code="PEE_S4_KILL_HARD",
            authorization_reference="AUTH-KILL-TERMINAL",
            transaction_timestamp_utc="2026-08-20T09:59:00Z",
            causal_tick_id=99,
        )
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAPSHOT-AFTER-HARD",
            timestamp_utc="2026-08-20T10:00:00Z",
            tick_id=100,
            intent_id="INTENT-AFTER-HARD",
        )
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.commit_progress(
                progress_cursor=cursor,
                transaction_event_id="PROGRESS-AFTER-HARD",
            )
        self.assertEqual(len(self.coordinator._transactions()), 1)

    def test_kill_duplicate_is_idempotent_and_conflict_is_rejected(self) -> None:
        first = self.coordinator.commit_kill(
            transaction_event_id="KILL-DUPLICATE-1",
            target_kill_level="SOFT",
            reason_code="PEE_S4_KILL_SOFT",
            authorization_reference="AUTH-KILL-DUPLICATE",
            transaction_timestamp_utc="2026-08-20T09:59:00Z",
            causal_tick_id=99,
        )
        duplicate = self.coordinator.commit_kill(
            transaction_event_id="KILL-DUPLICATE-1",
            target_kill_level="SOFT",
            reason_code="PEE_S4_KILL_SOFT",
            authorization_reference="AUTH-KILL-DUPLICATE",
            transaction_timestamp_utc="2026-08-20T09:59:00Z",
            causal_tick_id=99,
        )
        self.assertTrue(first.newly_committed)
        self.assertTrue(duplicate.already_committed)
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.commit_kill(
                transaction_event_id="KILL-DUPLICATE-1",
                target_kill_level="HARD",
                reason_code="PEE_S4_KILL_HARD",
                authorization_reference="AUTH-KILL-DUPLICATE",
                transaction_timestamp_utc="2026-08-20T09:59:00Z",
                causal_tick_id=99,
            )

    def test_entry_blocked_without_veto_writes_no_atomic_record(self) -> None:
        blocked_risk = replace(
            self.initial_state.risk,
            entry_allowed=False,
            reason_codes=("EXTERNAL_ENTRY_BLOCK",),
        )
        blocked = replace(self.initial_state, risk=blocked_risk)
        coordinator = self._make_coordinator(self.temp / "blocked-open")
        coordinator.initialize(
            blocked,
            committed_authority_target_state_fingerprint=blocked.state_fingerprint,
        )
        quote, position, event, cursor = self._quote_and_open(
            event_id="OPEN-BLOCKED",
        )
        with self.assertRaises(PaperAtomicCoordinatorError):
            coordinator.commit_open(
                position_after=position,
                entry_quote=quote,
                accepted_entry_event=event,
                progress_cursor=cursor,
            )
        self.assertEqual(coordinator._transactions(), [])

    def test_every_transaction_has_all_four_durable_fault_boundaries(self) -> None:
        fault_points = (
            "BEFORE_JOURNAL",
            "AFTER_JOURNAL",
            "BEFORE_SNAPSHOT",
            "AFTER_SNAPSHOT",
        )
        for effect in ("OPEN", "CLOSE", "ENTRY_VETO", "PROGRESS", "KILL"):
            for index, fault_point in enumerate(fault_points, start=1):
                with self.subTest(effect=effect, fault_point=fault_point):
                    root = self.temp / f"fault-{effect.lower()}-{index}"
                    coordinator = self._make_coordinator(root)
                    initial = self._make_initial_state()
                    if effect == "ENTRY_VETO":
                        loss = replace(initial.loss_cluster, pause_entries_remaining=2)
                        initial = replace(
                            initial,
                            loss_cluster=loss,
                            risk=replace(
                                initial.risk,
                                entry_allowed=False,
                                reason_codes=("LOSS_CLUSTER_PAUSE",),
                                loss_cluster_fingerprint=loss.state_fingerprint,
                            ),
                        )
                    coordinator.initialize(
                        initial,
                        committed_authority_target_state_fingerprint=(
                            initial.state_fingerprint
                        ),
                    )
                    self.coordinator = coordinator
                    baseline_sequence = 0
                    if effect == "OPEN":
                        quote, position, event, cursor = self._quote_and_open(
                            event_id=f"FAULT-OPEN-{index}"
                        )
                        operation = lambda: coordinator.commit_open(
                            position_after=position,
                            entry_quote=quote,
                            accepted_entry_event=event,
                            progress_cursor=cursor,
                            simulate_interruption_at=fault_point,
                        )
                    elif effect == "CLOSE":
                        _, quote = self._commit_open()
                        baseline_sequence = 1
                        flat, trade, cursor = self._close_values(quote)
                        operation = lambda: coordinator.commit_close(
                            position_after=flat,
                            trade=trade,
                            progress_cursor=cursor,
                            loss_updated_utc=cursor.timestamp_utc,
                            simulate_interruption_at=fault_point,
                        )
                    elif effect == "ENTRY_VETO":
                        cursor = AtomicProgressCursorV1(
                            schema_version=1,
                            snapshot_id=f"FAULT-VETO-SNAPSHOT-{index}",
                            timestamp_utc="2026-08-20T09:30:00Z",
                            tick_id=95,
                            intent_id=f"FAULT-VETO-INTENT-{index}",
                        )
                        operation = lambda: coordinator.commit_entry_veto(
                            progress_cursor=cursor,
                            entry_candidate=self._entry_veto_candidate(
                                cursor=cursor,
                                event_id=f"FAULT-VETO-{index}",
                                loss_state=coordinator.load_state().loss_cluster,
                            ),
                            transaction_event_id=f"FAULT-VETO-{index}",
                            loss_updated_utc=cursor.timestamp_utc,
                            simulate_interruption_at=fault_point,
                        )
                    elif effect == "PROGRESS":
                        cursor = AtomicProgressCursorV1(
                            schema_version=1,
                            snapshot_id=f"FAULT-PROGRESS-SNAPSHOT-{index}",
                            timestamp_utc="2026-08-20T09:00:00Z",
                            tick_id=90,
                            intent_id=f"FAULT-PROGRESS-INTENT-{index}",
                        )
                        operation = lambda: coordinator.commit_progress(
                            progress_cursor=cursor,
                            transaction_event_id=f"FAULT-PROGRESS-{index}",
                            simulate_interruption_at=fault_point,
                        )
                    else:
                        operation = lambda: coordinator.commit_kill(
                            transaction_event_id=f"FAULT-KILL-{index}",
                            target_kill_level="HARD",
                            reason_code="PEE_S4_KILL_HARD",
                            authorization_reference=f"FAULT-AUTH-{index}",
                            transaction_timestamp_utc="2026-08-20T09:45:00Z",
                            simulate_interruption_at=fault_point,
                        )
                    with self.assertRaises(SimulatedAtomicTransactionInterruption):
                        operation()
                    durable_count = len(coordinator._transactions())
                    if fault_point == "BEFORE_JOURNAL":
                        self.assertEqual(durable_count, baseline_sequence)
                        self.assertEqual(
                            coordinator.load_state().transaction_sequence,
                            baseline_sequence,
                        )
                    else:
                        self.assertEqual(durable_count, baseline_sequence + 1)
                        recovered = coordinator.recover()
                        self.assertEqual(
                            recovered.state.transaction_sequence,
                            baseline_sequence + 1,
                        )
                        expected_recovered = (
                            1
                            if fault_point in ("AFTER_JOURNAL", "BEFORE_SNAPSHOT")
                            else 0
                        )
                        self.assertEqual(
                            recovered.recovered_transaction_count,
                            expected_recovered,
                        )

    def test_resource_failures_are_classified_without_partial_state_claim(self) -> None:
        failures = (
            OSError(errno.ENOSPC, "disk full"),
            PermissionError(errno.EACCES, "permission denied"),
            OSError(errno.EMFILE, "file descriptor exhausted"),
            MemoryError("memory exhausted"),
        )
        for index, failure in enumerate(failures, start=1):
            with self.subTest(boundary="journal", failure=type(failure).__name__):
                root = self.temp / f"resource-journal-{index}"
                coordinator = self._make_coordinator(root)
                initial = self._make_initial_state()
                coordinator.initialize(
                    initial,
                    committed_authority_target_state_fingerprint=initial.state_fingerprint,
                )
                cursor = AtomicProgressCursorV1(
                    1,
                    f"RESOURCE-JOURNAL-SNAPSHOT-{index}",
                    "2026-08-20T09:00:00Z",
                    90,
                    f"RESOURCE-JOURNAL-INTENT-{index}",
                )
                with patch(
                    "live_l1.state.paper_atomic_coordinator._create_new_json",
                    side_effect=failure,
                ):
                    with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                        coordinator.commit_progress(
                            progress_cursor=cursor,
                            transaction_event_id=f"RESOURCE-JOURNAL-{index}",
                        )
                self.assertEqual(
                    caught.exception.reason_code,
                    AtomicCoordinatorReasonCode.RESOURCE_EXHAUSTED,
                )
                self.assertEqual(coordinator.load_state(), initial)
                self.assertEqual(coordinator._transactions(), [])

        root = self.temp / "resource-snapshot"
        coordinator = self._make_coordinator(root)
        initial = self._make_initial_state()
        coordinator.initialize(
            initial,
            committed_authority_target_state_fingerprint=initial.state_fingerprint,
        )
        cursor = AtomicProgressCursorV1(
            1,
            "RESOURCE-SNAPSHOT",
            "2026-08-20T09:00:00Z",
            90,
            "RESOURCE-INTENT",
        )
        with patch(
            "live_l1.state.paper_atomic_coordinator._atomic_write_json",
            side_effect=OSError(errno.ENOSPC, "disk full"),
        ):
            with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                coordinator.commit_progress(
                    progress_cursor=cursor,
                    transaction_event_id="RESOURCE-SNAPSHOT-EVENT",
                )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.RESOURCE_EXHAUSTED,
        )
        self.assertEqual(coordinator.load_state(), initial)
        self.assertEqual(len(coordinator._transactions()), 1)
        self.assertEqual(coordinator.recover().recovered_transaction_count, 1)

    def test_noncanonical_decimal_and_nested_float_records_are_rejected(self) -> None:
        quote, _, _, _ = self._quote_and_open()
        quote_record = quote.to_record()
        quote_record["reference_entry_price"] = "100.0"
        with self.assertRaises(PaperArtifactError):
            EntryEconomicsQuoteArtifactV1.from_record(quote_record)

        risk_record = self.initial_state.risk.to_record()
        risk_record["loss_today"] = "0.0"
        with self.assertRaises(PaperArtifactError):
            PaperRiskStateS4V2.from_record(risk_record)

        loss = replace(
            self.initial_state.loss_cluster,
            recent_closed_trade_pnls=(D("-1"),),
        )
        loss_record = loss.to_record()
        loss_record["recent_closed_trade_pnls"] = [-1.0]
        with self.assertRaises(LossClusterStateError):
            LossClusterStateV2.from_record(loss_record)

        aggregate_record = self.initial_state.to_record()
        aggregate_record["account"]["realized_equity_quote"] = 10000.0
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicPaperStateV2.from_record(aggregate_record)

    def test_snapshot_tick_identity_cannot_commit_under_another_event(self) -> None:
        first = AtomicProgressCursorV1(
            1,
            "REPLAY-SNAPSHOT",
            "2026-08-20T09:00:00Z",
            90,
            "REPLAY-INTENT-A",
        )
        self.coordinator.commit_progress(
            progress_cursor=first,
            transaction_event_id="REPLAY-EVENT-A",
        )
        divergent = replace(first, intent_id="REPLAY-INTENT-B")
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.commit_progress(
                progress_cursor=divergent,
                transaction_event_id="REPLAY-EVENT-B",
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
        )
        self.assertEqual(self.coordinator.load_state().transaction_sequence, 1)
        self.assertEqual(len(self.coordinator._transactions()), 1)

    def test_root_lock_prevents_two_sequence_one_commits(self) -> None:
        root = self.temp / "single-writer"
        first = self._make_coordinator(root)
        second = self._make_coordinator(root)
        initial = self._make_initial_state()
        first.initialize(
            initial,
            committed_authority_target_state_fingerprint=initial.state_fingerprint,
        )

        def transaction(coordinator, suffix: str, tick_id: int):
            cursor = AtomicProgressCursorV1(
                1,
                f"LOCK-SNAPSHOT-{suffix}",
                "2026-08-20T09:00:00Z",
                tick_id,
                f"LOCK-INTENT-{suffix}",
            )
            return coordinator._build_transaction(
                initial,
                event_id=f"LOCK-EVENT-{suffix}",
                ordering_space="TICK",
                effect="PROGRESS",
                timestamp=cursor.timestamp_utc,
                tick_id=cursor.tick_id,
                position_after=initial.position,
                account_after=initial.account,
                throttle_after=initial.throttle,
                loss_after=initial.loss_cluster,
                cursor_after=cursor,
                quote_after=None,
                effect_progress_cursor=cursor,
            )

        candidates = (transaction(first, "A", 90), transaction(second, "B", 91))
        outcomes: list[object] = []
        barrier = threading.Barrier(2)

        def commit(coordinator, candidate) -> None:
            barrier.wait()
            try:
                outcomes.append(
                    coordinator._commit(
                        candidate,
                        simulate_interruption_after_journal=False,
                    )
                )
            except PaperAtomicCoordinatorError as exc:
                outcomes.append(exc)

        threads = (
            threading.Thread(target=commit, args=(first, candidates[0])),
            threading.Thread(target=commit, args=(second, candidates[1])),
        )
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(
            sum(not isinstance(outcome, Exception) for outcome in outcomes),
            1,
        )
        self.assertEqual(len(first._transactions()), 1)
        self.assertEqual(first.load_state().transaction_sequence, 1)

    def test_open_effect_payload_rejects_unbound_throttle_after(self) -> None:
        quote, position, event, cursor = self._quote_and_open(
            event_id="AUTHORITATIVE-OPEN"
        )
        divergent_event = replace(
            event,
            entry_event_id="DIFFERENT-THROTTLE-EVENT",
        )
        divergent_throttle = apply_accepted_entry(
            self.initial_state.throttle,
            self.policy,
            divergent_event,
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator._build_transaction(
                self.initial_state,
                event_id=event.entry_event_id,
                ordering_space="TICK",
                effect="OPEN",
                timestamp=cursor.timestamp_utc,
                tick_id=cursor.tick_id,
                position_after=position,
                account_after=self.initial_state.account,
                throttle_after=divergent_throttle,
                loss_after=self.initial_state.loss_cluster,
                cursor_after=cursor,
                quote_after=quote,
                accepted_entry_event=event,
                effect_position=position,
                effect_entry_quote=quote,
                effect_progress_cursor=cursor,
                effect_throttle_policy=self.policy,
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
        )
        self.assertEqual(self.coordinator._transactions(), [])

    def test_close_effect_payload_rejects_unchanged_loss_state(self) -> None:
        _, quote = self._commit_open()
        before = self.coordinator.load_state()
        flat, trade, cursor = self._close_values(quote)
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator._build_transaction(
                before,
                event_id=trade.settlement_event_id,
                ordering_space="TICK",
                effect="CLOSE",
                timestamp=cursor.timestamp_utc,
                tick_id=cursor.tick_id,
                position_after=flat,
                account_after=apply_trade_to_account(before.account, trade),
                throttle_after=before.throttle,
                loss_after=before.loss_cluster,
                cursor_after=cursor,
                quote_after=None,
                trade=trade,
                effect_progress_cursor=cursor,
                loss_transition_updated_utc="2026-08-20T11:00:00Z",
                loss_transition_policy_id=self.loss_policy_id,
                loss_transition_policy_fingerprint=self.loss_policy_fingerprint,
                loss_transition_lookback=10,
                loss_transition_threshold=5,
                loss_transition_pause_entries=3,
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
        )
        self.assertEqual(self.coordinator.load_state(), before)
        self.assertEqual(len(self.coordinator._transactions()), 1)

    def test_public_close_rejects_wrong_last_closed_trade_identity(self) -> None:
        _, quote = self._commit_open()
        flat, trade, cursor = self._close_values(quote)
        wrong = replace(flat, last_closed_trade_id="NOT-THE-CLOSED-TRADE")
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.commit_close(
                position_after=wrong,
                trade=trade,
                progress_cursor=cursor,
                loss_updated_utc="2026-08-20T11:00:00Z",
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
        )
        self.assertEqual(self.coordinator.load_state().transaction_sequence, 1)
        self.assertEqual(len(self.coordinator._transactions()), 1)

    def test_open_recomputes_account_guard_and_rejects_stale_s4(self) -> None:
        account = replace(
            self.initial_state.account,
            realized_equity_quote=D("9600"),
            cumulative_net_pnl_quote=D("-400"),
            realized_drawdown_quote=D("400"),
            realized_drawdown_rate=D("0.04"),
            daily_net_pnl_quote=D("-400"),
        )
        stale = replace(
            self.initial_state,
            account=account,
            risk=replace(
                self.initial_state.risk,
                account_fingerprint=account.state_fingerprint,
                entry_allowed=True,
                reason_codes=(),
            ),
        )
        coordinator = self._make_coordinator(self.temp / "stale-guard")
        coordinator.initialize(
            stale,
            committed_authority_target_state_fingerprint=stale.state_fingerprint,
        )
        self.coordinator = coordinator
        quote, position, event, cursor = self._quote_and_open(
            event_id="STALE-GUARD-OPEN"
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            coordinator.commit_open(
                position_after=position,
                entry_quote=quote,
                accepted_entry_event=event,
                progress_cursor=cursor,
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
        )
        self.assertEqual(coordinator._transactions(), [])

    def test_refingerprinted_progress_cannot_change_s4_business_metrics(self) -> None:
        cursor = AtomicProgressCursorV1(
            1,
            "S4-TAMPER-SNAPSHOT",
            "2026-08-20T09:00:00Z",
            90,
            "S4-TAMPER-INTENT",
        )
        self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="S4-TAMPER-EVENT",
        )
        original = self.coordinator._transactions()[0][1]
        tampered_risk = replace(
            original.state_after.risk,
            trades_today=3,
            loss_today=D("9.5"),
            anomaly_counter=7,
        )
        new_head = AtomicPaperTransactionV2.journal_head_for(
            transaction_sequence=original.transaction_sequence,
            transaction_event_id=original.transaction_event_id,
            previous_journal_head=original.previous_journal_head,
            ordering_space=original.ordering_space,
            primary_effect=original.primary_effect,
            transaction_timestamp_utc=original.transaction_timestamp_utc,
            causal_tick_id=original.causal_tick_id,
            state_before=original.state_before,
            position_after=original.state_after.position,
            account_after=original.state_after.account,
            throttle_after=original.state_after.throttle,
            loss_cluster_after=original.state_after.loss_cluster,
            progress_cursor_after=original.state_after.progress_cursor,
            entry_quote_after=original.state_after.entry_quote,
            accepted_entry_event=None,
            trade=None,
            risk_escalation=original.risk_escalation,
            effect_position=original.effect_position,
            effect_entry_quote=original.effect_entry_quote,
            effect_progress_cursor=original.effect_progress_cursor,
            effect_throttle_policy=original.effect_throttle_policy,
            effect_entry_veto_candidate=(
                original.effect_entry_veto_candidate
            ),
            loss_transition_updated_utc=original.loss_transition_updated_utc,
            loss_transition_policy_id=original.loss_transition_policy_id,
            loss_transition_policy_fingerprint=(
                original.loss_transition_policy_fingerprint
            ),
            loss_transition_lookback=original.loss_transition_lookback,
            loss_transition_threshold=original.loss_transition_threshold,
            loss_transition_pause_entries=original.loss_transition_pause_entries,
            effect_target_kill_level=original.effect_target_kill_level,
            kill_level_after=tampered_risk.kill_level,
            risk_business_after_fingerprint=canonical_json_sha256(
                tampered_risk.business_payload()
            ),
            control_authorization_reference="",
        )
        tampered_after = replace(
            original.state_after,
            journal_head=new_head,
            risk=replace(tampered_risk, journal_head=new_head),
        )
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicPaperTransactionV2(
                schema_version=2,
                transaction_sequence=original.transaction_sequence,
                transaction_event_id=original.transaction_event_id,
                previous_journal_head=original.previous_journal_head,
                ordering_space=original.ordering_space,
                primary_effect=original.primary_effect,
                transaction_timestamp_utc=original.transaction_timestamp_utc,
                causal_tick_id=original.causal_tick_id,
                state_before=original.state_before,
                state_after=tampered_after,
                effect_progress_cursor=original.effect_progress_cursor,
            )

    def test_offline_v1_to_v2_migration_uses_prepare_target_commit(self) -> None:
        source_root = self.temp / "source-v1"
        from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator

        v1 = PaperAtomicCoordinator(
            source_root,
            self.config,
            self.policy,
            coordinator_id="SOURCE-V1",
            symbol="BTCUSDT",
        ).initialize(
            position=replace(self.initial_state.position, system_state_id="V1-SYSTEM"),
            account=self.initial_state.account,
            throttle=self.initial_state.throttle,
        )
        source_bytes = (source_root / "paper_atomic_state.json").read_bytes()
        source_loss_path = self.temp / "legacy-loss.json"
        source_loss_path.write_text(
            json.dumps(
                self.initial_state.loss_cluster.to_record(),
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="ascii",
        )
        source_loss_bytes = source_loss_path.read_bytes()
        migration_target = self._make_initial_state(
            authority_generation_id="PROVISIONAL",
            authority_prepare_fingerprint=digest("provisional-prepare"),
        )
        ledger = IU4LifecycleLedgerV1(self.temp / "ledger")
        artifact = self._migration_artifact(
            migration_id="I3-MIGRATION-1",
            source_state=v1,
            source_state_path=source_root / "paper_atomic_state.json",
            source_loss_path=source_loss_path,
            target_state=migration_target,
            target_path=self.temp / "migrated" / "paper_atomic_state_v2.json",
            ledger=ledger,
        )
        result = self.coordinator.migrate_v1_to_v2(
            source_state=v1,
            source_loss_cluster=self.initial_state.loss_cluster,
            target_state_template=migration_target,
            migration=artifact,
            lifecycle_ledger=ledger,
        )

        records = ledger.records()
        self.assertEqual(
            [record.record_type for record in records],
            [
                "ATOMIC_V1_TO_V2_MIGRATION_PREPARE",
                "ATOMIC_V1_TO_V2_MIGRATION_COMMIT",
            ],
        )
        self.assertEqual(
            Path(artifact.source_state_path).read_bytes(),
            source_bytes,
        )
        self.assertEqual(source_loss_path.read_bytes(), source_loss_bytes)
        self.assertEqual(result.target_state.state_owner_epoch, "PEE")
        self.assertEqual(
            result.target_state.authority_prepare_record_fingerprint,
            records[0].record_fingerprint,
        )
        self.assertEqual(ledger.view().authority_generation_id, result.target_state.authority_generation_id)

    def test_migration_interruption_leaves_one_open_prepare(self) -> None:
        source_root = self.temp / "source-v1-interrupt"
        from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator

        v1 = PaperAtomicCoordinator(
            source_root,
            self.config,
            self.policy,
            coordinator_id="SOURCE-V1-INTERRUPT",
            symbol="BTCUSDT",
        ).initialize(
            position=replace(self.initial_state.position, system_state_id="V1-SYSTEM-I"),
            account=self.initial_state.account,
            throttle=self.initial_state.throttle,
        )
        ledger = IU4LifecycleLedgerV1(self.temp / "ledger-interrupt")
        source_loss_path = self.temp / "legacy-loss-i.json"
        source_loss_path.write_text(
            json.dumps(
                self.initial_state.loss_cluster.to_record(),
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="ascii",
        )
        migration_target = self._make_initial_state(
            authority_generation_id="PROVISIONAL-I",
            authority_prepare_fingerprint=digest("provisional-i"),
        )
        artifact = self._migration_artifact(
            migration_id="I3-MIGRATION-INTERRUPT",
            source_state=v1,
            source_state_path=source_root / "paper_atomic_state.json",
            source_loss_path=source_loss_path,
            target_state=migration_target,
            target_path=self.temp / "migrated-i" / "paper_atomic_state_v2.json",
            ledger=ledger,
        )
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.migrate_v1_to_v2(
                source_state=v1,
                source_loss_cluster=self.initial_state.loss_cluster,
                target_state_template=migration_target,
                migration=artifact,
                lifecycle_ledger=ledger,
                simulate_interruption_after_prepare=True,
            )
        self.assertTrue(ledger.view().open_authority_prepare_event_id)
        self.assertFalse(Path(artifact.target_state_path).exists())

    def test_migration_artifact_is_strict_canonical_and_fingerprinted(self) -> None:
        *_, artifact = self._migration_fixture("ARTIFACT")
        record = artifact.to_record()
        self.assertEqual(
            AtomicV1ToV2MigrationArtifactV1.from_record(record),
            artifact,
        )
        unknown = dict(record)
        unknown["unknown"] = True
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicV1ToV2MigrationArtifactV1.from_record(unknown)
        tampered = dict(record)
        tampered["target_state_owner_epoch"] = "OTHER"
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicV1ToV2MigrationArtifactV1.from_record(tampered)

    def test_migration_complete_crash_grid_requires_explicit_reconciliation(self) -> None:
        cases = (
            ("BEFORE-PREPARE", "simulate_interruption_before_prepare", 0, False),
            ("AFTER-PREPARE", "simulate_interruption_after_prepare", 1, False),
            ("AFTER-TARGET", "simulate_interruption_after_target", 1, True),
            ("AFTER-COMMIT", "simulate_interruption_after_commit", 2, True),
        )
        for suffix, flag, records_after_fault, target_exists in cases:
            with self.subTest(point=suffix):
                (
                    _,
                    source_state,
                    _,
                    _,
                    target,
                    ledger,
                    artifact,
                ) = self._migration_fixture(suffix)
                arguments = {
                    "source_state": source_state,
                    "source_loss_cluster": self.initial_state.loss_cluster,
                    "target_state_template": target,
                    "migration": artifact,
                    "lifecycle_ledger": ledger,
                    flag: True,
                }
                with self.assertRaises(SimulatedAtomicTransactionInterruption):
                    self.coordinator.migrate_v1_to_v2(**arguments)
                self.assertEqual(len(ledger.records()), records_after_fault)
                self.assertEqual(Path(artifact.target_state_path).exists(), target_exists)
                if records_after_fault == 0:
                    continue
                with self.assertRaises(PaperAtomicCoordinatorError):
                    self.coordinator.migrate_v1_to_v2(
                        source_state=source_state,
                        source_loss_cluster=self.initial_state.loss_cluster,
                        target_state_template=target,
                        migration=artifact,
                        lifecycle_ledger=ledger,
                    )
                completion_fingerprint = "NONE"
                expected_final_records = 2
                if records_after_fault == 1:
                    prepare = ledger.records()[0]
                    generation = authority_generation_id(
                        operation="ATOMIC_V1_TO_V2_MIGRATION",
                        source_authority_generation_id=(
                            artifact.source_authority_generation_id
                        ),
                        source_authority_commit_anchor=(
                            artifact.source_authority_commit_anchor
                        ),
                        manifest_fingerprint=artifact.manifest_fingerprint,
                        approval_fingerprint=artifact.approval_fingerprint,
                        target_business_payload=target.business_payload(),
                    )
                    view = ledger.view()
                    completion = ledger.consume_restart_authorization(
                        lifecycle_event_id=f"{artifact.migration_id}:COMPLETE-AUTH",
                        authorization_id=f"AUTH-{artifact.migration_id}",
                        authorization_fingerprint=digest(
                            f"completion-auth:{artifact.migration_id}"
                        ),
                        operation="COMPLETE_AUTHORITY_PREPARE",
                        operator="I3-TEST",
                        startup_attempt_id=f"ATTEMPT-{artifact.migration_id}",
                        pre_state_fingerprint=source_state.state_fingerprint,
                        pre_journal_head="EMPTY",
                        pre_attempt_ledger_tip=view.ledger_tip,
                        source_authority_generation_id=(
                            artifact.source_authority_generation_id
                        ),
                        source_authority_commit_anchor=(
                            artifact.source_authority_commit_anchor
                        ),
                        consumption_timestamp_utc="2026-08-20T12:00:01Z",
                        completion_prepare_event_id=prepare.lifecycle_event_id,
                        completion_prepare_fingerprint=prepare.record_fingerprint,
                        target_authority_generation_id=generation,
                    )
                    completion_fingerprint = completion.record_fingerprint
                    expected_final_records = 4
                result = self.coordinator.migrate_v1_to_v2(
                    source_state=source_state,
                    source_loss_cluster=self.initial_state.loss_cluster,
                    target_state_template=target,
                    migration=artifact,
                    lifecycle_ledger=ledger,
                    reconcile_incomplete_migration=True,
                    completion_authorization_record_fingerprint=(
                        completion_fingerprint
                    ),
                )
                self.assertEqual(len(ledger.records()), expected_final_records)
                self.assertEqual(
                    AtomicPaperStateV2.from_record(
                        json.loads(Path(artifact.target_state_path).read_text("ascii"))
                    ),
                    result.target_state,
                )

    def test_recovered_migration_commit_is_exact_and_idempotent(self) -> None:
        (
            _,
            source_state,
            _,
            _,
            target,
            ledger,
            artifact,
        ) = self._migration_fixture("RECOVERED-READBACK")
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.migrate_v1_to_v2(
                source_state=source_state,
                source_loss_cluster=self.initial_state.loss_cluster,
                target_state_template=target,
                migration=artifact,
                lifecycle_ledger=ledger,
                simulate_interruption_after_prepare=True,
            )
        completion_fingerprint = self._consume_migration_completion(
            ledger=ledger,
            artifact=artifact,
            source_state=source_state,
            target=target,
        )
        arguments = {
            "source_state": source_state,
            "source_loss_cluster": self.initial_state.loss_cluster,
            "target_state_template": target,
            "migration": artifact,
            "lifecycle_ledger": ledger,
            "reconcile_incomplete_migration": True,
            "completion_authorization_record_fingerprint": (
                completion_fingerprint
            ),
        }
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.migrate_v1_to_v2(
                **arguments,
                simulate_interruption_after_commit=True,
            )
        records = ledger.records()
        self.assertEqual(len(records), 4)
        commit = records[-1]
        consumption = records[1]
        self.assertEqual(
            commit.payload["completion_provenance"],
            "RECOVERED_AFTER_PREPARE",
        )
        self.assertEqual(
            commit.payload["completion_authorization_id"],
            consumption.payload["authorization_id"],
        )
        self.assertEqual(
            commit.payload["completion_authorization_fingerprint"],
            consumption.payload["authorization_fingerprint"],
        )
        self.assertEqual(
            commit.payload["completion_consumption_event_id"],
            consumption.lifecycle_event_id,
        )
        self.assertEqual(
            commit.payload["completion_startup_attempt_id"],
            consumption.payload["startup_attempt_id"],
        )
        self.assertEqual(
            commit.payload["completion_pre_attempt_ledger_tip"],
            consumption.payload["pre_attempt_ledger_tip"],
        )
        second = self.coordinator.migrate_v1_to_v2(**arguments)
        third = self.coordinator.migrate_v1_to_v2(**arguments)
        self.assertEqual(third, second)
        self.assertEqual(second.commit_record_fingerprint, commit.record_fingerprint)
        self.assertEqual(len(ledger.records()), 4)

    def test_completion_crashes_require_fresh_authorization(self) -> None:
        for suffix, fault, target_exists in (
            (
                "AFTER-CLAIM",
                "simulate_interruption_after_completion_claim",
                False,
            ),
            ("AFTER-COMPLETION-TARGET", "simulate_interruption_after_target", True),
            ("BEFORE-COMPLETION-COMMIT", "simulate_interruption_before_commit", True),
        ):
            with self.subTest(point=suffix):
                (
                    _,
                    source_state,
                    _,
                    _,
                    target,
                    ledger,
                    artifact,
                ) = self._migration_fixture(suffix)
                with self.assertRaises(SimulatedAtomicTransactionInterruption):
                    self.coordinator.migrate_v1_to_v2(
                        source_state=source_state,
                        source_loss_cluster=self.initial_state.loss_cluster,
                        target_state_template=target,
                        migration=artifact,
                        lifecycle_ledger=ledger,
                        simulate_interruption_after_prepare=True,
                    )
                stale_fingerprint = self._consume_migration_completion(
                    ledger=ledger,
                    artifact=artifact,
                    source_state=source_state,
                    target=target,
                )
                arguments = {
                    "source_state": source_state,
                    "source_loss_cluster": self.initial_state.loss_cluster,
                    "target_state_template": target,
                    "migration": artifact,
                    "lifecycle_ledger": ledger,
                    "reconcile_incomplete_migration": True,
                    "completion_authorization_record_fingerprint": stale_fingerprint,
                }
                with self.assertRaises(SimulatedAtomicTransactionInterruption):
                    self.coordinator.migrate_v1_to_v2(
                        **arguments,
                        **{fault: True},
                    )
                self.assertEqual(len(ledger.records()), 3)
                self.assertEqual(
                    Path(artifact.target_state_path).exists(),
                    target_exists,
                )
                with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                    self.coordinator.migrate_v1_to_v2(**arguments)
                self.assertEqual(
                    caught.exception.reason_code,
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                )
                fresh_fingerprint = self._consume_migration_completion(
                    ledger=ledger,
                    artifact=artifact,
                    source_state=source_state,
                    target=target,
                    attempt_suffix="FRESH",
                )
                result = self.coordinator.migrate_v1_to_v2(
                    **{
                        **arguments,
                        "completion_authorization_record_fingerprint": (
                            fresh_fingerprint
                        ),
                    }
                )
                self.assertEqual(len(ledger.records()), 6)
                self.assertEqual(
                    ledger.records()[-1].payload["completion_provenance"],
                    "RECOVERED_AFTER_PREPARE",
                )
                self.assertEqual(
                    result.target_state.authority_generation_id,
                    ledger.view().authority_generation_id,
                )

    def test_completion_consumption_before_prepare_is_rejected_without_prepare(self) -> None:
        (
            _,
            source_state,
            _,
            _,
            target,
            ledger,
            artifact,
        ) = self._migration_fixture("CONSUME-BEFORE-PREPARE")
        generation = authority_generation_id(
            operation="ATOMIC_V1_TO_V2_MIGRATION",
            source_authority_generation_id=artifact.source_authority_generation_id,
            source_authority_commit_anchor=artifact.source_authority_commit_anchor,
            manifest_fingerprint=artifact.manifest_fingerprint,
            approval_fingerprint=artifact.approval_fingerprint,
            target_business_payload=target.business_payload(),
        )
        pre_tip = ledger.view().ledger_tip
        completion = ledger.consume_restart_authorization(
            lifecycle_event_id=f"{artifact.migration_id}:EARLY-COMPLETE",
            authorization_id="AUTH-EARLY-COMPLETION",
            authorization_fingerprint=digest("early-completion"),
            operation="COMPLETE_AUTHORITY_PREPARE",
            operator="I3-TEST",
            startup_attempt_id="ATTEMPT-EARLY-COMPLETION",
            pre_state_fingerprint=source_state.state_fingerprint,
            pre_journal_head="EMPTY",
            pre_attempt_ledger_tip=pre_tip,
            source_authority_generation_id=(
                artifact.source_authority_generation_id
            ),
            source_authority_commit_anchor=(
                artifact.source_authority_commit_anchor
            ),
            consumption_timestamp_utc="2026-08-20T12:00:01Z",
            completion_prepare_event_id=f"{artifact.migration_id}:PREPARE",
            completion_prepare_fingerprint=digest("prepare-does-not-exist"),
            target_authority_generation_id=generation,
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.migrate_v1_to_v2(
                source_state=source_state,
                source_loss_cluster=self.initial_state.loss_cluster,
                target_state_template=target,
                migration=artifact,
                lifecycle_ledger=ledger,
                reconcile_incomplete_migration=True,
                completion_authorization_record_fingerprint=(
                    completion.record_fingerprint
                ),
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
        )
        self.assertEqual(len(ledger.records()), 1)
        self.assertFalse(
            any(
                record.record_type == "ATOMIC_V1_TO_V2_MIGRATION_PREPARE"
                for record in ledger.records()
            )
        )

    def test_recovered_commit_without_materialization_claim_is_rejected(self) -> None:
        (
            _,
            source_state,
            _,
            _,
            target,
            ledger,
            artifact,
        ) = self._migration_fixture("CLAIMLESS-COMMIT")
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.migrate_v1_to_v2(
                source_state=source_state,
                source_loss_cluster=self.initial_state.loss_cluster,
                target_state_template=target,
                migration=artifact,
                lifecycle_ledger=ledger,
                simulate_interruption_after_prepare=True,
            )
        completion_fingerprint = self._consume_migration_completion(
            ledger=ledger,
            artifact=artifact,
            source_state=source_state,
            target=target,
        )
        prepare, completion = ledger.records()
        generation = authority_generation_id(
            operation="ATOMIC_V1_TO_V2_MIGRATION",
            source_authority_generation_id=artifact.source_authority_generation_id,
            source_authority_commit_anchor=artifact.source_authority_commit_anchor,
            manifest_fingerprint=artifact.manifest_fingerprint,
            approval_fingerprint=artifact.approval_fingerprint,
            target_business_payload=target.business_payload(),
        )
        ledger.append(
            record_type="ATOMIC_V1_TO_V2_MIGRATION_COMMIT",
            lifecycle_event_id=f"{artifact.migration_id}:COMMIT",
            payload={
                "prepare_record_fingerprint": prepare.record_fingerprint,
                "authority_generation_id": generation,
                "new_owner_epoch": artifact.new_owner_epoch,
                "completion_provenance": "RECOVERED_AFTER_PREPARE",
                "completion_authorization_record_fingerprint": (
                    completion.record_fingerprint
                ),
                "completion_materialization_event_id": "MISSING-CLAIM",
                "completion_materialization_record_fingerprint": digest(
                    "missing-claim"
                ),
            },
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.migrate_v1_to_v2(
                source_state=source_state,
                source_loss_cluster=self.initial_state.loss_cluster,
                target_state_template=target,
                migration=artifact,
                lifecycle_ledger=ledger,
                reconcile_incomplete_migration=True,
                completion_authorization_record_fingerprint=(
                    completion_fingerprint
                ),
            )
        self.assertEqual(
            caught.exception.reason_code,
            AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
        )

    def test_migration_rejects_missing_corrupt_and_wrong_bound_sources(self) -> None:
        for suffix, mutation in (
            ("MISSING-LOSS", "missing"),
            ("CORRUPT-LOSS", "corrupt"),
            ("SOURCE-CHECKSUM", "source-checksum"),
            ("WRONG-AUTHORITY", "authority"),
            ("WRONG-TARGET", "binding"),
        ):
            with self.subTest(mutation=mutation):
                (
                    _,
                    source_state,
                    _,
                    source_loss_path,
                    target,
                    ledger,
                    artifact,
                ) = self._migration_fixture(suffix)
                if mutation == "missing":
                    source_loss_path.unlink()
                elif mutation == "corrupt":
                    source_loss_path.write_text("{}\n", encoding="ascii")
                elif mutation == "source-checksum":
                    artifact = replace(
                        artifact,
                        source_state_sha256=digest("wrong-source-checksum"),
                    )
                elif mutation == "authority":
                    artifact = replace(
                        artifact,
                        manifest_fingerprint=digest("wrong-authority-manifest"),
                    )
                else:
                    artifact = replace(
                        artifact,
                        target_account_fingerprint=digest("wrong-target-account"),
                    )
                with self.assertRaises(PaperAtomicCoordinatorError):
                    self.coordinator.migrate_v1_to_v2(
                        source_state=source_state,
                        source_loss_cluster=self.initial_state.loss_cluster,
                        target_state_template=target,
                        migration=artifact,
                        lifecycle_ledger=ledger,
                    )
                self.assertEqual(ledger.records(), ())

    def test_migration_rejects_open_v1_source(self) -> None:
        (
            source_coordinator,
            _,
            source_state_path,
            source_loss_path,
            target,
            ledger,
            _,
        ) = self._migration_fixture("OPEN-SOURCE")
        current = source_coordinator.load_state()
        decision = authorize_entry(
            side="LONG",
            realized_equity_quote=current.account.realized_equity_quote,
            reference_entry_price=D("100"),
            reference_stop_price=D("95"),
            config=self.config,
        )
        assert decision.quote is not None
        quote = decision.quote
        position = PositionStateS2V2(
            schema_version=2,
            system_state_id="V1-OPEN-SYSTEM",
            symbol="BTCUSDT",
            position="LONG",
            side="LONG",
            trade_id="V1-OPEN-TRADE",
            reference_entry_price=quote.reference_entry_price,
            modeled_entry_fill_price=quote.modeled_entry_fill_price,
            quantity=quote.quantity,
            entry_notional_quote=quote.entry_notional_quote,
            entry_fee_quote=quote.entry_fee_quote,
            risk_budget_quote=quote.risk_budget_quote,
            modeled_stop_loss_quote=quote.modeled_stop_loss_quote,
            reference_stop_price=quote.reference_stop_price,
            entry_timestamp_utc="2026-08-20T10:00:00Z",
            entry_tick_id=100,
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
        )
        event = AcceptedEntryEventV1(
            schema_version=1,
            entry_sequence=1,
            entry_event_id="V1-OPEN-EVENT",
            previous_entry_event_id="",
            entry_timestamp_utc="2026-08-20T10:00:00Z",
            policy_model_version=self.policy.policy_model_version,
            policy_profile_id=self.policy.policy_profile_id,
            policy_fingerprint=self.policy.policy_fingerprint,
        )
        open_state = source_coordinator.commit_open(
            position_after=position,
            accepted_entry_event=event,
            transition_tick_id=100,
        ).state
        artifact = self._migration_artifact(
            migration_id="I3-MIGRATION-OPEN-SOURCE",
            source_state=open_state,
            source_state_path=source_state_path,
            source_loss_path=source_loss_path,
            target_state=target,
            target_path=self.temp / "target-open-source" / "paper_atomic_state_v2.json",
            ledger=ledger,
        )
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.migrate_v1_to_v2(
                source_state=open_state,
                source_loss_cluster=self.initial_state.loss_cluster,
                target_state_template=target,
                migration=artifact,
                lifecycle_ledger=ledger,
            )
        self.assertEqual(ledger.records(), ())

    def test_migration_reconciliation_rejects_tampered_published_target(self) -> None:
        (
            _,
            source_state,
            _,
            _,
            target,
            ledger,
            artifact,
        ) = self._migration_fixture("TAMPERED-TARGET")
        with self.assertRaises(SimulatedAtomicTransactionInterruption):
            self.coordinator.migrate_v1_to_v2(
                source_state=source_state,
                source_loss_cluster=self.initial_state.loss_cluster,
                target_state_template=target,
                migration=artifact,
                lifecycle_ledger=ledger,
                simulate_interruption_after_target=True,
            )
        target_path = Path(artifact.target_state_path)
        target_path.write_text("{}\n", encoding="ascii")
        completion_fingerprint = self._consume_migration_completion(
            ledger=ledger,
            artifact=artifact,
            source_state=source_state,
            target=target,
        )
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.migrate_v1_to_v2(
                source_state=source_state,
                source_loss_cluster=self.initial_state.loss_cluster,
                target_state_template=target,
                migration=artifact,
                lifecycle_ledger=ledger,
                reconcile_incomplete_migration=True,
                completion_authorization_record_fingerprint=completion_fingerprint,
            )
        self.assertEqual(len(ledger.records()), 3)

    def test_entry_denial_provenance_schema_canonicality_and_tamper_matrix(self) -> None:
        class TextSubclass(str):
            pass

        class IntegerSubclass(int):
            pass

        state = self.coordinator.load_state()
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAP-DENIAL-SCHEMA",
            timestamp_utc="2026-08-20T12:00:00Z",
            tick_id=300,
            intent_id="INTENT-DENIAL-SCHEMA",
        )
        provenance = self._entry_denial_provenance(
            state=state,
            cursor=cursor,
            event_id="DENIAL-SCHEMA",
        )
        record = provenance.to_record()
        self.assertEqual(13, len(record))
        self.assertEqual(
            provenance,
            AtomicEntryDenialProvenanceV1.from_record(record),
        )
        invalid_records = []
        for field, value in (
            ("schema_version", True),
            ("schema_version", IntegerSubclass(1)),
            ("schema_version", 2),
            ("artifact_type", "ATOMIC_ENTRY_DENIAL_PROVENANCE_V1"),
            ("artifact_type", TextSubclass("atomic_entry_denial_provenance_v1")),
            ("transaction_event_id", ""),
            ("transaction_event_id", " DENIAL-SCHEMA"),
            ("transaction_event_id", TextSubclass("DENIAL-SCHEMA")),
            ("snapshot_id", ""),
            ("snapshot_id", "SNAP-DENIAL-SCHEMA "),
            ("snapshot_id", TextSubclass("SNAP-DENIAL-SCHEMA")),
            ("timestamp_utc", "2026-08-20T12:00:00+00:00"),
            ("timestamp_utc", "2026-08-20T12:00:00.1Z"),
            ("timestamp_utc", "2026-08-20T12:00:00"),
            ("timestamp_utc", "not-a-timestamp"),
            ("timestamp_utc", TextSubclass("2026-08-20T12:00:00Z")),
            ("tick_id", True),
            ("tick_id", 300.0),
            ("tick_id", IntegerSubclass(300)),
            ("tick_id", -1),
            ("intent_id", ""),
            ("intent_id", "INTENT-DENIAL-SCHEMA "),
            ("intent_id", TextSubclass("INTENT-DENIAL-SCHEMA")),
            ("intent_action", "open_long"),
            ("intent_action", "OPEN_LONG "),
            ("intent_action", "CLOSE_LONG"),
            ("intent_action", TextSubclass("OPEN_LONG")),
            ("state_before_fingerprint", state.state_fingerprint.upper()),
            ("state_before_fingerprint", "g" * 64),
            ("state_before_fingerprint", "a" * 63),
            (
                "state_before_fingerprint",
                TextSubclass(state.state_fingerprint),
            ),
            ("denial_origin", "runtime_gate_capability"),
            ("denial_origin", "RUNTIME_GATE_CAPABILITY "),
            ("denial_origin", "UNKNOWN_ORIGIN"),
            (
                "denial_origin",
                TextSubclass("RUNTIME_GATE_CAPABILITY"),
            ),
            ("denial_reason_code", "PEE_ATOMIC_ENTRY_BLOCKED"),
            ("denial_reason_code", "PEE_IU4_ENTRY_BLOCKED "),
            (
                "denial_reason_code",
                TextSubclass("PEE_IU4_ENTRY_BLOCKED"),
            ),
            ("entry_capability_allowed", 1),
            ("entry_capability_allowed", "false"),
            ("entry_capability_allowed", SimpleNamespace(value=False)),
        ):
            changed = dict(record)
            changed[field] = value
            invalid_records.append((field, value, changed))
        missing = dict(record)
        missing.pop("intent_id")
        invalid_records.append(("missing", None, missing))
        unknown = dict(record)
        unknown["unknown"] = "x"
        invalid_records.append(("unknown", None, unknown))
        tampered = dict(record)
        tampered["provenance_fingerprint"] = digest("tampered-provenance")
        invalid_records.append(("fingerprint", None, tampered))
        for field, value, changed in invalid_records:
            with self.subTest(field=field, value=value):
                with self.assertRaises(PaperAtomicCoordinatorError):
                    AtomicEntryDenialProvenanceV1.from_record(changed)

    def test_entry_denial_provenance_transaction_replay_and_conflict(self) -> None:
        before = self.coordinator.load_state()
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAP-DENIAL-REPLAY",
            timestamp_utc="2026-08-20T12:01:00Z",
            tick_id=301,
            intent_id="INTENT-DENIAL-REPLAY",
        )
        provenance = self._entry_denial_provenance(
            state=before,
            cursor=cursor,
            event_id="DENIAL-REPLAY",
        )
        first = self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="DENIAL-REPLAY",
            effect_entry_denial_provenance=provenance,
        )
        transaction = self.coordinator._existing("DENIAL-REPLAY")
        assert transaction is not None
        self.assertEqual(provenance, transaction.effect_entry_denial_provenance)
        self.assertEqual(provenance, AtomicPaperTransactionV2.from_record(
            transaction.to_record()
        ).effect_entry_denial_provenance)
        self.assertIn("effect_entry_denial_provenance", transaction.to_record())
        self.assertEqual(before.position, first.state.position)
        self.assertEqual(before.account, first.state.account)
        self.assertEqual(before.throttle, first.state.throttle)
        self.assertEqual(before.loss_cluster, first.state.loss_cluster)
        self.assertEqual(before.risk.entry_allowed, first.state.risk.entry_allowed)
        self.assertEqual(before.risk.reason_codes, first.state.risk.reason_codes)
        replay = self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="DENIAL-REPLAY",
            effect_entry_denial_provenance=provenance,
        )
        self.assertTrue(replay.already_committed)
        divergent = replace(
            provenance,
            denial_origin="ECONOMICS_AUTHORIZATION",
            entry_capability_allowed=True,
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            self.coordinator.commit_progress(
                progress_cursor=cursor,
                transaction_event_id="DENIAL-REPLAY",
                effect_entry_denial_provenance=divergent,
            )
        self.assertEqual(
            AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
            caught.exception.reason_code,
        )
        self.assertEqual(1, len(self.coordinator._transactions()))

    def test_refingerprinted_provenance_transaction_and_journal_tamper_rejects(self) -> None:
        before = self.coordinator.load_state()
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAP-DENIAL-REFINGERPRINTED-TAMPER",
            timestamp_utc="2026-08-20T12:01:30Z",
            tick_id=301,
            intent_id="INTENT-DENIAL-REFINGERPRINTED-TAMPER",
        )
        event_id = "DENIAL-REFINGERPRINTED-TAMPER"
        provenance = self._entry_denial_provenance(
            state=before,
            cursor=cursor,
            event_id=event_id,
        )
        self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id=event_id,
            effect_entry_denial_provenance=provenance,
        )
        path, original = self.coordinator._transactions()[0]
        tampered_provenance = replace(
            provenance,
            denial_origin="STATE_CAPABILITY",
        )
        self.assertNotEqual(
            provenance.provenance_fingerprint,
            tampered_provenance.provenance_fingerprint,
        )
        new_head = AtomicPaperTransactionV2.journal_head_for(
            transaction_sequence=original.transaction_sequence,
            transaction_event_id=original.transaction_event_id,
            previous_journal_head=original.previous_journal_head,
            ordering_space=original.ordering_space,
            primary_effect=original.primary_effect,
            transaction_timestamp_utc=original.transaction_timestamp_utc,
            causal_tick_id=original.causal_tick_id,
            state_before=original.state_before,
            position_after=original.state_after.position,
            account_after=original.state_after.account,
            throttle_after=original.state_after.throttle,
            loss_cluster_after=original.state_after.loss_cluster,
            progress_cursor_after=original.state_after.progress_cursor,
            entry_quote_after=original.state_after.entry_quote,
            accepted_entry_event=original.accepted_entry_event,
            trade=original.trade,
            risk_escalation=original.risk_escalation,
            effect_position=original.effect_position,
            effect_entry_quote=original.effect_entry_quote,
            effect_progress_cursor=original.effect_progress_cursor,
            effect_throttle_policy=original.effect_throttle_policy,
            effect_entry_veto_candidate=original.effect_entry_veto_candidate,
            loss_transition_updated_utc=original.loss_transition_updated_utc,
            loss_transition_policy_id=original.loss_transition_policy_id,
            loss_transition_policy_fingerprint=(
                original.loss_transition_policy_fingerprint
            ),
            loss_transition_lookback=original.loss_transition_lookback,
            loss_transition_threshold=original.loss_transition_threshold,
            loss_transition_pause_entries=original.loss_transition_pause_entries,
            effect_target_kill_level=original.effect_target_kill_level,
            kill_level_after=original.state_after.risk.kill_level,
            risk_business_after_fingerprint=canonical_json_sha256(
                original.state_after.risk.business_payload()
            ),
            control_authorization_reference=(
                original.control_authorization_reference
            ),
            effect_entry_denial_provenance=tampered_provenance,
        )
        tampered_after = replace(
            original.state_after,
            journal_head=new_head,
            risk=replace(original.state_after.risk, journal_head=new_head),
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as direct:
            replace(
                original,
                state_after=tampered_after,
                effect_entry_denial_provenance=tampered_provenance,
            )
        self.assertEqual(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            direct.exception.reason_code,
        )

        tampered_record = original.to_record()
        tampered_record["state_after"] = tampered_after.to_record()
        tampered_record["effect_entry_denial_provenance"] = (
            tampered_provenance.to_record()
        )
        tampered_record["transaction_fingerprint"] = canonical_json_sha256(
            {
                key: value
                for key, value in tampered_record.items()
                if key != "transaction_fingerprint"
            }
        )
        path.write_text(
            json.dumps(
                tampered_record,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            + "\n",
            encoding="ascii",
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as journal:
            self.coordinator.recover()
        self.assertEqual(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            journal.exception.reason_code,
        )
        self.assertEqual(1, len(list(self.coordinator.transaction_directory.iterdir())))
        self.assertEqual(1, self.coordinator.load_state().transaction_sequence)

    def test_entry_denial_provenance_omission_preserves_base_transaction_shape(self) -> None:
        current = self.coordinator.load_state()
        cursor = AtomicProgressCursorV1(
            schema_version=1,
            snapshot_id="SNAP-ORDINARY-PROGRESS",
            timestamp_utc="2026-08-20T12:02:00Z",
            tick_id=302,
            intent_id="INTENT-ORDINARY-PROGRESS",
        )
        result = self.coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="ORDINARY-PROGRESS",
        )
        transaction = self.coordinator._existing("ORDINARY-PROGRESS")
        assert transaction is not None
        record = transaction.to_record()
        self.assertNotIn("effect_entry_denial_provenance", record)
        self.assertIsNone(transaction.effect_entry_denial_provenance)
        self.assertEqual(
            transaction,
            AtomicPaperTransactionV2.from_record(record),
        )
        explicit_null = dict(record)
        explicit_null["effect_entry_denial_provenance"] = None
        with self.assertRaises(PaperAtomicCoordinatorError):
            AtomicPaperTransactionV2.from_record(explicit_null)
        self.assertEqual(result.state, self.coordinator.load_state())
        self.assertEqual(current.position, result.state.position)

    def test_none_provenance_golden_matrix_all_effects(self) -> None:
        expected = {
            "PROGRESS": (
                "94417f540e9026241afef81ad5de318cc5c91c420575b54721474d2fdadf4e53",
                "a2b2f1a303abca1512916274307e431af56aaccfc12f1d266324753ae349dfe5",
                "7661715d187ed9067dc226e075f6b5b199e6a81d57cb1ad0d1834d94c9272433",
            ),
            "OPEN": (
                "8d53c1aa950e0b440c675f6e33cdc272d78927639cf5df92a2f6233318ee5dd2",
                "73cf8b8c806d877a8c39c81fe34316534e60df866dbfc6b8ce01c75b9aa1dade",
                "da577fd17171d9d9796f8e0338534d126088a1c7e75c7643dc0e2587ce8b9df7",
            ),
            "CLOSE": (
                "dc753fcdb17c303d5d4a320de5130ec98db0988ec84ca20d4d7234d008fe5f38",
                "1cb4ddce86640de8ecac693510e22d5deda4555474794a937b3212db80aa3ce4",
                "58eaf1c6078d79e1156262277461bbf6532221d561410f0cc351d814b8feb4ee",
            ),
            "ENTRY_VETO": (
                "49cfeb3f0be1a8f974006c2f7aa23755a03e3cb65f461adee6bd6d0184446e28",
                "55d71149582a095dc510bf917616d59f8ecdead1bded7948b0d4bf7621e4912e",
                "846c4d4c26e7df2c79d2ee5f28b83e7c02bd49bed6d3e865bab200b4be3f51a8",
            ),
            "KILL": (
                "90399c9479fff6a95bbfc5b32be99859db7a5a99691c23af81cbee7691f24ea0",
                "a22f4ac2ee3bae7a60337c6a6d7b0ab6cac3234e6d53f2d7e9894da354ff68ba",
                "7855847232d3895babd7db346de32a279e0248b6650f0975492a7b2eba12c4f8",
            ),
        }
        transactions = {}

        def initialize(name: str, state=None):
            coordinator = self._make_coordinator(self.temp / name)
            target = self.initial_state if state is None else state
            coordinator.initialize(
                target,
                committed_authority_target_state_fingerprint=(
                    target.state_fingerprint
                ),
            )
            self.coordinator = coordinator
            return coordinator

        coordinator = initialize("golden-none-progress")
        cursor = AtomicProgressCursorV1(
            1,
            "SNAP-GOLD-PROGRESS",
            "2026-08-20T15:00:00Z",
            700,
            "INTENT-GOLD-PROGRESS",
        )
        coordinator.commit_progress(
            progress_cursor=cursor,
            transaction_event_id="GOLD-PROGRESS",
        )
        transactions["PROGRESS"] = coordinator._existing("GOLD-PROGRESS")

        coordinator = initialize("golden-none-open")
        quote, position, event, cursor = self._quote_and_open(
            event_id="GOLD-OPEN",
            timestamp="2026-08-20T15:01:00Z",
            tick_id=701,
        )
        coordinator.commit_open(
            position_after=position,
            entry_quote=quote,
            accepted_entry_event=event,
            progress_cursor=cursor,
        )
        transactions["OPEN"] = coordinator._existing("GOLD-OPEN")

        coordinator = initialize("golden-none-close")
        quote, position, event, cursor = self._quote_and_open(
            event_id="OPEN-1",
            timestamp="2026-08-20T10:00:00Z",
            tick_id=100,
        )
        coordinator.commit_open(
            position_after=position,
            entry_quote=quote,
            accepted_entry_event=event,
            progress_cursor=cursor,
        )
        flat, trade, close_cursor = self._close_values(quote)
        coordinator.commit_close(
            position_after=flat,
            trade=trade,
            progress_cursor=close_cursor,
            loss_updated_utc="2026-08-20T11:00:00Z",
        )
        transactions["CLOSE"] = coordinator._existing("CLOSE-1")

        loss = replace(
            self.initial_state.loss_cluster,
            pause_entries_remaining=2,
        )
        loss_state = replace(
            self.initial_state,
            loss_cluster=loss,
            risk=replace(
                self.initial_state.risk,
                entry_allowed=False,
                reason_codes=("LOSS_CLUSTER_PAUSE",),
                loss_cluster_fingerprint=loss.state_fingerprint,
            ),
        )
        coordinator = initialize("golden-none-entry-veto", loss_state)
        cursor = AtomicProgressCursorV1(
            1,
            "SNAP-GOLD-VETO",
            "2026-08-20T15:03:00Z",
            703,
            "INTENT-GOLD-VETO",
        )
        candidate = self._entry_veto_candidate(
            cursor=cursor,
            event_id="GOLD-VETO",
            loss_state=loss_state.loss_cluster,
        )
        coordinator.commit_entry_veto(
            progress_cursor=cursor,
            entry_candidate=candidate,
            transaction_event_id="GOLD-VETO",
            loss_updated_utc=cursor.timestamp_utc,
        )
        transactions["ENTRY_VETO"] = coordinator._existing("GOLD-VETO")

        coordinator = initialize("golden-none-kill")
        coordinator.commit_kill(
            transaction_event_id="GOLD-KILL",
            target_kill_level="HARD",
            reason_code="PEE_GOLD_KILL",
            authorization_reference="AUTH-GOLD-KILL",
            transaction_timestamp_utc="2026-08-20T15:04:00Z",
            causal_tick_id=704,
        )
        transactions["KILL"] = coordinator._existing("GOLD-KILL")

        for effect, transaction in transactions.items():
            with self.subTest(effect=effect):
                assert transaction is not None
                record = transaction.to_record()
                self.assertNotIn("effect_entry_denial_provenance", record)
                self.assertIsNone(transaction.effect_entry_denial_provenance)
                self.assertEqual(
                    expected[effect],
                    (
                        canonical_json_sha256(record),
                        transaction.transaction_fingerprint,
                        transaction.state_after.journal_head,
                    ),
                )

    def test_entry_denial_origin_matrix_and_loss_exclusivity(self) -> None:
        cases = (
            ("STATE_CAPABILITY", False, True),
            ("STATE_CAPABILITY", True, True),
            ("RUNTIME_GATE_CAPABILITY", False, False),
            ("ECONOMICS_AUTHORIZATION", True, False),
            ("ATOMIC_ENTRY_GUARD", True, False),
        )
        for index, (origin, capability, state_blocked) in enumerate(cases, 1):
            with self.subTest(origin=origin, capability=capability):
                state = self.initial_state
                if state_blocked:
                    state = replace(
                        state,
                        risk=replace(
                            state.risk,
                            entry_allowed=False,
                            reason_codes=("PEE_S4_NON_LOSS_BLOCK",),
                        ),
                    )
                coordinator = self._make_coordinator(
                    self.temp / f"denial-origin-{index}"
                )
                coordinator.initialize(
                    state,
                    committed_authority_target_state_fingerprint=(
                        state.state_fingerprint
                    ),
                )
                cursor = AtomicProgressCursorV1(
                    schema_version=1,
                    snapshot_id=f"SNAP-DENIAL-ORIGIN-{index}",
                    timestamp_utc=f"2026-08-20T12:{index + 2:02d}:00Z",
                    tick_id=302 + index,
                    intent_id=f"INTENT-DENIAL-ORIGIN-{index}",
                )
                provenance = self._entry_denial_provenance(
                    state=state,
                    cursor=cursor,
                    event_id=f"DENIAL-ORIGIN-{index}",
                    origin=origin,
                    capability=capability,
                )
                committed = coordinator.commit_progress(
                    progress_cursor=cursor,
                    transaction_event_id=f"DENIAL-ORIGIN-{index}",
                    effect_entry_denial_provenance=provenance,
                )
                self.assertEqual(1, committed.state.transaction_sequence)

        invalid_cases = (
            ("STATE_CAPABILITY", False, False),
            ("STATE_CAPABILITY", True, False),
            ("RUNTIME_GATE_CAPABILITY", True, False),
            ("RUNTIME_GATE_CAPABILITY", False, True),
            ("ECONOMICS_AUTHORIZATION", False, False),
            ("ECONOMICS_AUTHORIZATION", True, True),
            ("ATOMIC_ENTRY_GUARD", False, False),
            ("ATOMIC_ENTRY_GUARD", True, True),
        )
        for index, (origin, capability, state_blocked) in enumerate(
            invalid_cases,
            10,
        ):
            with self.subTest(
                invalid_origin=origin,
                capability=capability,
                state_blocked=state_blocked,
            ):
                state = self.initial_state
                if state_blocked:
                    state = replace(
                        state,
                        risk=replace(
                            state.risk,
                            entry_allowed=False,
                            reason_codes=("PEE_S4_NON_LOSS_BLOCK",),
                        ),
                    )
                coordinator = self._make_coordinator(
                    self.temp / f"denial-origin-invalid-{index}"
                )
                coordinator.initialize(
                    state,
                    committed_authority_target_state_fingerprint=(
                        state.state_fingerprint
                    ),
                )
                cursor = AtomicProgressCursorV1(
                    schema_version=1,
                    snapshot_id=f"SNAP-DENIAL-ORIGIN-INVALID-{index}",
                    timestamp_utc=f"2026-08-20T14:{index:02d}:00Z",
                    tick_id=600 + index,
                    intent_id=f"INTENT-DENIAL-ORIGIN-INVALID-{index}",
                )
                event_id = f"DENIAL-ORIGIN-INVALID-{index}"
                provenance = self._entry_denial_provenance(
                    state=state,
                    cursor=cursor,
                    event_id=event_id,
                    origin=origin,
                    capability=capability,
                )
                with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                    coordinator.commit_progress(
                        progress_cursor=cursor,
                        transaction_event_id=event_id,
                        effect_entry_denial_provenance=provenance,
                    )
                self.assertEqual(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    caught.exception.reason_code,
                )
                self.assertEqual([], coordinator._transactions())
                self.assertEqual(state, coordinator.load_state())

        def transaction_arguments(
            transaction: AtomicPaperTransactionV2,
        ) -> dict[str, object]:
            return {
                "event_id": transaction.transaction_event_id,
                "ordering_space": transaction.ordering_space,
                "effect": transaction.primary_effect,
                "timestamp": transaction.transaction_timestamp_utc,
                "tick_id": transaction.causal_tick_id,
                "position_after": transaction.state_after.position,
                "account_after": transaction.state_after.account,
                "throttle_after": transaction.state_after.throttle,
                "loss_after": transaction.state_after.loss_cluster,
                "cursor_after": transaction.state_after.progress_cursor,
                "quote_after": transaction.state_after.entry_quote,
                "accepted_entry_event": transaction.accepted_entry_event,
                "trade": transaction.trade,
                "risk_escalation": transaction.risk_escalation,
                "control_authorization_reference": (
                    transaction.control_authorization_reference
                ),
                "target_kill_level": transaction.effect_target_kill_level or None,
                "effect_position": transaction.effect_position,
                "effect_entry_quote": transaction.effect_entry_quote,
                "effect_progress_cursor": transaction.effect_progress_cursor,
                "effect_throttle_policy": transaction.effect_throttle_policy,
                "effect_entry_veto_candidate": (
                    transaction.effect_entry_veto_candidate
                ),
                "loss_transition_updated_utc": (
                    transaction.loss_transition_updated_utc
                ),
                "loss_transition_policy_id": transaction.loss_transition_policy_id,
                "loss_transition_policy_fingerprint": (
                    transaction.loss_transition_policy_fingerprint
                ),
                "loss_transition_lookback": transaction.loss_transition_lookback,
                "loss_transition_threshold": transaction.loss_transition_threshold,
                "loss_transition_pause_entries": (
                    transaction.loss_transition_pause_entries
                ),
            }

        effect_transactions: list[
            tuple[str, PaperAtomicCoordinatorV2, AtomicPaperTransactionV2]
        ] = []

        open_coordinator = self._make_coordinator(self.temp / "denial-effect-open")
        open_coordinator.initialize(
            self.initial_state,
            committed_authority_target_state_fingerprint=(
                self.initial_state.state_fingerprint
            ),
        )
        quote, position, entry_event, open_cursor = self._quote_and_open(
            event_id="DENIAL-VALID-OPEN",
            timestamp="2026-08-20T14:30:00Z",
            tick_id=630,
            coordinator=open_coordinator,
        )
        open_coordinator.commit_open(
            position_after=position,
            entry_quote=quote,
            accepted_entry_event=entry_event,
            progress_cursor=open_cursor,
        )
        open_transaction = open_coordinator._existing("DENIAL-VALID-OPEN")
        assert open_transaction is not None
        effect_transactions.append(("OPEN", open_coordinator, open_transaction))

        close_coordinator = self._make_coordinator(self.temp / "denial-effect-close")
        close_coordinator.initialize(
            self.initial_state,
            committed_authority_target_state_fingerprint=(
                self.initial_state.state_fingerprint
            ),
        )
        quote, position, entry_event, open_cursor = self._quote_and_open(
            event_id="DENIAL-CLOSE-PREREQUISITE",
            timestamp="2026-08-20T10:00:00Z",
            tick_id=100,
            coordinator=close_coordinator,
        )
        close_coordinator.commit_open(
            position_after=position,
            entry_quote=quote,
            accepted_entry_event=entry_event,
            progress_cursor=open_cursor,
        )
        flat, trade, close_cursor = self._close_values(
            quote,
            coordinator=close_coordinator,
        )
        close_coordinator.commit_close(
            position_after=flat,
            trade=trade,
            progress_cursor=close_cursor,
            loss_updated_utc=close_cursor.timestamp_utc,
        )
        close_transaction = close_coordinator._existing(trade.settlement_event_id)
        assert close_transaction is not None
        effect_transactions.append(("CLOSE", close_coordinator, close_transaction))

        veto_loss = replace(
            self.initial_state.loss_cluster,
            pause_entries_remaining=2,
        )
        veto_state = replace(
            self.initial_state,
            loss_cluster=veto_loss,
            risk=replace(
                self.initial_state.risk,
                entry_allowed=False,
                reason_codes=("LOSS_CLUSTER_PAUSE",),
                loss_cluster_fingerprint=veto_loss.state_fingerprint,
            ),
        )
        veto_coordinator = self._make_coordinator(self.temp / "denial-effect-veto")
        veto_coordinator.initialize(
            veto_state,
            committed_authority_target_state_fingerprint=veto_state.state_fingerprint,
        )
        veto_cursor = AtomicProgressCursorV1(
            1,
            "SNAP-DENIAL-VALID-VETO",
            "2026-08-20T14:32:00Z",
            632,
            "INTENT-DENIAL-VALID-VETO",
        )
        veto_candidate = self._entry_veto_candidate(
            cursor=veto_cursor,
            event_id="DENIAL-VALID-VETO",
            loss_state=veto_loss,
        )
        veto_coordinator.commit_entry_veto(
            progress_cursor=veto_cursor,
            entry_candidate=veto_candidate,
            transaction_event_id="DENIAL-VALID-VETO",
            loss_updated_utc=veto_cursor.timestamp_utc,
        )
        veto_transaction = veto_coordinator._existing("DENIAL-VALID-VETO")
        assert veto_transaction is not None
        effect_transactions.append(("ENTRY_VETO", veto_coordinator, veto_transaction))

        kill_coordinator = self._make_coordinator(self.temp / "denial-effect-kill")
        kill_coordinator.initialize(
            self.initial_state,
            committed_authority_target_state_fingerprint=(
                self.initial_state.state_fingerprint
            ),
        )
        kill_coordinator.commit_kill(
            transaction_event_id="DENIAL-VALID-KILL",
            target_kill_level="HARD",
            reason_code="PEE_DENIAL_VALID_KILL",
            authorization_reference="AUTH-DENIAL-VALID-KILL",
            transaction_timestamp_utc="2026-08-20T14:33:00Z",
            causal_tick_id=633,
        )
        kill_transaction = kill_coordinator._existing("DENIAL-VALID-KILL")
        assert kill_transaction is not None
        effect_transactions.append(("KILL", kill_coordinator, kill_transaction))

        for effect, coordinator, transaction in effect_transactions:
            with self.subTest(disallowed_effect=effect):
                arguments = transaction_arguments(transaction)
                positive = coordinator._build_transaction(
                    transaction.state_before,
                    **arguments,
                )
                self.assertEqual(transaction.to_record(), positive.to_record())
                persisted_state = coordinator.load_state()
                persisted_journal = coordinator._transactions()
                effect_cursor = transaction.effect_progress_cursor
                if effect_cursor is None:
                    effect_cursor = AtomicProgressCursorV1(
                        1,
                        "SNAP-DENIAL-VALID-KILL",
                        transaction.transaction_timestamp_utc,
                        transaction.causal_tick_id,
                        "INTENT-DENIAL-VALID-KILL",
                    )
                provenance = self._entry_denial_provenance(
                    state=transaction.state_before,
                    cursor=effect_cursor,
                    event_id=transaction.transaction_event_id,
                )
                with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                    coordinator._build_transaction(
                        transaction.state_before,
                        **arguments,
                        effect_entry_denial_provenance=provenance,
                    )
                self.assertEqual(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    caught.exception.reason_code,
                )
                self.assertEqual(persisted_journal, coordinator._transactions())
                self.assertEqual(persisted_state, coordinator.load_state())

        progress_coordinator = self._make_coordinator(
            self.temp / "denial-effect-progress-entry-event"
        )
        progress_state = self.initial_state
        progress_coordinator.initialize(
            progress_state,
            committed_authority_target_state_fingerprint=(
                progress_state.state_fingerprint
            ),
        )
        progress_cursor = AtomicProgressCursorV1(
            1,
            "SNAP-DENIAL-PROGRESS-EVENT",
            "2026-08-20T14:34:00Z",
            634,
            "INTENT-DENIAL-PROGRESS-EVENT",
        )
        progress_event_id = "DENIAL-PROGRESS-EVENT"
        progress_provenance = self._entry_denial_provenance(
            state=progress_state,
            cursor=progress_cursor,
            event_id=progress_event_id,
        )
        progress_arguments = {
            "event_id": progress_event_id,
            "ordering_space": "TICK",
            "effect": "PROGRESS",
            "timestamp": progress_cursor.timestamp_utc,
            "tick_id": progress_cursor.tick_id,
            "position_after": progress_state.position,
            "account_after": progress_state.account,
            "throttle_after": progress_state.throttle,
            "loss_after": progress_state.loss_cluster,
            "cursor_after": progress_cursor,
            "quote_after": progress_state.entry_quote,
            "effect_progress_cursor": progress_cursor,
            "effect_entry_denial_provenance": progress_provenance,
        }
        positive_progress = progress_coordinator._build_transaction(
            progress_state,
            **progress_arguments,
        )
        self.assertEqual("PROGRESS", positive_progress.primary_effect)
        conflicting_event = AcceptedEntryEventV1(
            schema_version=1,
            entry_sequence=1,
            entry_event_id=progress_event_id,
            previous_entry_event_id="",
            entry_timestamp_utc=progress_cursor.timestamp_utc,
            policy_model_version=self.policy.policy_model_version,
            policy_profile_id=self.policy.policy_profile_id,
            policy_fingerprint=self.policy.policy_fingerprint,
        )
        with self.assertRaises(PaperAtomicCoordinatorError) as caught:
            progress_coordinator._build_transaction(
                progress_state,
                **progress_arguments,
                accepted_entry_event=conflicting_event,
            )
        self.assertEqual(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            caught.exception.reason_code,
        )
        self.assertEqual([], progress_coordinator._transactions())
        self.assertEqual(progress_state, progress_coordinator.load_state())

        loss = replace(self.initial_state.loss_cluster, pause_entries_remaining=2)
        loss_state = replace(
            self.initial_state,
            loss_cluster=loss,
            risk=replace(
                self.initial_state.risk,
                entry_allowed=False,
                reason_codes=("LOSS_CLUSTER_PAUSE",),
                loss_cluster_fingerprint=loss.state_fingerprint,
            ),
        )
        for index, origin in enumerate(
            ("STATE_CAPABILITY", "ATOMIC_ENTRY_GUARD"),
            20,
        ):
            coordinator = self._make_coordinator(self.temp / f"loss-origin-{index}")
            coordinator.initialize(
                loss_state,
                committed_authority_target_state_fingerprint=(
                    loss_state.state_fingerprint
                ),
            )
            cursor = AtomicProgressCursorV1(
                schema_version=1,
                snapshot_id=f"SNAP-LOSS-ORIGIN-{index}",
                timestamp_utc=f"2026-08-20T12:{index:02d}:00Z",
                tick_id=400 + index,
                intent_id=f"INTENT-LOSS-ORIGIN-{index}",
            )
            provenance = self._entry_denial_provenance(
                state=loss_state,
                cursor=cursor,
                event_id=f"LOSS-ORIGIN-{index}",
                origin=origin,
                capability=True,
            )
            with self.subTest(loss_origin=origin):
                with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                    coordinator.commit_progress(
                        progress_cursor=cursor,
                        transaction_event_id=f"LOSS-ORIGIN-{index}",
                        effect_entry_denial_provenance=provenance,
                    )
                self.assertEqual(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    caught.exception.reason_code,
                )
                self.assertEqual([], coordinator._transactions())
                self.assertEqual(loss_state, coordinator.load_state())

    def test_entry_denial_provenance_fault_recovery_grid(self) -> None:
        interruption_messages = {
            "BEFORE_JOURNAL": (
                "simulated interruption before Atomic V2 journal write"
            ),
            "AFTER_JOURNAL": (
                "simulated interruption after durable Atomic V2 journal write"
            ),
            "BEFORE_SNAPSHOT": (
                "simulated interruption before Atomic V2 snapshot replace"
            ),
            "AFTER_SNAPSHOT": (
                "simulated interruption after Atomic V2 snapshot replace"
            ),
        }
        for index, fault in enumerate(
            ("BEFORE_JOURNAL", "AFTER_JOURNAL", "BEFORE_SNAPSHOT", "AFTER_SNAPSHOT"),
            1,
        ):
            with self.subTest(fault=fault):
                coordinator = self._make_coordinator(
                    self.temp / f"denial-fault-{index}"
                )
                state = self.initial_state
                coordinator.initialize(
                    state,
                    committed_authority_target_state_fingerprint=(
                        state.state_fingerprint
                    ),
                )
                cursor = AtomicProgressCursorV1(
                    schema_version=1,
                    snapshot_id=f"SNAP-DENIAL-FAULT-{index}",
                    timestamp_utc=f"2026-08-20T13:0{index}:00Z",
                    tick_id=500 + index,
                    intent_id=f"INTENT-DENIAL-FAULT-{index}",
                )
                event_id = f"DENIAL-FAULT-{index}"
                provenance = self._entry_denial_provenance(
                    state=state,
                    cursor=cursor,
                    event_id=event_id,
                )
                before_risk_business = state.risk.business_payload()
                before_risk_business.pop("progress_cursor_fingerprint")
                before_business = (
                    state.position.state_fingerprint,
                    state.account.state_fingerprint,
                    state.throttle.state_fingerprint,
                    state.loss_cluster.state_fingerprint,
                    canonical_json_sha256(before_risk_business),
                )
                with patch.object(
                    coordinator,
                    "_risk_after",
                    side_effect=AssertionError("risk redecision"),
                ) as risk_sentinel, patch.object(
                    coordinator,
                    "_validate_open_guards",
                    side_effect=AssertionError("OPEN guard redecision"),
                ) as guard_sentinel:
                    with self.assertRaises(
                        SimulatedAtomicTransactionInterruption
                    ) as interruption:
                        coordinator.commit_progress(
                            progress_cursor=cursor,
                            transaction_event_id=event_id,
                            effect_entry_denial_provenance=provenance,
                            simulate_interruption_at=fault,
                        )
                    self.assertEqual(
                        interruption_messages[fault],
                        str(interruption.exception),
                    )
                    entries_after_fault = coordinator._transactions()
                    snapshot_after_fault = coordinator.load_state()
                    expected_durable = 0 if fault == "BEFORE_JOURNAL" else 1
                    expected_snapshot_sequence = (
                        1 if fault == "AFTER_SNAPSHOT" else 0
                    )
                    self.assertEqual(expected_durable, len(entries_after_fault))
                    self.assertEqual(
                        expected_snapshot_sequence,
                        snapshot_after_fault.transaction_sequence,
                    )
                    self.assertEqual(
                        cursor if expected_snapshot_sequence else state.progress_cursor,
                        snapshot_after_fault.progress_cursor,
                    )
                    self.assertEqual(
                        (
                            entries_after_fault[0][1].state_after.journal_head
                            if expected_snapshot_sequence
                            else state.journal_head
                        ),
                        snapshot_after_fault.journal_head,
                    )

                    if fault == "BEFORE_JOURNAL":
                        committed = coordinator.commit_progress(
                            progress_cursor=cursor,
                            transaction_event_id=event_id,
                            effect_entry_denial_provenance=provenance,
                        )
                        self.assertTrue(committed.newly_committed)
                        self.assertFalse(committed.already_committed)
                        self.assertEqual(1, len(coordinator._transactions()))
                        transaction = coordinator._transactions()[0][1]
                        materialized = committed
                    else:
                        transaction = entries_after_fault[0][1]
                        materialized = coordinator.recover()

                    self.assertEqual(
                        provenance,
                        transaction.effect_entry_denial_provenance,
                    )
                    assert transaction.effect_entry_denial_provenance is not None
                    self.assertEqual(
                        provenance.to_record(),
                        transaction.effect_entry_denial_provenance.to_record(),
                    )
                    self.assertEqual(
                        provenance.provenance_fingerprint,
                        transaction.effect_entry_denial_provenance.provenance_fingerprint,
                    )
                    self.assertEqual(cursor, transaction.state_after.progress_cursor)
                    self.assertEqual(
                        cursor.cursor_fingerprint,
                        transaction.state_after.progress_cursor.cursor_fingerprint,
                    )
                    self.assertEqual(1, transaction.state_after.transaction_sequence)
                    self.assertEqual(
                        transaction.state_after.journal_head,
                        transaction.state_after.risk.journal_head,
                    )
                    self.assertEqual(
                        transaction.transaction_fingerprint,
                        coordinator._existing(event_id).transaction_fingerprint,
                    )
                    after_risk_business = (
                        transaction.state_after.risk.business_payload()
                    )
                    after_risk_business.pop("progress_cursor_fingerprint")
                    self.assertEqual(
                        before_business,
                        (
                            transaction.state_after.position.state_fingerprint,
                            transaction.state_after.account.state_fingerprint,
                            transaction.state_after.throttle.state_fingerprint,
                            transaction.state_after.loss_cluster.state_fingerprint,
                            canonical_json_sha256(after_risk_business),
                        ),
                    )
                    self.assertEqual(transaction.state_after, materialized.state)
                    replay = coordinator.commit_progress(
                        progress_cursor=cursor,
                        transaction_event_id=event_id,
                        effect_entry_denial_provenance=provenance,
                    )
                    self.assertEqual(materialized.state, replay.state)
                    self.assertTrue(replay.already_committed)
                    self.assertFalse(replay.newly_committed)
                    self.assertEqual(1, len(coordinator._transactions()))
                    self.assertEqual(0, risk_sentinel.call_count)
                    self.assertEqual(0, guard_sentinel.call_count)

    def test_entry_denial_fingerprint_transaction_and_head_sensitivity(self) -> None:
        transactions = []
        provenances = []
        for index, (origin, capability) in enumerate(
            (
                ("RUNTIME_GATE_CAPABILITY", False),
                ("ECONOMICS_AUTHORIZATION", True),
            ),
            1,
        ):
            coordinator = self._make_coordinator(
                self.temp / f"denial-sensitivity-{index}"
            )
            state = self.initial_state
            coordinator.initialize(
                state,
                committed_authority_target_state_fingerprint=state.state_fingerprint,
            )
            cursor = AtomicProgressCursorV1(
                schema_version=1,
                snapshot_id="SNAP-DENIAL-SENSITIVITY",
                timestamp_utc="2026-08-20T13:10:00Z",
                tick_id=510,
                intent_id="INTENT-DENIAL-SENSITIVITY",
            )
            provenance = self._entry_denial_provenance(
                state=state,
                cursor=cursor,
                event_id="DENIAL-SENSITIVITY",
                origin=origin,
                capability=capability,
            )
            coordinator.commit_progress(
                progress_cursor=cursor,
                transaction_event_id="DENIAL-SENSITIVITY",
                effect_entry_denial_provenance=provenance,
            )
            transaction = coordinator._existing("DENIAL-SENSITIVITY")
            assert transaction is not None
            provenances.append(provenance)
            transactions.append(transaction)
        self.assertNotEqual(
            provenances[0].provenance_fingerprint,
            provenances[1].provenance_fingerprint,
        )
        self.assertNotEqual(
            transactions[0].state_after.journal_head,
            transactions[1].state_after.journal_head,
        )
        self.assertNotEqual(
            transactions[0].transaction_fingerprint,
            transactions[1].transaction_fingerprint,
        )

        base = provenances[0]
        variants = (
            replace(base, transaction_event_id="DENIAL-SENSITIVITY-OTHER"),
            replace(base, snapshot_id="SNAP-DENIAL-SENSITIVITY-OTHER"),
            replace(base, timestamp_utc="2026-08-20T13:11:00Z"),
            replace(base, tick_id=511),
            replace(base, intent_id="INTENT-DENIAL-SENSITIVITY-OTHER"),
            replace(base, intent_action="OPEN_SHORT"),
            replace(base, state_before_fingerprint=digest("other-state")),
            replace(
                base,
                denial_origin="ECONOMICS_AUTHORIZATION",
                entry_capability_allowed=True,
            ),
        )
        for variant in variants:
            with self.subTest(variant=variant.canonical_payload()):
                self.assertNotEqual(
                    base.provenance_fingerprint,
                    variant.provenance_fingerprint,
                )

    def test_entry_denial_resource_failures_classify_without_partial_state(self) -> None:
        failures = (
            OSError(errno.ENOSPC, "disk full"),
            PermissionError(errno.EACCES, "permission denied"),
            OSError(errno.EMFILE, "file descriptor exhausted"),
            MemoryError("memory exhausted"),
        )
        for index, failure in enumerate(failures, 1):
            coordinator = self._make_coordinator(
                self.temp / f"denial-resource-{index}"
            )
            state = self.initial_state
            coordinator.initialize(
                state,
                committed_authority_target_state_fingerprint=state.state_fingerprint,
            )
            cursor = AtomicProgressCursorV1(
                schema_version=1,
                snapshot_id=f"SNAP-DENIAL-RESOURCE-{index}",
                timestamp_utc=f"2026-08-20T13:{10 + index:02d}:00Z",
                tick_id=520 + index,
                intent_id=f"INTENT-DENIAL-RESOURCE-{index}",
            )
            provenance = self._entry_denial_provenance(
                state=state,
                cursor=cursor,
                event_id=f"DENIAL-RESOURCE-{index}",
            )
            with self.subTest(failure=type(failure).__name__), patch(
                "live_l1.state.paper_atomic_coordinator._create_new_json",
                side_effect=failure,
            ):
                with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                    coordinator.commit_progress(
                        progress_cursor=cursor,
                        transaction_event_id=f"DENIAL-RESOURCE-{index}",
                        effect_entry_denial_provenance=provenance,
                    )
                self.assertEqual(
                    AtomicCoordinatorReasonCode.RESOURCE_EXHAUSTED,
                    caught.exception.reason_code,
                )
            self.assertEqual(state, coordinator.load_state())
            self.assertEqual([], coordinator._transactions())

    def test_entry_denial_failure_code_precedence_is_stable(self) -> None:
        state = self.coordinator.load_state()
        cursor = AtomicProgressCursorV1(
            1,
            "SNAP-DENIAL-PRECEDENCE",
            "2026-08-20T15:20:00Z",
            720,
            "INTENT-DENIAL-PRECEDENCE",
        )
        provenance = self._entry_denial_provenance(
            state=state,
            cursor=cursor,
            event_id="DENIAL-PRECEDENCE",
        )
        valid = provenance.to_record()
        cases = []
        schema_and_fingerprint = dict(valid)
        schema_and_fingerprint["schema_version"] = 2
        schema_and_fingerprint["provenance_fingerprint"] = digest("wrong")
        cases.append(
            (
                "schema-before-fingerprint",
                schema_and_fingerprint,
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
            )
        )
        origin_and_fingerprint = dict(valid)
        origin_and_fingerprint["denial_origin"] = "UNKNOWN_ORIGIN"
        origin_and_fingerprint["provenance_fingerprint"] = digest("wrong")
        cases.append(
            (
                "canonicality-before-fingerprint",
                origin_and_fingerprint,
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            )
        )
        fingerprint_only = dict(valid)
        fingerprint_only["provenance_fingerprint"] = digest("wrong")
        cases.append(
            (
                "fingerprint-after-schema-and-canonicality",
                fingerprint_only,
                AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
            )
        )
        for name, record, expected in cases:
            with self.subTest(name=name):
                with self.assertRaises(PaperAtomicCoordinatorError) as caught:
                    AtomicEntryDenialProvenanceV1.from_record(record)
                self.assertEqual(expected, caught.exception.reason_code)
        self.assertEqual(state, self.coordinator.load_state())
        self.assertEqual([], self.coordinator._transactions())


if __name__ == "__main__":
    unittest.main()
