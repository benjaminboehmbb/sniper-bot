#!/usr/bin/env python3
"""Focused offline contract tests for IU4 I6 recovery/projection artifacts."""

from __future__ import annotations

import hashlib
import builtins
import dis
import errno
import json
import os
import tempfile
import unittest
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import patch

from live_l1.state.models import LegacyRiskStateS4ProjectionV1
from live_l1.state.models import PositionStateS2, RiskStateS4
from live_l1.state.paper_iu4_recovery_projection import (
    EMPTY,
    NONE,
    IU4CleanGenesisManifestV1,
    IU4CompatibilityProjectionV1,
    IU4LegacySafetySnapshotV1,
    IU4PersistenceWorkerDeathTrustAnchorV1,
    IU4PersistenceWorkerExclusionProofV1,
    IU4ProjectionCursorV1,
    IU4ProjectionPublisherV1,
    IU4RecoveryMonitoringReportV1,
    IU4RecoveryOrchestratorV1,
    IU4RecoveryProjectionError,
    IU4StateHandoffManifestV1,
    IU4TerminalMonitoringObservationV1,
    IU4TerminalRuntimeProfileAnchorV1,
    IU4TerminalRuntimeProfileRegistryV1,
    build_monitoring_report,
    canonical_json_bytes,
    classify_owner_state,
    handoff_mapping_record,
    handoff_planned_generation_id,
    projection_root_realpath_sha256,
    terminal_static_bindings_fingerprint,
    validate_worker_exclusion,
)
from live_l1.state.state_store import (
    load_or_init_state,
    persist_state,
    read_legacy_safety_projection,
    write_legacy_safety_projection,
)
from live_l1.state.iu4_lifecycle_ledger import (
    IU4LifecycleLedgerError,
    IU4LifecycleLedgerV1,
)


H = "a" * 64
H2 = "b" * 64
UTC = "2026-08-21T12:00:00Z"


def _fp(record: dict[str, object]) -> str:
    return hashlib.sha256(canonical_json_bytes(record)).hexdigest()


def _nested_resource_error(resource_error: BaseException) -> IU4LifecycleLedgerError:
    try:
        raise resource_error
    except BaseException as resource:
        try:
            raise RuntimeError("nested publication wrapper") from resource
        except RuntimeError as wrapper:
            try:
                raise IU4LifecycleLedgerError("outer ledger wrapper") from wrapper
            except IU4LifecycleLedgerError as outer:
                return outer


def _runtime_resource_error(resource_error: BaseException) -> RuntimeError:
    try:
        raise resource_error
    except BaseException as resource:
        try:
            raise RuntimeError("runtime resource wrapper") from resource
        except RuntimeError as wrapper:
            return wrapper


def _rebuild_artifact(value, **overrides):
    record = value.to_record()
    record.update(overrides)
    material = {
        name: item for name, item in record.items()
        if name not in {
            "schema_version", "artifact_type", value.ID_FIELD,
            value.FINGERPRINT_FIELD,
        }
    }
    return type(value).build(**material)


def _rebuild_observation(
    observation: IU4TerminalMonitoringObservationV1,
    group: str,
    **overrides: object,
) -> IU4TerminalMonitoringObservationV1:
    record = observation.to_record()
    record[group].update(overrides)
    material = {
        name: item for name, item in record.items()
        if name not in {
            "schema_version", "artifact_type",
            "terminal_monitoring_observation_id", "observation_fingerprint",
        }
    }
    return IU4TerminalMonitoringObservationV1.build(**material)


def _risk() -> LegacyRiskStateS4ProjectionV1:
    return LegacyRiskStateS4ProjectionV1(
        kill_level="NONE",
        cooldown_until_utc=NONE,
        trades_today=0,
        loss_today="0",
        anomaly_counter=0,
        trades_6h=0,
        last_trade_timestamp_utc=NONE,
        reason_codes=(),
    )


def _legacy_snapshot(
    *,
    owner_epoch: str = "LEGACY",
    source_path: str = "/tmp/source.json",
    system_state_id: str = "STATE-1",
    source_bytes_sha256: str = H,
    authority_generation_id: str = "GEN-1",
) -> IU4LegacySafetySnapshotV1:
    position = {
        "schema_version": 1,
        "system_state_id": system_state_id,
        "symbol": "BTCUSDT",
        "position": "FLAT",
        "side": NONE,
        "size": "0",
        "entry_price": NONE,
        "entry_timestamp_utc": NONE,
        "position_size": "0",
        "last_intent_id": NONE,
        "snapshot_id": NONE,
    }
    loss = {
        "schema_version": 2,
        "pause_entries_remaining": 0,
        "recent_closed_trade_pnls": [],
        "revision": 0,
        "updated_utc": UTC,
        "version": 2,
    }
    loss["state_fingerprint"] = _fp(loss)
    throttle = {
        "schema_version": 1,
        "entries_today": 0,
        "last_entry_event_id": NONE,
        "last_entry_timestamp_utc": NONE,
        "last_update_event_id": NONE,
        "policy_fingerprint": H,
        "policy_model_version": "PEE_RATE_V1",
        "policy_profile_id": "I6-THROTTLE",
        "recent_entry_events": [],
        "total_accepted_entry_count": 0,
        "utc_day": "2026-08-21",
    }
    throttle["state_fingerprint"] = _fp(throttle)
    cursor = {
        "schema_version": 1,
        "tick_id": 0,
        "snapshot_id": NONE,
        "intent_id": NONE,
        "timestamp_utc": NONE,
    }
    cursor["cursor_fingerprint"] = _fp(cursor)
    risk = _risk().to_record()
    return IU4LegacySafetySnapshotV1.build(
        system_state_id=system_state_id,
        symbol="BTCUSDT",
        source_path=source_path,
        source_bytes_sha256=source_bytes_sha256,
        owner_epoch=owner_epoch,
        authority_generation_id=authority_generation_id,
        position_record=position,
        risk_record=risk,
        loss_cluster_record=loss,
        loss_cluster_fingerprint=loss["state_fingerprint"],
        throttle_record=throttle,
        throttle_fingerprint=throttle["state_fingerprint"],
        progress_cursor_record=cursor,
        progress_cursor_fingerprint=cursor["cursor_fingerprint"],
        position_fingerprint=_fp(position),
        risk_fingerprint=_fp(risk),
    )


def _projection_snapshot(transaction) -> IU4LegacySafetySnapshotV1:
    state = transaction.state_after
    return _legacy_snapshot(
        owner_epoch="PEE",
        source_path=f"/tmp/{state.system_state_id}-atomic-state.json",
        system_state_id=state.system_state_id,
        source_bytes_sha256=_fp(state.to_record()),
        authority_generation_id=state.authority_generation_id,
    )


def _anchor() -> IU4PersistenceWorkerDeathTrustAnchorV1:
    return IU4PersistenceWorkerDeathTrustAnchorV1.build(
        allowed_attestor_type="TERMINAL_PARENT_GUARDIAN_V13",
        trusted_attestor_id="GUARDIAN-1",
        trusted_attestor_executable_sha256=H,
        trusted_collector_id="COLLECTOR-1",
        trusted_source_evidence_sha256=H2,
        expected_boot_id="BOOT-1",
        expected_runtime_session_id="SESSION-1",
        approval_reference="APPROVAL-1",
        approval_fingerprint=H,
        trusted_anchor_registry_id="REGISTRY-1",
        trusted_anchor_registry_fingerprint=H2,
        valid_from_utc="2026-08-21T11:00:00Z",
        valid_until_utc="2026-08-21T13:00:00Z",
    )


def _proof() -> IU4PersistenceWorkerExclusionProofV1:
    return IU4PersistenceWorkerExclusionProofV1.build(
        proof_mode="PROCESS_DEATH",
        runtime_session_id="SESSION-1",
        runtime_session_open_event_id="OPEN-1",
        runtime_session_open_record_fingerprint=H,
        authority_generation_id="GEN-1",
        authority_commit_anchor=H2,
        coordinator_id="COORD-1",
        journal_root_fingerprint=H,
        old_worker_id="WORKER-1",
        old_worker_boot_id="BOOT-1",
        old_worker_pid=123,
        old_worker_start_time_ns=1,
        old_broker_generation_id=0,
        old_worker_generation_id=1,
        attestor_type="TERMINAL_PARENT_GUARDIAN_V13",
        attestor_id="GUARDIAN-1",
        attestor_executable_sha256=H,
        collector_id="COLLECTOR-1",
        source_evidence_id="EVIDENCE-1",
        source_evidence_sha256=H2,
        observed_at_utc=UTC,
        death_evidence_kind="PIDFD_EXIT_AND_REAP_ATTESTATION",
        observed_pidfd_id="PIDFD-1",
        pidfd_exit_observed=True,
        waitid_reaped=True,
        death_exit_status_class="EXITED",
        reap_evidence_fingerprint=H,
        death_observation_sequence=1,
        worker_append_handle_closed=True,
        surviving_writer_holder_count=0,
        append_handle_inventory_fingerprint=H2,
    )


def _observation(**overrides: object) -> IU4TerminalMonitoringObservationV1:
    values = dict(
        runtime_session_id="SESSION-1", runtime_session_open_record_fingerprint=H,
        authority_generation_id="GEN-1", authority_commit_anchor=H2,
        atomic_root_fingerprint=H, source_collector_id="COLLECTOR-1",
        source_evidence_id="EVIDENCE-1", source_evidence_sha256=H2,
        observation_sequence=1, observed_at_utc=UTC,
    )
    values.update(overrides)
    return IU4TerminalMonitoringObservationV1.build_minimal_pass(**values)


def _trusted_profile_registry(
    observation: IU4TerminalMonitoringObservationV1 | None = None,
) -> IU4TerminalRuntimeProfileRegistryV1:
    trusted_observation = _observation() if observation is None else observation
    anchor = IU4TerminalRuntimeProfileAnchorV1.build(
        runtime_profile_id="RP",
        terminal_static_bindings_fingerprint=(
            terminal_static_bindings_fingerprint(trusted_observation)
        ),
    )
    return IU4TerminalRuntimeProfileRegistryV1.from_anchors((anchor,))


def _report_kwargs(observation: IU4TerminalMonitoringObservationV1) -> dict[str, object]:
    return dict(
        observation=observation, owner_epoch="PEE", report_operation="MONITOR_ONLY",
        expected_runtime_session_id=observation.runtime_session_id,
        expected_runtime_session_open_record_fingerprint=observation.runtime_session_open_record_fingerprint,
        expected_authority_generation_id=observation.authority_generation_id,
        expected_authority_commit_anchor=observation.authority_commit_anchor,
        expected_atomic_root_fingerprint=observation.atomic_root_fingerprint,
        lifecycle_root_inventory_fingerprint=H, atomic_root_inventory_fingerprint=H2,
        projection_root_inventory_fingerprint=H, authorization_valid=True,
        runtime_profile_id="RP",
        economics_profile_id="EP", economics_profile_fingerprint=H2,
        entry_throttle_profile_id="TP", entry_throttle_profile_fingerprint=H,
        runtime_control_fingerprint=H2, lifecycle_ledger_tip_event_id="LEDGER-1",
        lifecycle_ledger_tip_fingerprint=H, open_prepare_count=0,
        runtime_session_status="OPEN_CLEAN", handoff_or_genesis_manifest_id="MANIFEST-1",
        handoff_or_genesis_manifest_fingerprint=H2, atomic_journal_sequence=0,
        atomic_journal_head=EMPTY, atomic_snapshot_fingerprint=H,
        authority_root_ancestry_result="PASS", projection_cursor_id=NONE,
        projection_cursor_fingerprint=NONE, projection_cursor_sequence=0,
        projection_cursor_journal_head=EMPTY, component_fingerprints={
            "s2": H, "account": H2, "throttle": H, "loss_cluster": H2,
            "s4": H, "entry_quote": H2, "progress_cursor": H,
        }, terminal_gap_status="NONE", reported_at_utc=UTC,
    )


def _orchestrator(ledger, coordinator) -> IU4RecoveryOrchestratorV1:
    return IU4RecoveryOrchestratorV1(
        lifecycle_ledger=ledger,
        atomic_coordinator=coordinator,
        expected_repository_commit="c" * 40,
        expected_operator="OP",
        expected_secured_logs_manifest_sha256=H,
        expected_environment_check_sha256=H2,
        expected_last_state_timestamp_utc=UTC,
    )


def _genesis_manifest(coordinator, state, *, suffix: str = "I6") -> IU4CleanGenesisManifestV1:
    profiles = {
        "runtime_control_profile_id": state.runtime_control_profile_id,
        "runtime_control_fingerprint": state.runtime_control_fingerprint,
        "loss_cluster_policy_id": state.loss_cluster_policy_id,
        "loss_cluster_policy_fingerprint": state.loss_cluster_policy_fingerprint,
        "economics_profile_id": state.account.economics_profile_id,
        "economics_config_fingerprint": state.account.config_fingerprint,
        "throttle_policy_profile_id": state.throttle.policy_profile_id,
        "throttle_policy_fingerprint": state.throttle.policy_fingerprint,
    }
    components = {
        "position": state.position.state_fingerprint,
        "account": state.account.state_fingerprint,
        "throttle": state.throttle.state_fingerprint,
        "loss_cluster": state.loss_cluster.state_fingerprint,
        "progress_cursor": state.progress_cursor.cursor_fingerprint,
        "risk": state.risk.state_fingerprint,
        "entry_quote": NONE,
        "state": state.state_fingerprint,
        "business": _fp(state.business_payload()),
        "core": _fp(state.core_payload()),
    }
    state_path = str(coordinator.state_path)
    journal_path = str(coordinator.transaction_directory)
    empty_inventory = _fp({"entries": [], "journal_path": journal_path, "schema_version": 1})
    atomic_absence = _fp({"absent": True, "artifact_kind": "ATOMIC_STATE", "path": state_path, "schema_version": 1})
    legacy_absence = _fp({"absent": True, "artifact_kind": "LEGACY_STATE", "path": state_path + ".legacy", "schema_version": 1})
    return IU4CleanGenesisManifestV1.build(
        symbol="BTCUSDT",
        starting_equity=str(state.account.starting_equity_quote),
        profile_bindings=profiles,
        coordinator_id=coordinator.coordinator_id,
        system_state_id=state.system_state_id,
        state_owner_epoch="PEE",
        initial_state_record=state.to_record(),
        empty_journal_inventory_fingerprint=empty_inventory,
        component_fingerprints=components,
        state_path=state_path,
        journal_path=journal_path,
        legacy_absence_proof_sha256=legacy_absence,
        atomic_absence_proof_sha256=atomic_absence,
        operator="OP",
        operation_timestamp_utc=UTC,
        approval_reference="APP",
        approval_fingerprint=H,
        process_instance_id=f"PROCESS-{suffix}",
        operation_attempt_id=f"GENESIS-{suffix}",
    )


def _restart_authorization(coordinator, ledger, fixture, operation: str):
    from live_l1.core.paper_iu4_startup_gate import IU4RestartRecoveryAuthorizationV1

    state = coordinator.load_state(); view = ledger.view()
    return IU4RestartRecoveryAuthorizationV1(
        schema_version=1, restart_recovery_authorization_id="", operator="OP",
        decision_timestamp_utc=UTC, stop_recovery_reason="MANUAL-I6",
        previous_kill_level=state.risk.kill_level,
        secured_logs_manifest_sha256=H, last_state_timestamp_utc=UTC,
        no_open_intents_confirmed=True, environment_check_sha256=H2,
        repository_commit_sha="c" * 40, coordinator_id=coordinator.coordinator_id,
        economics_config_fingerprint=fixture.config.config_fingerprint,
        throttle_policy_fingerprint=fixture.policy.policy_fingerprint,
        runtime_control_fingerprint=fixture.runtime_control_fingerprint,
        pre_attempt_ledger_tip=view.ledger_tip,
        startup_attempt_id=f"START-{operation}",
        source_authority_commit_anchor=view.authority_commit_anchor,
        source_authority_generation_id=state.authority_generation_id,
        expected_transaction_sequence=state.transaction_sequence,
        expected_journal_head=state.journal_head,
        expected_snapshot_fingerprint=state.state_fingerprint,
        operation=operation, completion_prepare_event_id=NONE,
        completion_prepare_fingerprint=NONE, completion_operation_type=NONE,
        planned_authority_generation_id=NONE,
        completion_source_authority_anchor=NONE, target_core_fingerprint=NONE,
        expected_target_schema=NONE, expected_target_path=NONE,
        expected_commit_type=NONE, valid_from_utc="2026-08-21T11:00:00Z",
        valid_until_utc="2026-08-21T13:00:00Z",
    )


def _pee_to_legacy_material(coordinator, ledger, target_path: str):
    state = coordinator.load_state(); view = ledger.view()
    target = _legacy_snapshot(
        owner_epoch="LEGACY", source_path=target_path,
        system_state_id=state.system_state_id,
    )
    source_snapshot = _legacy_snapshot(
        owner_epoch="PEE", source_path=str(coordinator.state_path),
        system_state_id=state.system_state_id,
        source_bytes_sha256=hashlib.sha256(
            coordinator.state_path.read_bytes()
        ).hexdigest(),
        authority_generation_id=state.authority_generation_id,
    )
    target_business_fingerprint = _fp(target.to_record())
    target_core_fingerprint = _fp(target.to_record())
    generation = handoff_planned_generation_id(
        operation="PEE_TO_LEGACY",
        source_authority_generation_id=state.authority_generation_id,
        source_authority_commit_anchor=view.authority_commit_anchor,
        approval_fingerprint=H,
        target_business_payload=target.to_record(),
    )
    manifest = IU4StateHandoffManifestV1.build(
        direction="PEE_TO_LEGACY", repository_commit="c" * 40,
        symbol="BTCUSDT", coordinator_id=coordinator.coordinator_id,
        system_state_id=state.system_state_id,
        source_state_path=str(coordinator.state_path), source_state_schema=2,
        source_state_bytes_sha256=hashlib.sha256(
            coordinator.state_path.read_bytes()
        ).hexdigest(),
        source_state_fingerprint=state.state_fingerprint,
        competing_state_path=target_path, competing_state_schema=1,
        competing_state_bytes_sha256=H, competing_state_fingerprint=H2,
        source_safety_snapshot=source_snapshot.to_record(),
        target_business_fingerprint=target_business_fingerprint,
        target_core_fingerprint=target_core_fingerprint,
        previous_owner_epoch=view.owner_epoch, new_owner_epoch=view.owner_epoch + 1,
        source_authority_generation_id=state.authority_generation_id,
        source_authority_commit_anchor=view.authority_commit_anchor,
        planned_authority_generation_id=generation,
        mapping_record=handoff_mapping_record(
            direction="PEE_TO_LEGACY", source_snapshot=source_snapshot,
            target_business_fingerprint=target_business_fingerprint,
            target_core_fingerprint=target_core_fingerprint,
        ),
        operator="OP", operation_timestamp_utc=UTC,
        approval_reference="APP", approval_fingerprint=H,
        operation_attempt_id=f"PEE-TO-LEGACY-{Path(target_path).name}",
    )
    return manifest, target


def _terminal_gap_material(coordinator, ledger, fixture, *, suffix: str):
    open_event_id = f"I6-GRID-SESSION-OPEN-{suffix}"
    open_record = ledger.append(
        record_type="RUNTIME_SESSION_OPEN", lifecycle_event_id=open_event_id,
        payload={"session_id": "SESSION-1", "journal_head": EMPTY},
    )
    state = coordinator.load_state(); view = ledger.view()
    anchor = _anchor()
    proof = IU4PersistenceWorkerExclusionProofV1.build(
        proof_mode="PROCESS_DEATH", runtime_session_id="SESSION-1",
        runtime_session_open_event_id=open_event_id,
        runtime_session_open_record_fingerprint=open_record.record_fingerprint,
        authority_generation_id=state.authority_generation_id,
        authority_commit_anchor=view.authority_commit_anchor,
        coordinator_id=coordinator.coordinator_id, journal_root_fingerprint=H,
        old_worker_id="WORKER-1", old_worker_boot_id="BOOT-1",
        old_worker_pid=123, old_worker_start_time_ns=1,
        old_broker_generation_id=0, old_worker_generation_id=1,
        attestor_type="TERMINAL_PARENT_GUARDIAN_V13",
        attestor_id="GUARDIAN-1", attestor_executable_sha256=H,
        collector_id="COLLECTOR-1", source_evidence_id="EVIDENCE-1",
        source_evidence_sha256=H2, observed_at_utc=UTC,
        death_evidence_kind="PIDFD_EXIT_AND_REAP_ATTESTATION",
        observed_pidfd_id="PIDFD-1", pidfd_exit_observed=True,
        waitid_reaped=True, death_exit_status_class="EXITED",
        reap_evidence_fingerprint=H, death_observation_sequence=1,
        worker_append_handle_closed=True, surviving_writer_holder_count=0,
        append_handle_inventory_fingerprint=H2,
    )
    return _restart_authorization(
        coordinator, ledger, fixture, "RECONCILE_TERMINAL_GAP"
    ), anchor, proof, open_event_id, open_record


class I6ArtifactContractTests(unittest.TestCase):
    def test_fixed_canonical_ids_fingerprints_and_complete_bytes(self) -> None:
        snapshot, anchor, proof, observation = _legacy_snapshot(), _anchor(), _proof(), _observation()
        report = build_monitoring_report(**_report_kwargs(observation))
        expected = (
            (snapshot.legacy_safety_snapshot_id, "IU4-LEGACY-SAFETY-SNAPSHOT-V1-a7fa73618fdafe0542ac15da62667c585f60a0bca887d24e5f8090c749d8e2ee"),
            (snapshot.snapshot_fingerprint, "8b4431737ba7f9dc2627f35aaee7326e5b433f86b7065ed39b6c70e130135257"),
            (anchor.trust_anchor_id, "IU4-PERSISTENCE-WORKER-DEATH-TRUST-ANCHOR-V1-f26bcfab8f4840dc8e8a6fd42ff212e2886308ed81c261ad8aa0af6b17b45a53"),
            (anchor.trust_anchor_fingerprint, "26780ee1d2dab5311e437e4da32e22a56fac26afec10c16b1aefbda033bf7619"),
            (proof.worker_exclusion_proof_id, "IU4-PERSISTENCE-WORKER-EXCLUSION-PROOF-V1-6f3014e7b038b3d3efd43a49bcb8f2152bde91d22ba83f09f7e24264625e3bda"),
            (proof.proof_fingerprint, "6073ff2e953bd69d6ecefa9417e7b1b2fbb7e204474727383405b6911cadffb2"),
            (observation.terminal_monitoring_observation_id, "IU4-TERMINAL-MONITORING-OBSERVATION-V1-ee0d7980d53b02d5a8f24825dde64543e8cf8adc7f4ef753eaa2f5549ef1c64f"),
            (observation.observation_fingerprint, "a151ff36e360960b4c8483dff1827e616e04055860e4bfbc34ef583117495bb6"),
            (report.monitoring_report_id, "IU4-RECOVERY-MONITORING-REPORT-V1-cb3967b402d1e5c13ef18a3964112d420c9ac3b6f85953c0bf321171ce25665b"),
            (report.report_fingerprint, "94e9d0e5526b0e46442ea361cae623d38f25918d14be715a41a9573d18e52462"),
        )
        for actual, wanted in expected:
            self.assertEqual(actual, wanted)
        self.assertEqual(
            terminal_static_bindings_fingerprint(observation),
            "842946705cc9fca3cb2b83beddd819ff48ea95cec6fecef153eb052e6e69285c",
        )
        self.assertEqual(len(canonical_json_bytes(observation.to_record())), 13704)
        self.assertEqual(len(canonical_json_bytes(report.to_record())), 18600)

    def test_legacy_risk_roundtrip_and_exact_types(self) -> None:
        risk = _risk()
        self.assertEqual(LegacyRiskStateS4ProjectionV1.from_record(risk.to_record()), risk)
        for bad in ({**risk.to_record(), "extra": 1}, {**risk.to_record(), "trades_today": True}):
            with self.assertRaises(ValueError):
                LegacyRiskStateS4ProjectionV1.from_record(bad)

    def test_legacy_snapshot_rejects_flat_timestamp_and_untyped_throttle_event(self) -> None:
        snapshot = _legacy_snapshot()
        position = deepcopy(snapshot.position_record)
        position["entry_timestamp_utc"] = UTC
        with self.assertRaises(IU4RecoveryProjectionError):
            _rebuild_artifact(
                snapshot,
                position_record=position,
                position_fingerprint=_fp(position),
            )

        throttle = deepcopy(snapshot.throttle_record)
        throttle["recent_entry_events"] = [{"unexpected": "accepted"}]
        payload = dict(throttle)
        payload.pop("state_fingerprint")
        throttle["state_fingerprint"] = _fp(payload)
        with self.assertRaises(IU4RecoveryProjectionError):
            _rebuild_artifact(
                snapshot,
                throttle_record=throttle,
                throttle_fingerprint=throttle["state_fingerprint"],
            )

    def test_all_content_addressed_artifacts_reject_tamper(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests

        snapshot = _legacy_snapshot()
        handoff = IU4StateHandoffManifestV1.build(
            direction="LEGACY_TO_PEE", repository_commit="c" * 40,
            symbol="BTCUSDT", coordinator_id="COORD-1", system_state_id="STATE-1",
            source_state_path=snapshot.source_path, source_state_schema=1,
            source_state_bytes_sha256=H, source_state_fingerprint=H2,
            competing_state_path="/tmp/target", competing_state_schema=2,
            competing_state_bytes_sha256=H2, competing_state_fingerprint=H,
            source_safety_snapshot=snapshot.to_record(), target_business_fingerprint=H,
            target_core_fingerprint=H2, previous_owner_epoch=0, new_owner_epoch=1,
            source_authority_generation_id=snapshot.authority_generation_id,
            source_authority_commit_anchor=H,
            planned_authority_generation_id="GEN-2", mapping_record=handoff_mapping_record(
                direction="LEGACY_TO_PEE", source_snapshot=snapshot,
                target_business_fingerprint=H, target_core_fingerprint=H2,
            ),
            operator="OP", operation_timestamp_utc=UTC, approval_reference="APP",
            approval_fingerprint=H, operation_attempt_id="ATTEMPT-1",
        )
        fixture = AtomicV2Tests(methodName="test_progress_changes_only_cursor_and_bound_risk")
        fixture.setUp()
        coordinator = fixture._make_coordinator(fixture.temp / "artifact-genesis")
        genesis = _genesis_manifest(coordinator, fixture.initial_state, suffix="ARTIFACT")
        projection = IU4CompatibilityProjectionV1.build(
            projection_id_material="P-1", atomic_transaction_event_id="TX-1",
            atomic_transaction_fingerprint=H, atomic_transaction_sequence=1,
            atomic_journal_head=H2, atomic_state_fingerprint=H,
            authority_generation_id="GEN-1", authority_prepare_record_fingerprint=H2,
            projected_legacy_safety=snapshot.to_record(),
            source_path=snapshot.source_path,
            target_path="/tmp/projection",
            source_bytes_sha256=snapshot.source_bytes_sha256,
            target_bytes_sha256=_fp(snapshot.to_record()), projected_at_utc=UTC,
        )
        try:
            for value in (snapshot, handoff, genesis, projection, _anchor(), _proof()):
                record = value.to_record()
                parser = type(value).from_record
                self.assertEqual(parser(record), value)
                key = next(k for k in record if k not in {value.ID_FIELD, value.FINGERPRINT_FIELD, "schema_version", "artifact_type"})
                tampered = dict(record)
                tampered[key] = "TAMPER" if not isinstance(tampered[key], int) else tampered[key] + 1
                with self.assertRaises(IU4RecoveryProjectionError):
                    parser(tampered)
            with self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(snapshot, source_path="relative/source.json")
            bad_position = dict(snapshot.position_record)
            bad_position["entry_timestamp_utc"] = "NOT-A-TIME"
            with self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(
                    snapshot, position_record=bad_position,
                    position_fingerprint=_fp(bad_position),
                )
            with self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(_anchor(), approval_reference="")
            with self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(
                    handoff, mapping_record={"unexpected": "value"}
                )
            with self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(
                    projection, source_path="/tmp/unbound-source.json"
                )
            wrong_components = dict(genesis.component_fingerprints)
            wrong_components["position"] = "f" * 64
            if wrong_components["position"] == genesis.component_fingerprints["position"]:
                wrong_components["position"] = "e" * 64
            with self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(
                    genesis, component_fingerprints=wrong_components
                )
        finally:
            fixture.tearDown()

    def test_worker_death_proof_exact_trust_and_death_facts(self) -> None:
        anchor, proof = _anchor(), _proof()
        validate_worker_exclusion(
            anchor=anchor, proof=proof,
            expected_death_trust_anchor_id=anchor.trust_anchor_id,
            expected_death_trust_anchor_fingerprint=anchor.trust_anchor_fingerprint,
            expected_approval_fingerprint=H,
            expected_trusted_anchor_registry_fingerprint=H2,
            runtime_session_id="SESSION-1", runtime_session_open_event_id="OPEN-1",
            runtime_session_open_record_fingerprint=H,
            authority_generation_id="GEN-1", authority_commit_anchor=H2,
            coordinator_id="COORD-1", journal_root_fingerprint=H,
            old_worker_id="WORKER-1", old_worker_boot_id="BOOT-1",
        )
        for field, bad in (("waitid_reaped", False), ("worker_append_handle_closed", False),
                           ("surviving_writer_holder_count", 1), ("proof_mode", "HIGHER_DURABLE_FENCING_TOKEN")):
            record = proof.to_record(); record[field] = bad
            with self.assertRaises(IU4RecoveryProjectionError):
                IU4PersistenceWorkerExclusionProofV1.from_record(record)

    def test_worker_trust_binding_negative_matrix(self) -> None:
        anchor, proof = _anchor(), _proof()
        base = dict(
            anchor=anchor, proof=proof,
            expected_death_trust_anchor_id=anchor.trust_anchor_id,
            expected_death_trust_anchor_fingerprint=anchor.trust_anchor_fingerprint,
            expected_approval_fingerprint=H,
            expected_trusted_anchor_registry_fingerprint=H2,
            runtime_session_id="SESSION-1", runtime_session_open_event_id="OPEN-1",
            runtime_session_open_record_fingerprint=H,
            authority_generation_id="GEN-1", authority_commit_anchor=H2,
            coordinator_id="COORD-1", journal_root_fingerprint=H,
            old_worker_id="WORKER-1", old_worker_boot_id="BOOT-1",
        )
        for name in (
            "expected_death_trust_anchor_id", "expected_death_trust_anchor_fingerprint",
            "expected_approval_fingerprint", "expected_trusted_anchor_registry_fingerprint",
            "runtime_session_id", "runtime_session_open_event_id",
            "runtime_session_open_record_fingerprint",
            "authority_generation_id", "authority_commit_anchor", "coordinator_id",
            "journal_root_fingerprint", "old_worker_id", "old_worker_boot_id",
        ):
            bad = dict(base); bad[name] = H if name.endswith("fingerprint") else "DIFFERENT"
            if bad[name] == base[name]: bad[name] = H2
            with self.subTest(name=name), self.assertRaises(IU4RecoveryProjectionError):
                validate_worker_exclusion(**bad)

    def test_artifact_schema_unknown_missing_bool_and_noncanonical_decimal(self) -> None:
        snapshot = _legacy_snapshot()
        for mutation in (
            lambda r: r.pop("symbol"),
            lambda r: r.update({"unknown": 1}),
            lambda r: r.update({"schema_version": True}),
        ):
            record = snapshot.to_record(); mutation(record)
            with self.assertRaises(IU4RecoveryProjectionError):
                IU4LegacySafetySnapshotV1.from_record(record)
        record = _risk().to_record(); record["loss_today"] = "0.0"
        with self.assertRaises(ValueError):
            LegacyRiskStateS4ProjectionV1.from_record(record)

    def test_self_consistently_refingerprinted_incomplete_artifacts_reject(self) -> None:
        snapshot = _legacy_snapshot()
        values = snapshot.to_record()
        values["loss_cluster_record"] = {}
        material = {
            name: value for name, value in values.items()
            if name not in {
                "schema_version", "artifact_type", "legacy_safety_snapshot_id",
                "snapshot_fingerprint",
            }
        }
        with self.assertRaises(IU4RecoveryProjectionError):
            IU4LegacySafetySnapshotV1.build(**material)
        for field, nested in (
            ("loss_cluster_record", {**snapshot.loss_cluster_record, "revision": True}),
            ("throttle_record", {**snapshot.throttle_record, "entries_today": True}),
            ("progress_cursor_record", {**snapshot.progress_cursor_record, "tick_id": True}),
        ):
            with self.subTest(field=field), self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(snapshot, **{field: nested})

        observation = _observation()
        values = observation.to_record()
        values["role_readiness"]["parent_guardian_id"] = ""
        values["signal_envelope"]["signal_envelope_fingerprint"] = "NOT-A-SHA"
        material = {
            name: value for name, value in values.items()
            if name not in {
                "schema_version", "artifact_type",
                "terminal_monitoring_observation_id", "observation_fingerprint",
            }
        }
        with self.assertRaises(IU4RecoveryProjectionError):
            IU4TerminalMonitoringObservationV1.build(**material)

    def test_nonempty_throttle_day_must_equal_latest_retained_event_day(self) -> None:
        snapshot = _legacy_snapshot()
        event = {
            "schema_version": 1,
            "entry_sequence": 1,
            "entry_event_id": "ENTRY-1",
            "previous_entry_event_id": "",
            "entry_timestamp_utc": "2026-08-20T23:59:59Z",
            "policy_model_version": "PEE_RATE_V1",
            "policy_profile_id": "I6-THROTTLE",
            "policy_fingerprint": H,
        }
        throttle = {
            **snapshot.throttle_record,
            "entries_today": 0,
            "last_entry_event_id": "ENTRY-1",
            "last_entry_timestamp_utc": "2026-08-20T23:59:59Z",
            "last_update_event_id": "ENTRY-1",
            "recent_entry_events": [event],
            "total_accepted_entry_count": 1,
            "utc_day": "2026-08-21",
        }
        throttle.pop("state_fingerprint")
        throttle["state_fingerprint"] = _fp(throttle)
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            _rebuild_artifact(
                snapshot,
                throttle_record=throttle,
                throttle_fingerprint=throttle["state_fingerprint"],
            )
        self.assertEqual(
            caught.exception.reason_code, "PEE_IU4_HANDOFF_SAFETY_CONFLICT"
        )

    def test_owner_matrix(self) -> None:
        expected = {
            ("LEGACY", "OPEN", "FLAT"): "LEGACY_EXIT_ONLY",
            ("LEGACY", "OPEN", "OPEN"): "PEE_IU4_HANDOFF_DUAL_OPEN_CONFLICT",
            ("LEGACY", "FLAT", "FLAT"): "HANDOFF_REQUIRED",
            ("LEGACY", "FLAT", "OPEN"): "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID",
            ("PEE", "FLAT", "OPEN"): "PEE_RESUME_CANDIDATE",
            ("PEE", "FLAT", "FLAT"): "PEE_FLAT_CANDIDATE",
            ("PEE", "OPEN", "OPEN"): "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID",
            ("PEE", "OPEN", "FLAT"): "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID",
        }
        for row, result in expected.items():
            with self.subTest(row=row):
                self.assertEqual(classify_owner_state(*row), result)


class I6ProjectionAndStoreTests(unittest.TestCase):
    def test_projection_root_hash_fixed_domain(self) -> None:
        path = "/tmp/example/projection"
        expected = hashlib.sha256(b"IU4_PROJECTION_ROOT_V1\x00" + path.encode("utf-8")).hexdigest()
        self.assertEqual(projection_root_realpath_sha256(path), expected)

    def test_legacy_projection_store_create_read_replay_conflict(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iu4-i6-store-") as root:
            path = Path(root) / "legacy_projection.json"
            record = _legacy_snapshot().to_record()
            write_legacy_safety_projection(path, record)
            self.assertEqual(read_legacy_safety_projection(path), record)
            write_legacy_safety_projection(path, record)
            with self.assertRaises(ValueError):
                write_legacy_safety_projection(path, {**record, "symbol": "ETHUSDT"})

    def test_state_store_parent_cleanup_preserves_primary_and_attempts_every_descriptor(self) -> None:
        import live_l1.state.state_store as state_store

        original_close = state_store.os.close
        primary = IU4RecoveryProjectionError(
            "PEE_IU4_PROJECTION_LAG", "primary projection semantics"
        )
        cleanup_rows = (
            MemoryError("direct cleanup resource"),
            _nested_resource_error(OSError(errno.EIO, "nested cleanup resource")),
            RuntimeError("non-resource cleanup failure"),
        )
        for cleanup_error in cleanup_rows:
            with self.subTest(cleanup=type(cleanup_error).__name__), tempfile.TemporaryDirectory(
                prefix="iu4-i6-store-parent-cleanup-"
            ) as root:
                target = Path(root) / "parent" / "projection.json"
                target.parent.mkdir()
                attempted: list[int] = []
                failed: list[int] = []

                def close_with_failures(descriptor):
                    attempted.append(descriptor)
                    if len(attempted) in {1, 3}:
                        failed.append(descriptor)
                        raise cleanup_error
                    return original_close(descriptor)

                try:
                    with patch.object(
                        state_store._LegacyProjectionBoundary,
                        "revalidate",
                        side_effect=primary,
                    ), patch.object(
                        state_store.os, "close", side_effect=close_with_failures
                    ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                        IU4RecoveryOrchestratorV1._legacy_projection_read(
                            str(target), "parent cleanup classification"
                        )
                    self.assertIs(caught.exception, primary)
                    self.assertEqual(
                        caught.exception.reason_code, "PEE_IU4_PROJECTION_LAG"
                    )
                    self.assertGreaterEqual(len(attempted), 4)
                    self.assertEqual(len(attempted), len(set(attempted)))
                finally:
                    for descriptor in failed:
                        original_close(descriptor)

    def test_state_store_read_cleanup_classification_and_complete_cleanup_matrix(self) -> None:
        import live_l1.state.state_store as state_store

        original_close = state_store.os.close
        with tempfile.TemporaryDirectory(prefix="iu4-i6-store-cleanup-matrix-") as root:
            target = Path(root) / "parent" / "projection.json"
            target.parent.mkdir()
            record = _legacy_snapshot().to_record()
            write_legacy_safety_projection(target, record)
            rows = (
                (
                    "DIRECT_RESOURCE",
                    MemoryError("direct cleanup resource"),
                    IU4RecoveryProjectionError,
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                ),
                (
                    "NESTED_RESOURCE",
                    _nested_resource_error(OSError(errno.EMFILE, "nested cleanup resource")),
                    IU4RecoveryProjectionError,
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                ),
                (
                    "NON_RESOURCE",
                    RuntimeError("non-resource cleanup failure"),
                    ValueError,
                    None,
                ),
            )
            for label, cleanup_error, expected_type, expected_reason in rows:
                with self.subTest(label=label):
                    attempted: list[int] = []
                    failed: list[int] = []

                    def close_with_failures(descriptor):
                        attempted.append(descriptor)
                        if len(attempted) in {1, 3}:
                            failed.append(descriptor)
                            raise cleanup_error
                        return original_close(descriptor)

                    try:
                        with patch.object(
                            state_store.os, "close", side_effect=close_with_failures
                        ), self.assertRaises(expected_type) as caught:
                            IU4RecoveryOrchestratorV1._legacy_projection_read(
                                str(target), "read cleanup classification"
                            )
                        if expected_reason is not None:
                            self.assertEqual(
                                caught.exception.reason_code, expected_reason
                            )
                        self.assertGreaterEqual(len(attempted), 5)
                        self.assertEqual(len(attempted), len(set(attempted)))
                    finally:
                        for descriptor in failed:
                            original_close(descriptor)

    def test_state_store_target_primary_and_postterminal_write_cleanup_semantics(self) -> None:
        import live_l1.state.state_store as state_store

        original_close = state_store.os.close
        with tempfile.TemporaryDirectory(prefix="iu4-i6-store-target-cleanup-") as root:
            base = Path(root)
            existing = base / "existing" / "projection.json"
            existing.parent.mkdir()
            record = _legacy_snapshot().to_record()
            write_legacy_safety_projection(existing, record)
            primary = IU4RecoveryProjectionError(
                "PEE_IU4_PROJECTION_LAG", "primary target read semantics"
            )
            attempted: list[int] = []
            failed: list[int] = []

            def close_during_primary(descriptor):
                attempted.append(descriptor)
                if len(attempted) in {1, 3}:
                    failed.append(descriptor)
                    raise MemoryError("secondary target cleanup")
                return original_close(descriptor)

            try:
                with patch.object(
                    state_store.os, "read", side_effect=primary
                ), patch.object(
                    state_store.os, "close", side_effect=close_during_primary
                ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                    IU4RecoveryOrchestratorV1._legacy_projection_read(
                        str(existing), "target primary cleanup"
                    )
                self.assertIs(caught.exception, primary)
                self.assertEqual(
                    caught.exception.reason_code, "PEE_IU4_PROJECTION_LAG"
                )
                self.assertGreaterEqual(len(attempted), 5)
                self.assertEqual(len(attempted), len(set(attempted)))
            finally:
                for descriptor in failed:
                    original_close(descriptor)

            for nested in (False, True):
                target = base / f"write-{'nested' if nested else 'direct'}" / "projection.json"
                target.parent.mkdir()
                attempted = []
                failed = []
                resource = MemoryError("write cleanup resource")
                cleanup_error = (
                    _nested_resource_error(resource) if nested else resource
                )

                def close_after_write(descriptor):
                    attempted.append(descriptor)
                    if len(attempted) in {1, 3}:
                        failed.append(descriptor)
                        raise cleanup_error
                    return original_close(descriptor)

                try:
                    with patch.object(
                        state_store.os, "close", side_effect=close_after_write
                    ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                        IU4RecoveryOrchestratorV1._legacy_projection_write(
                            str(target), record, "postterminal write cleanup"
                        )
                    self.assertEqual(
                        caught.exception.reason_code,
                        "PEE_IU4_RESOURCE_EXHAUSTED",
                    )
                    self.assertGreaterEqual(len(attempted), 5)
                    self.assertEqual(len(attempted), len(set(attempted)))
                finally:
                    for descriptor in failed:
                        original_close(descriptor)
                IU4RecoveryOrchestratorV1._legacy_projection_write(
                    str(target), record, "postterminal write retry"
                )
                self.assertEqual(read_legacy_safety_projection(target), record)

    def test_legacy_projection_store_rejects_parent_symlink_before_creation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iu4-i6-store-link-") as root:
            base = Path(root)
            outside = base / "outside"
            outside.mkdir()
            linked_parent = base / "linked"
            linked_parent.symlink_to(outside, target_is_directory=True)
            target = linked_parent / "must-not-exist" / "projection.json"
            with self.assertRaises(ValueError):
                write_legacy_safety_projection(target, _legacy_snapshot().to_record())
            self.assertFalse((outside / "must-not-exist").exists())

            outside_file = outside / "existing.json"
            outside_file.write_bytes(
                json.dumps(
                    _legacy_snapshot().to_record(),
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("ascii") + b"\n"
            )
            with self.assertRaises(ValueError):
                read_legacy_safety_projection(linked_parent / "existing.json")

    def test_legacy_projection_fd_chain_rejects_root_or_parent_swap_at_readback(self) -> None:
        import live_l1.state.state_store as state_store

        for operation in ("WRITE_READBACK", "READ_RECONCILIATION"):
            for swap_level in ("ROOT", "PARENT"):
                with self.subTest(operation=operation, swap_level=swap_level), tempfile.TemporaryDirectory(
                    prefix="iu4-i6-store-race-"
                ) as temporary:
                    base = Path(temporary)
                    root = base / "root"
                    parent = root / "parent"
                    outside = base / "outside"
                    parent.mkdir(parents=True)
                    outside.mkdir()
                    target = parent / "legacy.json"
                    record = _legacy_snapshot().to_record()
                    if operation == "READ_RECONCILIATION":
                        write_legacy_safety_projection(target, record)
                    original_read = state_store._read_projection_bytes
                    read_count = 0
                    swapped = False
                    held = base / f"held-{swap_level.lower()}"

                    def swap_binding() -> None:
                        nonlocal swapped
                        if swapped:
                            return
                        victim = root if swap_level == "ROOT" else parent
                        victim.rename(held)
                        victim.symlink_to(outside, target_is_directory=True)
                        swapped = True

                    def read_with_race(directory_fd, basename, **kwargs):
                        nonlocal read_count
                        read_count += 1
                        trigger = (
                            2 if operation == "WRITE_READBACK" else 1
                        )
                        if read_count == trigger:
                            swap_binding()
                        return original_read(
                            directory_fd, basename, **kwargs
                        )

                    with patch.object(
                        state_store,
                        "_read_projection_bytes",
                        side_effect=read_with_race,
                    ), self.assertRaises(ValueError):
                        if operation == "WRITE_READBACK":
                            write_legacy_safety_projection(target, record)
                        else:
                            read_legacy_safety_projection(target)
                    self.assertTrue(swapped)
                    self.assertEqual(list(outside.rglob("*")), [])
                    hidden_target = (
                        held / "parent" / "legacy.json"
                        if swap_level == "ROOT"
                        else held / "legacy.json"
                    )
                    self.assertTrue(hidden_target.is_file())

    def test_legacy_projection_target_identity_is_bound_during_all_readbacks(self) -> None:
        import live_l1.state.state_store as state_store

        rows = (
            ("READ_DURING", "SAME_BYTES"),
            ("WRITE_READBACK", "SAME_BYTES"),
            ("READ_RECONCILIATION", "SIZE_MISMATCH"),
            ("READ_RECONCILIATION", "TYPE_MISMATCH"),
        )
        for phase, replacement_kind in rows:
            with self.subTest(phase=phase, replacement=replacement_kind), tempfile.TemporaryDirectory(
                prefix="iu4-i6-target-identity-"
            ) as temporary:
                root = Path(temporary)
                parent = root / "parent"
                outside = root / "outside"
                parent.mkdir()
                outside.mkdir()
                target = parent / "legacy.json"
                held = parent / "held-original.json"
                record = _legacy_snapshot().to_record()
                canonical = canonical_json_bytes(record) + b"\n"
                if phase != "WRITE_READBACK":
                    write_legacy_safety_projection(target, record)
                swapped = False

                def replace_target() -> None:
                    nonlocal swapped
                    if swapped:
                        return
                    target.rename(held)
                    if replacement_kind == "TYPE_MISMATCH":
                        target.mkdir()
                    elif replacement_kind == "SIZE_MISMATCH":
                        target.write_bytes(canonical[:-1])
                    else:
                        target.write_bytes(canonical)
                    swapped = True

                if phase == "WRITE_READBACK":
                    original_projection_read = state_store._read_projection_bytes
                    read_count = 0

                    def projection_read_with_replacement(
                        directory_fd, basename, **kwargs
                    ):
                        nonlocal read_count
                        read_count += 1
                        if read_count == 2:
                            replace_target()
                        return original_projection_read(
                            directory_fd, basename, **kwargs
                        )

                    context = patch.object(
                        state_store,
                        "_read_projection_bytes",
                        side_effect=projection_read_with_replacement,
                    )
                else:
                    original_read = state_store.os.read

                    def read_with_replacement(descriptor, size):
                        chunk = original_read(descriptor, size)
                        if chunk:
                            replace_target()
                        return chunk

                    context = patch.object(
                        state_store.os,
                        "read",
                        side_effect=read_with_replacement,
                    )

                with context, self.assertRaises(ValueError):
                    if phase == "WRITE_READBACK":
                        write_legacy_safety_projection(target, record)
                    else:
                        read_legacy_safety_projection(target)
                self.assertTrue(swapped)
                self.assertEqual(list(outside.iterdir()), [])
                self.assertTrue(held.is_file())

    def test_schema1_models_and_state_store_behavior_remain_unchanged(self) -> None:
        position = PositionStateS2("BTCUSDT", "FLAT", 0.0, None)
        risk = RiskStateS4("NONE", None)
        self.assertEqual((position.position, risk.kill_level), ("FLAT", "NONE"))
        with tempfile.TemporaryDirectory(prefix="iu4-i6-v1-store-") as root:
            state = load_or_init_state(root, "SYSTEM-V1")
            persist_state(root, state)
            loaded = load_or_init_state(root, "SYSTEM-V1")
            self.assertEqual(loaded.system_state_id, state.system_state_id)
            self.assertEqual(loaded.s2_position.position, "FLAT")

    def test_projection_cursor_base_and_contiguous_link(self) -> None:
        first = IU4ProjectionCursorV1.build(
            authority_generation_id="GEN-1", authority_prepare_record_fingerprint=H,
            projection_base_sequence=0, projection_base_journal_head=EMPTY,
            projection_base_state_fingerprint=H2, previous_atomic_transaction_sequence=0,
            previous_atomic_journal_head=EMPTY, previous_atomic_state_fingerprint=H2,
            atomic_transaction_event_id="TX-1", atomic_transaction_fingerprint=H,
            atomic_transaction_sequence=1, atomic_journal_head=H2,
            atomic_state_fingerprint=H, projection_id="PROJ-1",
            projection_fingerprint=H2, projection_output_bytes_sha256=H,
            previous_projection_cursor_id=NONE, previous_projection_cursor_fingerprint=NONE,
            published_at_utc=UTC, projection_root_inventory_fingerprint=H2,
        )
        self.assertEqual(IU4ProjectionCursorV1.from_record(first.to_record()), first)
        bad = first.to_record(); bad["atomic_transaction_sequence"] = 2
        with self.assertRaises(IU4RecoveryProjectionError):
            IU4ProjectionCursorV1.from_record(bad)

    def test_projection_publisher_output_cursor_replay_and_lag(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests
        from live_l1.state.paper_atomic_coordinator import AtomicProgressCursorV1

        fixture = AtomicV2Tests(methodName="test_progress_changes_only_cursor_and_bound_risk")
        fixture.setUp()
        try:
            transaction_root = fixture.temp / "projection-owner"
            transaction_root.mkdir()
            cursor = AtomicProgressCursorV1(
                schema_version=1, snapshot_id="I6-SNAPSHOT-1",
                timestamp_utc=UTC, tick_id=1, intent_id="I6-INTENT-1",
            )
            fixture.coordinator.commit_progress(
                progress_cursor=cursor, transaction_event_id="I6-PROGRESS-1"
            )
            transaction = fixture.coordinator._transactions()[0][1]
            publisher = IU4ProjectionPublisherV1(str(transaction_root))
            published = publisher.publish(
                transaction=transaction, projected_legacy_safety=_projection_snapshot(transaction),
                operation_attempt_id="I6-PROJECTION-ATTEMPT-1", published_at_utc=UTC,
            )
            self.assertEqual(published.atomic_transaction_sequence, 1)
            self.assertEqual(publisher.publish(
                transaction=transaction, projected_legacy_safety=_projection_snapshot(transaction),
                operation_attempt_id="I6-PROJECTION-ATTEMPT-REPLAY", published_at_utc=UTC,
            ), published)
            evil = publisher.records_root / "99999999999999999999_EVIL.json"
            evil.write_bytes(b"{}\n")
            with self.assertRaises(IU4RecoveryProjectionError):
                publisher.publish(
                    transaction=transaction,
                    projected_legacy_safety=_projection_snapshot(transaction),
                    operation_attempt_id="I6-PROJECTION-DIVERGENT-INVENTORY",
                    published_at_utc=UTC,
                )
            self.assertEqual(fixture.coordinator.load_state().state_fingerprint, transaction.state_after.state_fingerprint)
        finally:
            fixture.tearDown()

    def test_output_only_crash_advances_only_matching_cursor(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests
        from live_l1.state.paper_atomic_coordinator import AtomicProgressCursorV1

        fixture = AtomicV2Tests(methodName="test_progress_changes_only_cursor_and_bound_risk")
        fixture.setUp()
        try:
            root = fixture.temp / "output-crash-owner"; root.mkdir()
            fixture.coordinator.commit_progress(
                progress_cursor=AtomicProgressCursorV1(
                    schema_version=1, snapshot_id="I6-SNAPSHOT-CRASH",
                    timestamp_utc=UTC, tick_id=2, intent_id="I6-INTENT-CRASH",
                ), transaction_event_id="I6-PROGRESS-CRASH",
            )
            transaction = fixture.coordinator._transactions()[0][1]
            publisher = IU4ProjectionPublisherV1(str(root))
            with self.assertRaises(IU4RecoveryProjectionError):
                publisher.publish(
                    transaction=transaction, projected_legacy_safety=_projection_snapshot(transaction),
                    operation_attempt_id="I6-OUTPUT-CRASH", published_at_utc=UTC,
                    fault_point="AFTER_OUTPUT_READBACK",
                )
            self.assertIsNone(publisher.read_cursor())
            recovered = publisher.publish(
                transaction=transaction, projected_legacy_safety=_projection_snapshot(transaction),
                operation_attempt_id="I6-OUTPUT-RECOVER", published_at_utc=UTC,
            )
            self.assertEqual(recovered.atomic_transaction_sequence, 1)
        finally:
            fixture.tearDown()

    def test_atomic_genesis_prepare_target_commit_and_authority_ancestry(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests

        fixture = AtomicV2Tests(methodName="test_progress_changes_only_cursor_and_bound_risk")
        fixture.setUp()
        try:
            root = fixture.temp / "i6-genesis-atomic"
            coordinator = fixture._make_coordinator(root)
            ledger = IU4LifecycleLedgerV1(fixture.temp / "i6-genesis-ledger")
            manifest = _genesis_manifest(coordinator, fixture.initial_state)
            orchestrator = _orchestrator(ledger, coordinator)
            with self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(manifest, profile_bindings={})
            wrong_state = replace(fixture.initial_state, coordinator_id="WRONG-COORD")
            class WrongBindings:
                coordinator_id = "WRONG-COORD"
                state_path = coordinator.state_path
                transaction_directory = coordinator.transaction_directory
            wrong_manifest = _genesis_manifest(
                WrongBindings(), wrong_state, suffix="WRONG"
            )
            with self.assertRaises(IU4RecoveryProjectionError):
                orchestrator.atomic_genesis(
                    manifest=wrong_manifest,
                    target_state_template=fixture.initial_state,
                    prepare_event_id="I6-WRONG-GENESIS-PREPARE",
                    commit_event_id="I6-WRONG-GENESIS-COMMIT",
                )
            self.assertEqual(ledger.view().record_count, 0)
            self.assertFalse(coordinator.state_path.exists())
            result = orchestrator.atomic_genesis(
                manifest=manifest, target_state_template=fixture.initial_state,
                prepare_event_id="I6-GENESIS-PREPARE", commit_event_id="I6-GENESIS-COMMIT",
            )
            view = ledger.view()
            self.assertEqual(view.owner_epoch, 1)
            self.assertEqual(result.outcome, "GENESIS_COMPLETE_LOOP_NOT_AUTHORIZED")
            state = coordinator.load_state()
            self.assertEqual(coordinator.i6_validate_authority_root(
                committed_target_state_fingerprint=state.state_fingerprint,
                authority_generation_id=state.authority_generation_id,
                authority_prepare_record_fingerprint=state.authority_prepare_record_fingerprint,
            ), state)
            self.assertEqual(orchestrator.atomic_genesis(
                manifest=manifest, target_state_template=fixture.initial_state,
                prepare_event_id="I6-GENESIS-PREPARE", commit_event_id="I6-GENESIS-COMMIT",
            ), result)
        finally:
            fixture.tearDown()

    def test_projection_complete_fault_grid_recovers_one_cursor(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests
        from live_l1.state.paper_atomic_coordinator import AtomicProgressCursorV1

        points = (
            "BEFORE_OUTPUT_CREATE", "AFTER_OUTPUT_CREATE", "AFTER_OUTPUT_FILE_SYNC",
            "AFTER_OUTPUT_DIRECTORY_SYNC", "AFTER_OUTPUT_READBACK", "AFTER_INVENTORY",
            "AFTER_CURSOR_TEMP_CREATE", "AFTER_CURSOR_FILE_SYNC",
            "AFTER_CURSOR_REPLACE", "AFTER_CURSOR_DIRECTORY_SYNC", "AFTER_CURSOR_READBACK",
        )
        for index, point in enumerate(points, 1):
            fixture = AtomicV2Tests(methodName="test_progress_changes_only_cursor_and_bound_risk")
            fixture.setUp()
            try:
                root = fixture.temp / f"fault-owner-{index}"; root.mkdir()
                fixture.coordinator.commit_progress(
                    progress_cursor=AtomicProgressCursorV1(
                        schema_version=1, snapshot_id=f"I6-SNAPSHOT-F-{index}",
                        timestamp_utc=UTC, tick_id=index, intent_id=f"I6-INTENT-F-{index}",
                    ), transaction_event_id=f"I6-PROGRESS-F-{index}",
                )
                transaction = fixture.coordinator._transactions()[0][1]
                publisher = IU4ProjectionPublisherV1(str(root))
                with self.subTest(point=point), self.assertRaises(IU4RecoveryProjectionError):
                    publisher.publish(
                        transaction=transaction, projected_legacy_safety=_projection_snapshot(transaction),
                        operation_attempt_id=f"I6-FAULT-{index}", published_at_utc=UTC,
                        fault_point=point,
                    )
                recovered = publisher.publish(
                    transaction=transaction, projected_legacy_safety=_projection_snapshot(transaction),
                    operation_attempt_id=f"I6-FAULT-{index}", published_at_utc=UTC,
                )
                self.assertEqual(recovered.atomic_transaction_sequence, 1)
                self.assertEqual(len(list(publisher.records_root.glob("*.json"))), 1)
                self.assertEqual(publisher.read_cursor(), recovered)
            finally:
                fixture.tearDown()

    def test_projection_root_spelling_symlink_and_cursor_without_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iu4-i6-roots-") as root:
            canonical = str(Path(root).resolve())
            for value in (canonical + "/", canonical + "//x", canonical + "/./x", "/"):
                with self.subTest(value=value), self.assertRaises(IU4RecoveryProjectionError):
                    IU4ProjectionPublisherV1(value)
            target = Path(root) / "target"; target.mkdir()
            link = Path(root) / "link"; link.symlink_to(target, target_is_directory=True)
            with self.assertRaises(IU4RecoveryProjectionError):
                IU4ProjectionPublisherV1(str(link))
            caller = Path(root) / "caller"; caller.mkdir()
            outside = Path(root) / "outside"; outside.mkdir()
            (caller / "projection").symlink_to(outside, target_is_directory=True)
            publisher = IU4ProjectionPublisherV1(str(caller))
            with self.assertRaises(IU4RecoveryProjectionError):
                publisher.initialize()
            self.assertFalse((outside / "records").exists())

    def test_inventory_bytes_use_projection_relative_sorted_entries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iu4-i6-inventory-") as root:
            publisher = IU4ProjectionPublisherV1(str(Path(root).resolve()))
            publisher.initialize()
            for sequence in (2, 1):
                projection = IU4CompatibilityProjectionV1.build(
                    projection_id_material=f"P-{sequence}",
                    atomic_transaction_event_id=f"TX-{sequence}",
                    atomic_transaction_fingerprint=H,
                    atomic_transaction_sequence=sequence,
                    atomic_journal_head=H2,
                    atomic_state_fingerprint=H,
                    authority_generation_id="GEN-1",
                    authority_prepare_record_fingerprint=H2,
                    projected_legacy_safety=_legacy_snapshot().to_record(),
                    source_path="/tmp/source.json",
                    target_path="/tmp/projection",
                    source_bytes_sha256=H,
                    target_bytes_sha256=_fp(_legacy_snapshot().to_record()),
                    projected_at_utc=UTC,
                )
                path = publisher.records_root / (
                    f"{sequence:020d}_{projection.projection_id}.json"
                )
                path.write_bytes(canonical_json_bytes(projection.to_record()) + b"\n")
                path.chmod(0o600)
            value, fingerprint = publisher._inventory("ATTEMPT-1")
            self.assertEqual(
                [row[0][:29] for row in value["entries"]],
                ["records/00000000000000000001_", "records/00000000000000000002_"],
            )
            self.assertNotIn("projection/records", canonical_json_bytes(value).decode("ascii"))
            self.assertEqual(fingerprint, hashlib.sha256(canonical_json_bytes(value)).hexdigest())

    def test_projection_resource_classification_disk_permission_fd_memory(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests
        from live_l1.state.paper_atomic_coordinator import AtomicProgressCursorV1

        fixture = AtomicV2Tests(methodName="test_progress_changes_only_cursor_and_bound_risk")
        fixture.setUp()
        try:
            root = fixture.temp / "resource-owner"; root.mkdir()
            fixture.coordinator.commit_progress(
                progress_cursor=AtomicProgressCursorV1(
                    schema_version=1, snapshot_id="RESOURCE-S", timestamp_utc=UTC,
                    tick_id=1, intent_id="RESOURCE-I",
                ), transaction_event_id="RESOURCE-TX",
            )
            transaction = fixture.coordinator._transactions()[0][1]
            publisher = IU4ProjectionPublisherV1(str(root))
            for failure in (
                OSError(errno.ENOSPC, "disk full"), OSError(errno.EACCES, "permission"),
                OSError(errno.EMFILE, "fd exhausted"), MemoryError("memory exhausted"),
                _runtime_resource_error(OSError(errno.EIO, "nested I/O")),
                _runtime_resource_error(MemoryError("nested memory")),
            ):
                with self.subTest(failure=type(failure).__name__), patch(
                    "live_l1.state.paper_iu4_recovery_projection.os.open", side_effect=failure
                ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                    publisher.publish(
                        transaction=transaction, projected_legacy_safety=_projection_snapshot(transaction),
                        operation_attempt_id="RESOURCE", published_at_utc=UTC,
                    )
                self.assertEqual(caught.exception.reason_code, "PEE_IU4_RESOURCE_EXHAUSTED")
        finally:
            fixture.tearDown()

    def test_projection_read_inventory_cursor_and_cleanup_resource_matrix(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iu4-i6-resource-matrix-") as root:
            publisher = IU4ProjectionPublisherV1(str(Path(root).resolve()))
            publisher.initialize()
            publisher.cursor_path.write_bytes(b"{}\n")

            def inventory_bytes() -> dict[str, bytes]:
                return {
                    str(path.relative_to(root)): path.read_bytes()
                    for path in Path(root).rglob("*") if path.is_file()
                }

            baseline = inventory_bytes()
            for failure in (
                OSError(errno.EIO, "direct Cursor read failure"),
                _nested_resource_error(MemoryError("nested Cursor read failure")),
            ):
                with self.subTest(boundary="CURSOR_READ", failure=type(failure).__name__), patch(
                    "live_l1.state.paper_iu4_recovery_projection.os.read",
                    side_effect=failure,
                ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                    publisher.read_cursor()
                self.assertEqual(
                    caught.exception.reason_code,
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                )
                self.assertEqual(inventory_bytes(), baseline)

            for failure in (
                OSError(errno.EMFILE, "direct inventory failure"),
                _nested_resource_error(MemoryError("nested inventory failure")),
            ):
                with self.subTest(boundary="INVENTORY", failure=type(failure).__name__), patch(
                    "live_l1.state.paper_iu4_recovery_projection.os.listdir",
                    side_effect=failure,
                ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                    publisher._inventory("RESOURCE-MATRIX")
                self.assertEqual(
                    caught.exception.reason_code,
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                )
                self.assertEqual(inventory_bytes(), baseline)

            original_close = os.close
            for nested in (False, True):
                state = {"count": 0, "failed_fd": None}

                def close_inventory_fault(descriptor):
                    state["count"] += 1
                    if state["count"] == 1:
                        state["failed_fd"] = descriptor
                        failure = OSError(errno.EIO, "inventory close failure")
                        raise (
                            _nested_resource_error(failure)
                            if nested else failure
                        )
                    return original_close(descriptor)

                try:
                    with self.subTest(boundary="INVENTORY_CLOSE", nested=nested), patch(
                        "live_l1.state.paper_iu4_recovery_projection.os.close",
                        side_effect=close_inventory_fault,
                    ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                        publisher._inventory("RESOURCE-CLOSE")
                    self.assertEqual(
                        caught.exception.reason_code,
                        "PEE_IU4_RESOURCE_EXHAUSTED",
                    )
                finally:
                    if state["failed_fd"] is not None:
                        original_close(state["failed_fd"])
                self.assertEqual(inventory_bytes(), baseline)

            close_state = {"count": 0, "failed_fd": None}

            def close_after_primary(descriptor):
                close_state["count"] += 1
                if close_state["count"] == 2:
                    close_state["failed_fd"] = descriptor
                    raise _nested_resource_error(
                        OSError(errno.EIO, "secondary Cursor directory close")
                    )
                return original_close(descriptor)

            try:
                with patch(
                    "live_l1.state.paper_iu4_recovery_projection.os.close",
                    side_effect=close_after_primary,
                ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                    publisher.read_cursor()
                self.assertEqual(
                    caught.exception.reason_code, "PEE_IU4_PROJECTION_LAG"
                )
            finally:
                if close_state["failed_fd"] is not None:
                    original_close(close_state["failed_fd"])
            self.assertEqual(inventory_bytes(), baseline)

    def test_projection_directory_fd_confinement_across_mkdir_open_replace_races(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests
        from live_l1.state.paper_atomic_coordinator import AtomicProgressCursorV1

        for race_point in ("MKDIR", "OPEN", "REPLACE"):
            fixture = AtomicV2Tests(
                methodName="test_progress_changes_only_cursor_and_bound_risk"
            )
            fixture.setUp()
            try:
                parent = fixture.temp / f"race-parent-{race_point.lower()}"
                caller = parent / "caller"
                outside = fixture.temp / f"outside-{race_point.lower()}"
                parent.mkdir(); caller.mkdir(); outside.mkdir()
                fixture.coordinator.commit_progress(
                    progress_cursor=AtomicProgressCursorV1(
                        schema_version=1,
                        snapshot_id=f"RACE-{race_point}-SNAPSHOT",
                        timestamp_utc=UTC, tick_id=1,
                        intent_id=f"RACE-{race_point}-INTENT",
                    ),
                    transaction_event_id=f"RACE-{race_point}-TX",
                )
                transaction = fixture.coordinator._transactions()[0][1]
                publisher = IU4ProjectionPublisherV1(str(caller))
                held_parent = fixture.temp / f"held-parent-{race_point.lower()}"
                swapped = False

                def swap_parent() -> None:
                    nonlocal swapped
                    if swapped:
                        return
                    parent.rename(held_parent)
                    parent.symlink_to(outside, target_is_directory=True)
                    swapped = True

                if race_point == "MKDIR":
                    original = os.mkdir

                    def mkdir_race(path, mode=0o777, *, dir_fd=None):
                        if path == "projection" and dir_fd is not None:
                            swap_parent()
                        return original(path, mode=mode, dir_fd=dir_fd)

                    context = patch(
                        "live_l1.state.paper_iu4_recovery_projection.os.mkdir",
                        side_effect=mkdir_race,
                    )
                elif race_point == "OPEN":
                    original = os.open

                    def open_race(path, flags, mode=0o777, *, dir_fd=None):
                        if (
                            path == ".projection_v1.lock"
                            and dir_fd is not None and not swapped
                        ):
                            swap_parent()
                        return original(path, flags, mode, dir_fd=dir_fd)

                    context = patch(
                        "live_l1.state.paper_iu4_recovery_projection.os.open",
                        side_effect=open_race,
                    )
                else:
                    original = os.replace

                    def replace_race(
                        src, dst, *, src_dir_fd=None, dst_dir_fd=None
                    ):
                        self.assertIsNotNone(src_dir_fd)
                        self.assertIsNotNone(dst_dir_fd)
                        swap_parent()
                        return original(
                            src, dst, src_dir_fd=src_dir_fd,
                            dst_dir_fd=dst_dir_fd,
                        )

                    context = patch(
                        "live_l1.state.paper_iu4_recovery_projection.os.replace",
                        side_effect=replace_race,
                    )

                with context:
                    if race_point == "MKDIR":
                        publisher.initialize()
                    else:
                        publisher.publish(
                            transaction=transaction,
                            projected_legacy_safety=_projection_snapshot(transaction),
                            operation_attempt_id=f"RACE-{race_point}",
                            published_at_utc=UTC,
                        )
                self.assertTrue(swapped)
                self.assertEqual(list(outside.rglob("*")), [])
                held_projection = held_parent / "caller" / "projection"
                self.assertTrue(held_projection.is_dir())
                if race_point != "MKDIR":
                    self.assertEqual(
                        len(list((held_projection / "records").glob("*.json"))), 1
                    )
                    self.assertTrue(
                        (held_projection / "projection_cursor_v1.json").is_file()
                    )
            finally:
                fixture.tearDown()

    def test_projection_lock_cleanup_resource_errors_preserve_durable_record_cursor(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests
        from live_l1.state.paper_atomic_coordinator import AtomicProgressCursorV1

        for cleanup_kind in ("UNLOCK", "CLOSE"):
            for nested in (False, True):
                self._assert_projection_cleanup_resource_boundary(
                    AtomicV2Tests, AtomicProgressCursorV1,
                    cleanup_kind=cleanup_kind, nested=nested,
                )

    def _assert_projection_cleanup_resource_boundary(
        self, AtomicV2Tests, AtomicProgressCursorV1, *,
        cleanup_kind: str, nested: bool,
    ) -> None:
            fixture = AtomicV2Tests(
                methodName="test_progress_changes_only_cursor_and_bound_risk"
            )
            fixture.setUp()
            leaked_lock_fd = None
            try:
                label = f"{cleanup_kind}-{'NESTED' if nested else 'DIRECT'}"
                root = fixture.temp / f"cleanup-{label.lower()}"
                root.mkdir()
                fixture.coordinator.commit_progress(
                    progress_cursor=AtomicProgressCursorV1(
                        schema_version=1,
                        snapshot_id=f"CLEANUP-{label}-SNAPSHOT",
                        timestamp_utc=UTC, tick_id=1,
                        intent_id=f"CLEANUP-{label}-INTENT",
                    ),
                    transaction_event_id=f"CLEANUP-{label}-TX",
                )
                transaction = fixture.coordinator._transactions()[0][1]
                publisher = IU4ProjectionPublisherV1(str(root))
                original_flock = __import__("fcntl").flock
                original_close = os.close
                lock_state = {"fd": None, "failed": False}

                def flock_fault(fd, operation):
                    if operation == __import__("fcntl").LOCK_EX:
                        lock_state["fd"] = fd
                    if (
                        cleanup_kind == "UNLOCK"
                        and operation == __import__("fcntl").LOCK_UN
                        and not lock_state["failed"]
                    ):
                        lock_state["failed"] = True
                        failure = OSError(errno.EIO, "synthetic unlock failure")
                        raise (
                            _runtime_resource_error(failure)
                            if nested else failure
                        )
                    return original_flock(fd, operation)

                def close_fault(fd):
                    if (
                        cleanup_kind == "CLOSE"
                        and fd == lock_state["fd"]
                        and not lock_state["failed"]
                    ):
                        lock_state["failed"] = True
                        failure = MemoryError(
                            "synthetic lock close exhaustion"
                        )
                        raise (
                            _nested_resource_error(failure)
                            if nested else failure
                        )
                    return original_close(fd)

                with patch(
                    "live_l1.state.paper_iu4_recovery_projection.fcntl.flock",
                    side_effect=flock_fault,
                ), patch(
                    "live_l1.state.paper_iu4_recovery_projection.os.close",
                    side_effect=close_fault,
                ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                    publisher.publish(
                        transaction=transaction,
                        projected_legacy_safety=_projection_snapshot(transaction),
                        operation_attempt_id=f"CLEANUP-{label}",
                        published_at_utc=UTC,
                    )
                self.assertEqual(
                    caught.exception.reason_code, "PEE_IU4_RESOURCE_EXHAUSTED"
                )
                leaked_lock_fd = lock_state["fd"] if cleanup_kind == "CLOSE" else None
                if leaked_lock_fd is not None:
                    original_close(leaked_lock_fd)
                    leaked_lock_fd = None
                durable_cursor = publisher.read_cursor()
                self.assertIsNotNone(durable_cursor)
                self.assertEqual(len(list(publisher.records_root.glob("*.json"))), 1)
                replay = publisher.publish(
                    transaction=transaction,
                    projected_legacy_safety=_projection_snapshot(transaction),
                    operation_attempt_id=f"CLEANUP-{label}-REPLAY",
                    published_at_utc=UTC,
                )
                self.assertEqual(replay, durable_cursor)
                self.assertEqual(len(list(publisher.records_root.glob("*.json"))), 1)
            finally:
                if leaked_lock_fd is not None:
                    try:
                        os.close(leaked_lock_fd)
                    except OSError:
                        pass
                fixture.tearDown()

    def test_projection_initialize_nested_close_resource_is_stable(self) -> None:
        for nested in (False, True):
            with self.subTest(nested=nested), tempfile.TemporaryDirectory(
                prefix="iu4-i6-init-cleanup-"
            ) as root:
                publisher = IU4ProjectionPublisherV1(root)
                original_close = os.close
                state = {"failed": False, "fd": None}

                def close_fault(descriptor):
                    if not state["failed"]:
                        state["failed"] = True
                        state["fd"] = descriptor
                        failure = OSError(
                            errno.EMFILE, "initialize close failure"
                        )
                        raise (
                            _runtime_resource_error(failure)
                            if nested else failure
                        )
                    return original_close(descriptor)

                try:
                    with patch(
                        "live_l1.state.paper_iu4_recovery_projection.os.close",
                        side_effect=close_fault,
                    ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                        publisher.initialize()
                    self.assertEqual(
                        caught.exception.reason_code,
                        "PEE_IU4_RESOURCE_EXHAUSTED",
                    )
                    self.assertTrue(
                        (Path(root) / "projection" / "records").is_dir()
                    )
                finally:
                    if state["fd"] is not None:
                        try:
                            original_close(state["fd"])
                        except OSError:
                            pass

    def test_projection_requires_one_by_one_catchup_and_rejects_cursor_without_output(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests
        from live_l1.state.paper_atomic_coordinator import AtomicProgressCursorV1

        fixture = AtomicV2Tests(methodName="test_progress_changes_only_cursor_and_bound_risk")
        fixture.setUp()
        try:
            root = fixture.temp / "catchup-owner"; root.mkdir()
            for index in (1, 2):
                fixture.coordinator.commit_progress(
                    progress_cursor=AtomicProgressCursorV1(
                        schema_version=1, snapshot_id=f"I6-CATCHUP-S-{index}",
                        timestamp_utc=f"2026-08-21T12:00:0{index}Z", tick_id=index,
                        intent_id=f"I6-CATCHUP-I-{index}",
                    ), transaction_event_id=f"I6-CATCHUP-TX-{index}",
                )
            transactions = [item[1] for item in fixture.coordinator._transactions()]
            publisher = IU4ProjectionPublisherV1(str(root))
            with self.assertRaises(IU4RecoveryProjectionError):
                publisher.publish(
                    transaction=transactions[1], projected_legacy_safety=_projection_snapshot(transactions[1]),
                    operation_attempt_id="SKIP-FIRST", published_at_utc=UTC,
                )
            first = publisher.publish(
                transaction=transactions[0], projected_legacy_safety=_projection_snapshot(transactions[0]),
                operation_attempt_id="CATCHUP-1", published_at_utc=UTC,
            )
            second = publisher.publish(
                transaction=transactions[1], projected_legacy_safety=_projection_snapshot(transactions[1]),
                operation_attempt_id="CATCHUP-2", published_at_utc=UTC,
            )
            self.assertEqual(second.atomic_transaction_sequence, first.atomic_transaction_sequence + 1)
            output = next(publisher.records_root.glob(f"{second.atomic_transaction_sequence:020d}_{second.projection_id}.json"))
            output.unlink()
            with self.assertRaises(IU4RecoveryProjectionError):
                publisher.publish(
                    transaction=transactions[1], projected_legacy_safety=_projection_snapshot(transactions[1]),
                    operation_attempt_id="CATCHUP-REPLAY", published_at_utc=UTC,
                )
        finally:
            fixture.tearDown()


class I6MonitoringTests(unittest.TestCase):
    def test_observation_and_report_are_strict_and_derived(self) -> None:
        observation = IU4TerminalMonitoringObservationV1.build_minimal_pass(
            runtime_session_id="SESSION-1", runtime_session_open_record_fingerprint=H,
            authority_generation_id="GEN-1", authority_commit_anchor=H2,
            atomic_root_fingerprint=H, source_collector_id="COLLECTOR-1",
            source_evidence_id="EVIDENCE-1", source_evidence_sha256=H2,
            observation_sequence=1, observed_at_utc=UTC,
        )
        report = build_monitoring_report(
            observation=observation, owner_epoch="PEE", report_operation="MONITOR_ONLY",
            expected_runtime_session_id="SESSION-1",
            expected_runtime_session_open_record_fingerprint=H,
            expected_authority_generation_id="GEN-1",
            expected_authority_commit_anchor=H2,
            expected_atomic_root_fingerprint=H,
            lifecycle_root_inventory_fingerprint=H,
            atomic_root_inventory_fingerprint=H2,
            projection_root_inventory_fingerprint=H,
            authorization_valid=True, runtime_profile_id="RP",
            economics_profile_id="EP", economics_profile_fingerprint=H2,
            entry_throttle_profile_id="TP", entry_throttle_profile_fingerprint=H,
            runtime_control_fingerprint=H2, lifecycle_ledger_tip_event_id="LEDGER-1",
            lifecycle_ledger_tip_fingerprint=H, open_prepare_count=0,
            runtime_session_status="OPEN_CLEAN", handoff_or_genesis_manifest_id="MANIFEST-1",
            handoff_or_genesis_manifest_fingerprint=H2, atomic_journal_sequence=0,
            atomic_journal_head=EMPTY, atomic_snapshot_fingerprint=H,
            authority_root_ancestry_result="PASS", projection_cursor_id=NONE,
            projection_cursor_fingerprint=NONE, projection_cursor_sequence=0,
            projection_cursor_journal_head=EMPTY, component_fingerprints={
                "s2": H, "account": H2, "throttle": H, "loss_cluster": H2,
                "s4": H, "entry_quote": H2, "progress_cursor": H,
            }, terminal_gap_status="NONE", reported_at_utc=UTC,
        )
        self.assertIsInstance(report, IU4RecoveryMonitoringReportV1)
        self.assertEqual(report.overall_result, "PASS")
        self.assertEqual(len(report.group_results()), 12)
        self.assertEqual(IU4RecoveryMonitoringReportV1.from_record(report.to_record()), report)

    def test_monitoring_rejects_caller_selected_trust_and_reason_codes(self) -> None:
        base = _observation()
        committed_without_evidence = _rebuild_observation(
            base,
            "runtime_close_fsm",
            channel_phase="RELEASED",
            close_fsm_phase="COMMITTED",
        )
        report = build_monitoring_report(
            **_report_kwargs(committed_without_evidence)
        )
        self.assertEqual(report.runtime_close_fsm_result, "FAIL")
        self.assertEqual(report.overall_result, "FAIL")

        forged_control = _rebuild_observation(
            base,
            "control_word_and_memfd",
            memfd_create_flags=["MFD_ALLOW_SEALING"],
        )
        forged_kwargs = _report_kwargs(forged_control)
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            build_monitoring_report(**forged_kwargs)
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        forged_channels = deepcopy(base.runtime_channels)
        forged_channels["channel_records"][0]["receiver_tid"] = 999
        refingerprinted = _rebuild_observation(
            base, "runtime_channels", **forged_channels
        )
        refingerprinted_kwargs = _report_kwargs(refingerprinted)
        refingerprinted_static = terminal_static_bindings_fingerprint(
            refingerprinted
        )
        self.assertNotEqual(
            refingerprinted_static,
            _trusted_profile_registry().resolve("RP").terminal_static_bindings_fingerprint,
        )
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            build_monitoring_report(**refingerprinted_kwargs)
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        passing = build_monitoring_report(**_report_kwargs(base))
        with self.assertRaises(IU4RecoveryProjectionError):
            _rebuild_artifact(passing, reason_codes=("ARBITRARY_REASON",))
        with self.assertRaises(IU4RecoveryProjectionError):
            _rebuild_artifact(
                passing,
                runtime_close_fsm_reason_code=(
                    "PEE_IU4_RUNTIME_SESSION_CLOSE_TIMEOUT"
                ),
            )

    def test_profile_registry_is_exact_content_addressed_and_prebound(self) -> None:
        trusted_registry = _trusted_profile_registry()
        base = _observation()
        forged_channels = deepcopy(base.runtime_channels)
        forged_channels["channel_records"][0]["receiver_tid"] = 777
        forged = _rebuild_observation(base, "runtime_channels", **forged_channels)
        forged_static_fingerprint = terminal_static_bindings_fingerprint(forged)
        self.assertNotEqual(
            forged_static_fingerprint,
            trusted_registry.resolve("RP").terminal_static_bindings_fingerprint,
        )
        kwargs = _report_kwargs(forged)
        kwargs["untrusted_profile_registry"] = trusted_registry
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            build_monitoring_report(**kwargs)
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        divergent_a = IU4TerminalRuntimeProfileAnchorV1.build(
            runtime_profile_id="DUPLICATE-PROFILE",
            terminal_static_bindings_fingerprint=H,
        )
        divergent_b = IU4TerminalRuntimeProfileAnchorV1.build(
            runtime_profile_id="DUPLICATE-PROFILE",
            terminal_static_bindings_fingerprint=H2,
        )
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            IU4TerminalRuntimeProfileRegistryV1.from_anchors(
                (divergent_a, divergent_b)
            )
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        class RegistrySubclass(IU4TerminalRuntimeProfileRegistryV1):
            pass

        class AnchorSubclass(IU4TerminalRuntimeProfileAnchorV1):
            pass

        class RegistryLookalike:
            def resolve(self, _runtime_profile_id):
                return trusted_registry.resolve("RP")

        class StringSubclass(str):
            pass

        strict_rows = (
            {"RP": trusted_registry.resolve("RP")},
            RegistrySubclass.from_record(trusted_registry.to_record()),
            RegistryLookalike(),
        )
        for value in strict_rows:
            with self.subTest(value=type(value).__name__):
                rejected = _report_kwargs(base)
                rejected["untrusted_profile_registry"] = value
                with self.assertRaises(IU4RecoveryProjectionError) as caught:
                    build_monitoring_report(**rejected)
                self.assertEqual(
                    caught.exception.reason_code,
                    "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                )
        with self.assertRaises(IU4RecoveryProjectionError):
            IU4TerminalRuntimeProfileRegistryV1.from_anchors(
                (AnchorSubclass.from_record(divergent_a.to_record()),)
            )
        rejected = _report_kwargs(base)
        rejected["runtime_profile_id"] = StringSubclass("RP")
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            build_monitoring_report(**rejected)
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

    def test_profile_registry_is_deeply_immutable_and_revalidated_on_resolve(self) -> None:
        trusted = _trusted_profile_registry()
        self.assertIs(
            type(trusted.profile_anchors[0]),
            IU4TerminalRuntimeProfileAnchorV1,
        )
        with self.assertRaises(FrozenInstanceError):
            trusted.profile_anchors[0].runtime_profile_id = "MUTATED"
        with self.assertRaises(TypeError):
            trusted.profile_anchors[0]["runtime_profile_id"] = "MUTATED"

        detached = trusted.to_record()
        detached["profile_anchors"][0]["runtime_profile_id"] = "DETACHED"
        self.assertEqual(trusted.resolve("RP").runtime_profile_id, "RP")

        replacement = IU4TerminalRuntimeProfileAnchorV1.build(
            runtime_profile_id="RP",
            terminal_static_bindings_fingerprint=H2,
        )
        replaced_registry = IU4TerminalRuntimeProfileRegistryV1.from_record(
            trusted.to_record()
        )
        object.__setattr__(
            replaced_registry, "profile_anchors", (replacement,)
        )
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            replaced_registry.resolve("RP")
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        mutated_registry = IU4TerminalRuntimeProfileRegistryV1.from_record(
            trusted.to_record()
        )
        object.__setattr__(
            mutated_registry.profile_anchors[0],
            "terminal_static_bindings_fingerprint",
            H2,
        )
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            mutated_registry.resolve("RP")
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        class MappingSubclass(dict):
            pass

        with self.assertRaises(IU4RecoveryProjectionError):
            IU4TerminalRuntimeProfileRegistryV1.from_record(
                MappingSubclass(trusted.to_record())
            )
        inner_subclass = trusted.to_record()
        inner_subclass["profile_anchors"][0] = MappingSubclass(
            inner_subclass["profile_anchors"][0]
        )
        with self.assertRaises(IU4RecoveryProjectionError):
            IU4TerminalRuntimeProfileRegistryV1.from_record(inner_subclass)

    def test_report_build_constructor_and_from_record_require_provisioned_root(self) -> None:
        base = _observation()
        passing = build_monitoring_report(**_report_kwargs(base))
        self.assertEqual(
            IU4RecoveryMonitoringReportV1.from_record(passing.to_record()),
            passing,
        )

        forged_channels = deepcopy(base.runtime_channels)
        forged_channels["channel_records"][0]["receiver_tid"] = 4242
        forged_observation = _rebuild_observation(
            base, "runtime_channels", **forged_channels
        )
        forged_anchor = IU4TerminalRuntimeProfileAnchorV1.build(
            runtime_profile_id="RP",
            terminal_static_bindings_fingerprint=(
                terminal_static_bindings_fingerprint(forged_observation)
            ),
        )
        forged_registry = IU4TerminalRuntimeProfileRegistryV1.from_anchors(
            (forged_anchor,)
        )
        caller_kwargs = _report_kwargs(forged_observation)
        caller_kwargs["untrusted_profile_registry"] = forged_registry
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            build_monitoring_report(**caller_kwargs)
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        forged_record = passing.to_record()
        forged_record.update(
            runtime_profile_fingerprint=(
                forged_anchor.terminal_static_bindings_fingerprint
            ),
            runtime_profile_anchor_record=forged_anchor.to_record(),
            profile_registry_id=forged_registry.profile_registry_id,
            profile_registry_fingerprint=(
                forged_registry.profile_registry_fingerprint
            ),
        )
        material = {
            name: value for name, value in forged_record.items()
            if name not in {"monitoring_report_id", "report_fingerprint"}
        }
        forged_record["monitoring_report_id"] = (
            IU4RecoveryMonitoringReportV1.ID_PREFIX + _fp(material)
        )
        material["monitoring_report_id"] = forged_record[
            "monitoring_report_id"
        ]
        forged_record["report_fingerprint"] = _fp(material)

        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            IU4RecoveryMonitoringReportV1.from_record(forged_record)
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )
        constructor_values = dict(forged_record)
        constructor_values["reason_codes"] = tuple(
            constructor_values["reason_codes"]
        )
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            IU4RecoveryMonitoringReportV1(**constructor_values)
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )
        build_values = {
            name: value for name, value in constructor_values.items()
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint",
            }
        }
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            IU4RecoveryMonitoringReportV1.build(**build_values)
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        class MappingSubclass(dict):
            pass

        lookalike = passing.to_record()
        lookalike["runtime_profile_anchor_record"] = MappingSubclass(
            lookalike["runtime_profile_anchor_record"]
        )
        with self.assertRaises(IU4RecoveryProjectionError):
            IU4RecoveryMonitoringReportV1.from_record(lookalike)

    def test_pinned_report_authority_survives_root_resolver_class_and_import_alias_rebinding(self) -> None:
        import live_l1.state.paper_iu4_recovery_projection as projection_module

        original_builder = build_monitoring_report
        original_report_type = IU4RecoveryMonitoringReportV1
        original_error_type = IU4RecoveryProjectionError
        authority_global_names = {
            instruction.argval
            for instruction in dis.get_instructions(original_builder.__func__)
            if instruction.opname in {"LOAD_GLOBAL", "LOAD_NAME"}
        }
        self.assertTrue({
            "terminal_static_bindings_fingerprint",
            "IU4TerminalMonitoringObservationV1",
            "IU4RecoveryMonitoringReportV1",
        }.isdisjoint(authority_global_names))
        self.assertNotIn("__builtins__", authority_global_names)
        trusted_observation = _observation()
        trusted_kwargs = _report_kwargs(trusted_observation)
        trusted_report = original_builder(**trusted_kwargs)

        forged_channels = deepcopy(trusted_observation.runtime_channels)
        forged_channels["channel_records"][0]["receiver_tid"] = 8181
        forged_observation = _rebuild_observation(
            trusted_observation, "runtime_channels", **forged_channels
        )
        forged_anchor = IU4TerminalRuntimeProfileAnchorV1.build(
            runtime_profile_id="RP",
            terminal_static_bindings_fingerprint=(
                terminal_static_bindings_fingerprint(forged_observation)
            ),
        )
        forged_registry = IU4TerminalRuntimeProfileRegistryV1.from_anchors(
            (forged_anchor,)
        )
        forged_root = projection_module._IU4TerminalRuntimeProfileTrustRootV1.build(
            provisioning_authority_id="CALLER-REBIND-AUTHORITY",
            provisioning_authority_fingerprint=H,
            profile_registry=forged_registry,
        )
        forged_record = trusted_report.to_record()
        forged_record.update(
            runtime_profile_fingerprint=(
                forged_anchor.terminal_static_bindings_fingerprint
            ),
            runtime_profile_anchor_record=forged_anchor.to_record(),
            profile_registry_id=forged_registry.profile_registry_id,
            profile_registry_fingerprint=(
                forged_registry.profile_registry_fingerprint
            ),
        )
        forged_material = {
            name: value for name, value in forged_record.items()
            if name not in {"monitoring_report_id", "report_fingerprint"}
        }
        forged_record["monitoring_report_id"] = (
            "IU4-RECOVERY-MONITORING-REPORT-V1-" + _fp(forged_material)
        )
        forged_material["monitoring_report_id"] = forged_record[
            "monitoring_report_id"
        ]
        forged_record["report_fingerprint"] = _fp(forged_material)
        forged_constructor_values = dict(forged_record)
        forged_constructor_values["reason_codes"] = tuple(
            forged_constructor_values["reason_codes"]
        )
        forged_build_values = {
            name: value for name, value in forged_constructor_values.items()
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint",
            }
        }

        trusted_record = trusted_report.to_record()
        trusted_constructor_values = dict(trusted_record)
        trusted_constructor_values["reason_codes"] = tuple(
            trusted_constructor_values["reason_codes"]
        )
        trusted_build_values = {
            name: value for name, value in trusted_constructor_values.items()
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint",
            }
        }

        for attack in ("ROOT", "RESOLVER", "CLASSES", "IMPORT_ALIASES"):
            with self.subTest(attack=attack), ExitStack() as stack:
                if attack == "ROOT":
                    stack.enter_context(patch.object(
                        projection_module,
                        "_PROVISIONED_TERMINAL_RUNTIME_PROFILE_TRUST_ROOT",
                        forged_root,
                        create=True,
                    ))
                elif attack == "RESOLVER":
                    stack.enter_context(patch.object(
                        projection_module,
                        "_resolve_provisioned_terminal_runtime_profile",
                        forged_root.resolve,
                        create=True,
                    ))
                elif attack == "CLASSES":
                    for name in (
                        "_IU4TerminalRuntimeProfileTrustRootV1",
                        "IU4TerminalRuntimeProfileRegistryV1",
                        "IU4TerminalRuntimeProfileAnchorV1",
                    ):
                        stack.enter_context(
                            patch.object(projection_module, name, object)
                        )
                else:
                    test_module = __import__(__name__, fromlist=["*"])
                    stack.enter_context(patch.object(
                        test_module, "build_monitoring_report", lambda **_kwargs: None
                    ))
                    stack.enter_context(patch.object(
                        test_module, "IU4RecoveryMonitoringReportV1", object
                    ))

                trusted_rows = (
                    original_builder(**trusted_kwargs),
                    original_report_type(**trusted_constructor_values),
                    original_report_type.build(**trusted_build_values),
                    original_report_type.from_record(trusted_record),
                )
                self.assertTrue(all(
                    type(value) is original_report_type for value in trusted_rows
                ))

                forged_calls = (
                    lambda: original_builder(**_report_kwargs(forged_observation)),
                    lambda: original_report_type(**forged_constructor_values),
                    lambda: original_report_type.build(**forged_build_values),
                    lambda: original_report_type.from_record(forged_record),
                )
                for entry_index, invoke in enumerate(forged_calls):
                    with self.subTest(attack=attack, entry=entry_index), self.assertRaises(
                        original_error_type
                    ) as caught:
                        invoke()
                    self.assertEqual(
                        caught.exception.reason_code,
                        "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                    )

    def test_code_pinned_report_authority_survives_function_metadata_rebinding(self) -> None:
        original_builder = build_monitoring_report
        original_report_type = IU4RecoveryMonitoringReportV1
        original_error_type = IU4RecoveryProjectionError
        trusted_observation = _observation()
        trusted_kwargs = _report_kwargs(trusted_observation)
        trusted_report = original_builder(**trusted_kwargs)

        forged_channels = deepcopy(trusted_observation.runtime_channels)
        forged_channels["channel_records"][0]["receiver_tid"] = 8282
        forged_observation = _rebuild_observation(
            trusted_observation, "runtime_channels", **forged_channels
        )
        forged_anchor = IU4TerminalRuntimeProfileAnchorV1.build(
            runtime_profile_id="RP",
            terminal_static_bindings_fingerprint=(
                terminal_static_bindings_fingerprint(forged_observation)
            ),
        )
        forged_registry = IU4TerminalRuntimeProfileRegistryV1.from_anchors(
            (forged_anchor,)
        )
        projection_module = __import__(
            "live_l1.state.paper_iu4_recovery_projection", fromlist=["*"]
        )
        forged_root = projection_module._IU4TerminalRuntimeProfileTrustRootV1.build(
            provisioning_authority_id="CALLER-METADATA-AUTHORITY",
            provisioning_authority_fingerprint=H,
            profile_registry=forged_registry,
        )
        self.assertIs(
            type(forged_root),
            projection_module._IU4TerminalRuntimeProfileTrustRootV1,
        )

        forged_record = trusted_report.to_record()
        forged_record.update(
            runtime_profile_fingerprint=(
                forged_anchor.terminal_static_bindings_fingerprint
            ),
            runtime_profile_anchor_record=forged_anchor.to_record(),
            profile_registry_id=forged_registry.profile_registry_id,
            profile_registry_fingerprint=(
                forged_registry.profile_registry_fingerprint
            ),
        )
        forged_material = {
            name: value for name, value in forged_record.items()
            if name not in {"monitoring_report_id", "report_fingerprint"}
        }
        forged_record["monitoring_report_id"] = (
            "IU4-RECOVERY-MONITORING-REPORT-V1-" + _fp(forged_material)
        )
        forged_material["monitoring_report_id"] = forged_record[
            "monitoring_report_id"
        ]
        forged_record["report_fingerprint"] = _fp(forged_material)
        forged_constructor_values = dict(forged_record)
        forged_constructor_values["reason_codes"] = tuple(
            forged_constructor_values["reason_codes"]
        )
        forged_build_values = {
            name: value for name, value in forged_constructor_values.items()
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint",
            }
        }

        trusted_record = trusted_report.to_record()
        trusted_constructor_values = dict(trusted_record)
        trusted_constructor_values["reason_codes"] = tuple(
            trusted_constructor_values["reason_codes"]
        )
        trusted_build_values = {
            name: value for name, value in trusted_constructor_values.items()
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint",
            }
        }
        entry_functions = (
            original_builder.__func__,
            original_report_type._validate_specific,
            original_report_type.build.__func__.__func__,
            original_report_type.from_record.__func__.__func__,
        )
        authority_types = original_builder.__self__
        self.assertIs(authority_types.__class__, tuple)
        self.assertEqual(len(authority_types), 3)
        self.assertIs(authority_types[0], original_report_type)
        self.assertIs(
            authority_types[1], IU4TerminalMonitoringObservationV1
        )
        self.assertIs(
            authority_types[2],
            original_report_type.__post_init__,
        )
        with self.assertRaises(AttributeError):
            original_builder.__self__ = object
        pinned_builder_roots = tuple(
            value for value in authority_types[2].__code__.co_consts
            if type(value) is tuple
            and len(value) == 11
            and value[1] == "iu4_terminal_runtime_profile_trust_root_v1"
        )
        pinned_validator_roots = tuple(
            value
            for value in original_report_type._validate_specific.__code__.co_consts
            if type(value) is tuple
            and len(value) == 11
            and value[1] == "iu4_terminal_runtime_profile_trust_root_v1"
        )
        self.assertEqual(len(pinned_builder_roots), 1)
        self.assertEqual(pinned_validator_roots, pinned_builder_roots)
        pinned_root = pinned_builder_roots[0]
        pinned_anchors = tuple(
            IU4TerminalRuntimeProfileAnchorV1.build(
                runtime_profile_id=row[0],
                terminal_static_bindings_fingerprint=row[1],
            )
            for row in pinned_root[10]
        )
        self.assertEqual(
            tuple(
                (anchor.profile_anchor_id, anchor.profile_anchor_fingerprint)
                for anchor in pinned_anchors
            ),
            tuple((row[2], row[3]) for row in pinned_root[10]),
        )
        pinned_registry = IU4TerminalRuntimeProfileRegistryV1.from_anchors(
            pinned_anchors
        )
        self.assertEqual(
            (
                pinned_registry.profile_registry_id,
                pinned_registry.profile_registry_fingerprint,
            ),
            (pinned_root[6], pinned_root[7]),
        )
        rederived_root = (
            projection_module._IU4TerminalRuntimeProfileTrustRootV1.build(
                provisioning_authority_id=pinned_root[3],
                provisioning_authority_fingerprint=pinned_root[4],
                profile_registry=pinned_registry,
            )
        )
        self.assertIs(
            type(rederived_root),
            projection_module._IU4TerminalRuntimeProfileTrustRootV1,
        )
        self.assertEqual(
            (rederived_root.trust_root_id, rederived_root.trust_root_fingerprint),
            (pinned_root[2], pinned_root[8]),
        )
        with self.assertRaises(FrozenInstanceError):
            rederived_root.trust_root_id = "MUTATED"
        self.assertIsNone(original_builder.__func__.__defaults__)
        self.assertEqual(
            original_builder.__func__.__kwdefaults__,
            {"untrusted_profile_registry": None},
        )
        self.assertIsNone(original_report_type._validate_specific.__defaults__)
        self.assertIsNone(original_report_type._validate_specific.__kwdefaults__)

        for boundary in (
            "CLOSURES_ABSENT",
            "DEFAULTS",
            "KEYWORD_DEFAULTS",
            "FUNCTION_ATTRIBUTES",
            "CLASS_METADATA",
        ):
            with self.subTest(boundary=boundary), ExitStack() as stack:
                self.assertTrue(all(
                    function.__closure__ is None for function in entry_functions
                ))
                if boundary == "DEFAULTS":
                    for function in entry_functions:
                        stack.enter_context(patch.object(
                            function,
                            "__defaults__",
                            (forged_root.resolve,),
                        ))
                elif boundary == "KEYWORD_DEFAULTS":
                    for function in entry_functions:
                        keyword_defaults = dict(function.__kwdefaults__ or {})
                        keyword_defaults.update(
                            _pinned_profile_authority=forged_root.resolve,
                            _pinned_report_type=object,
                        )
                        stack.enter_context(patch.object(
                            function, "__kwdefaults__", keyword_defaults
                        ))
                elif boundary == "FUNCTION_ATTRIBUTES":
                    for function in entry_functions:
                        stack.enter_context(patch.dict(
                            function.__dict__,
                            {
                                "pinned_profile_authority": forged_root.resolve,
                                "pinned_report_type": object,
                            },
                        ))
                elif boundary == "CLASS_METADATA":
                    annotations = dict(original_report_type.__annotations__)
                    annotations["pinned_profile_authority"] = forged_root.resolve
                    stack.enter_context(patch.object(
                        original_report_type, "__annotations__", annotations
                    ))
                    stack.enter_context(patch.object(
                        original_report_type,
                        "pinned_profile_authority",
                        forged_root.resolve,
                        create=True,
                    ))
                    stack.enter_context(patch.object(
                        original_report_type,
                        "pinned_report_type",
                        object,
                        create=True,
                    ))

                trusted_rows = (
                    original_builder(**trusted_kwargs),
                    original_report_type(**trusted_constructor_values),
                    original_report_type.build(**trusted_build_values),
                    original_report_type.from_record(trusted_record),
                )
                self.assertTrue(all(
                    type(value) is original_report_type for value in trusted_rows
                ))
                forged_calls = (
                    lambda: original_builder(**_report_kwargs(forged_observation)),
                    lambda: original_report_type(**forged_constructor_values),
                    lambda: original_report_type.build(**forged_build_values),
                    lambda: original_report_type.from_record(forged_record),
                )
                for entry_index, invoke in enumerate(forged_calls):
                    with self.subTest(
                        boundary=boundary, entry=entry_index
                    ), self.assertRaises(original_error_type) as caught:
                        invoke()
                    self.assertEqual(
                        caught.exception.reason_code,
                        "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                    )

    def test_projection_lag_is_warn_and_blocks_entry(self) -> None:
        observation = IU4TerminalMonitoringObservationV1.build_minimal_pass(
            runtime_session_id="SESSION-1", runtime_session_open_record_fingerprint=H,
            authority_generation_id="GEN-1", authority_commit_anchor=H2,
            atomic_root_fingerprint=H, source_collector_id="COLLECTOR-1",
            source_evidence_id="EVIDENCE-1", source_evidence_sha256=H2,
            observation_sequence=1, observed_at_utc=UTC,
        )
        kwargs = dict(
            observation=observation, owner_epoch="PEE", report_operation="MONITOR_ONLY",
            expected_runtime_session_id="SESSION-1",
            expected_runtime_session_open_record_fingerprint=H,
            expected_authority_generation_id="GEN-1",
            expected_authority_commit_anchor=H2,
            expected_atomic_root_fingerprint=H,
            lifecycle_root_inventory_fingerprint=H, atomic_root_inventory_fingerprint=H2,
            projection_root_inventory_fingerprint=H, authorization_valid=True,
            runtime_profile_id="RP",
            economics_profile_id="EP", economics_profile_fingerprint=H2,
            entry_throttle_profile_id="TP", entry_throttle_profile_fingerprint=H,
            runtime_control_fingerprint=H2, lifecycle_ledger_tip_event_id="LEDGER-1",
            lifecycle_ledger_tip_fingerprint=H, open_prepare_count=0,
            runtime_session_status="OPEN_CLEAN", handoff_or_genesis_manifest_id="MANIFEST-1",
            handoff_or_genesis_manifest_fingerprint=H2, atomic_journal_sequence=2,
            atomic_journal_head=H, atomic_snapshot_fingerprint=H,
            authority_root_ancestry_result="PASS", projection_cursor_id="CURSOR-1",
            projection_cursor_fingerprint=H2, projection_cursor_sequence=1,
            projection_cursor_journal_head=H2, component_fingerprints={
                "s2": H, "account": H2, "throttle": H, "loss_cluster": H2,
                "s4": H, "entry_quote": H2, "progress_cursor": H,
            }, terminal_gap_status="NONE", reported_at_utc=UTC,
        )
        report = build_monitoring_report(**kwargs)
        self.assertEqual(report.overall_result, "WARN")
        self.assertEqual(report.entry_capability_result, "BLOCKED")
        self.assertIn("PEE_IU4_PROJECTION_LAG", report.reason_codes)

    def test_close_fsm_session_status_positive_and_negative_matrix(self) -> None:
        base = _observation()
        positive_rows = (
            ("OPEN", {}, "OPEN_CLEAN"),
            ("CLOSING", {"close_fsm_phase": "CLOSING"}, "OPEN_CLEAN"),
            ("PREPARE", {
                "close_fsm_phase": "PREPARE",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
            }, "OPEN_CLEAN"),
            ("BROKER_CLOSED", {
                "close_fsm_phase": "BROKER_CLOSED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_peer_status": "OK", "close_hup_status": "HUP",
            }, "OPEN_CLEAN"),
            ("COMMIT", {
                "close_fsm_phase": "COMMIT",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_commit_event_id": "CLOSE-COMMIT-1",
                "close_peer_status": "OK", "close_hup_status": "HUP",
            }, "OPEN_CLEAN"),
            ("COMMITTED", {
                "channel_phase": "RELEASED", "close_fsm_phase": "COMMITTED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_commit_event_id": "CLOSE-COMMIT-1",
                "close_peer_status": "OK", "close_hup_status": "HUP",
            }, "CLOSED_CLEAN"),
            ("FAILED_OPEN", {
                "close_fsm_phase": "FAILED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "close_peer_status": "ERROR",
            }, "OPEN_UNCLEAN"),
            ("FAILED_CLOSED", {
                "channel_phase": "RELEASED", "close_fsm_phase": "FAILED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_commit_event_id": "CLOSE-COMMIT-1",
                "close_timeout_status": "TIMEOUT",
            }, "CLOSED_UNCLEAN"),
        )
        for name, changes, session_status in positive_rows:
            observation = _rebuild_observation(
                base, "runtime_close_fsm", **changes
            )
            if session_status.endswith("UNCLEAN"):
                observation = _rebuild_observation(
                    observation, "failstop_and_terminal_gap",
                    runtime_session_unclean=True,
                )
            kwargs = _report_kwargs(observation)
            kwargs["runtime_session_status"] = session_status
            report = build_monitoring_report(**kwargs)
            with self.subTest(positive=name):
                self.assertEqual(report.runtime_close_fsm_result, "PASS")

        negative_rows = (
            ("OPEN_WITH_STATUS", {"close_peer_status": "OK"}, "OPEN_CLEAN"),
            ("PREPARE_WITHOUT_ID", {"close_fsm_phase": "PREPARE"}, "OPEN_CLEAN"),
            ("BROKER_WITHOUT_EVIDENCE", {
                "close_fsm_phase": "BROKER_CLOSED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "close_peer_status": "OK", "close_hup_status": "HUP",
            }, "OPEN_CLEAN"),
            ("COMMIT_WITHOUT_COMMIT_ID", {
                "close_fsm_phase": "COMMIT",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_peer_status": "OK", "close_hup_status": "HUP",
            }, "OPEN_CLEAN"),
            ("COMMITTED_OPEN_CLEAN", {
                "channel_phase": "RELEASED", "close_fsm_phase": "COMMITTED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_commit_event_id": "CLOSE-COMMIT-1",
                "close_peer_status": "OK", "close_hup_status": "HUP",
            }, "OPEN_CLEAN"),
            ("COMMITTED_OPEN_UNCLEAN", {
                "channel_phase": "RELEASED", "close_fsm_phase": "COMMITTED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_commit_event_id": "CLOSE-COMMIT-1",
                "close_peer_status": "OK", "close_hup_status": "HUP",
            }, "OPEN_UNCLEAN"),
            ("COMMITTED_CHANNEL_OPEN", {
                "close_fsm_phase": "COMMITTED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_commit_event_id": "CLOSE-COMMIT-1",
                "close_peer_status": "OK", "close_hup_status": "HUP",
            }, "CLOSED_CLEAN"),
        )
        for name, changes, session_status in negative_rows:
            observation = _rebuild_observation(
                base, "runtime_close_fsm", **changes
            )
            if session_status.endswith("UNCLEAN"):
                observation = _rebuild_observation(
                    observation, "failstop_and_terminal_gap",
                    runtime_session_unclean=True,
                )
            kwargs = _report_kwargs(observation)
            kwargs["runtime_session_status"] = session_status
            report = build_monitoring_report(**kwargs)
            with self.subTest(negative=name):
                self.assertEqual(report.runtime_close_fsm_result, "FAIL")
                self.assertEqual(report.overall_result, "FAIL")

    def test_failed_close_fsm_complete_evidence_status_session_matrix(self) -> None:
        base = _observation()
        identifier_rows = (
            ("PRE_PREPARE", {}, "OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN"),
            ("POST_PREPARE", {
                "close_prepare_event_id": "CLOSE-PREPARE-1",
            }, "OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN"),
            ("POST_BROKER", {
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
            }, "RELEASED", "CLOSED_UNCLEAN"),
            ("POST_COMMIT_OPEN", {
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_commit_event_id": "CLOSE-COMMIT-1",
            }, "OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN"),
            ("POST_COMMIT_RELEASED", {
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_commit_event_id": "CLOSE-COMMIT-1",
            }, "RELEASED", "CLOSED_UNCLEAN"),
        )
        for stage, identifiers, channel, session in identifier_rows:
            status_rows = [
                (
                    {"close_peer_status": "ERROR"},
                    "PEE_IU4_RUNTIME_SESSION_CLOSE_TRANSPORT_FAILED",
                ),
                (
                    {"close_timeout_status": "TIMEOUT"},
                    "PEE_IU4_RUNTIME_SESSION_CLOSE_TIMEOUT",
                ),
            ]
            if identifiers:
                status_rows.extend((
                    (
                        {"close_peer_status": "OK", "close_hup_status": "ERROR"},
                        "PEE_IU4_RUNTIME_SESSION_CLOSE_TRANSPORT_FAILED",
                    ),
                    (
                        {"close_peer_status": "OK", "close_timeout_status": "TIMEOUT"},
                        "PEE_IU4_RUNTIME_SESSION_CLOSE_TIMEOUT",
                    ),
                ))
            for statuses, reason in status_rows:
                observation = _rebuild_observation(
                    base, "runtime_close_fsm", close_fsm_phase="FAILED",
                    channel_phase=channel, **identifiers, **statuses,
                )
                observation = _rebuild_observation(
                    observation, "failstop_and_terminal_gap",
                    runtime_session_unclean=True,
                )
                kwargs = _report_kwargs(observation)
                kwargs["runtime_session_status"] = session
                report = build_monitoring_report(**kwargs)
                with self.subTest(stage=stage, statuses=statuses):
                    self.assertEqual(report.runtime_close_fsm_result, "PASS")
                    self.assertEqual(report.runtime_close_fsm_reason_code, reason)
                    self.assertEqual(
                        report.reason_codes[:2],
                        ("PEE_IU4_RUNTIME_SESSION_UNCLEAN", reason),
                    )

        invalid_rows = (
            ("RELEASED_WITHOUT_EVIDENCE", {
                "channel_phase": "RELEASED", "close_fsm_phase": "FAILED",
                "close_timeout_status": "TIMEOUT",
            }, "CLOSED_UNCLEAN"),
            ("HUP_ERROR_BEFORE_PREPARE", {
                "close_fsm_phase": "FAILED", "close_hup_status": "ERROR",
            }, "OPEN_UNCLEAN"),
            ("NON_PREFIX_EVIDENCE", {
                "close_fsm_phase": "FAILED",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_peer_status": "ERROR",
            }, "OPEN_UNCLEAN"),
            ("MULTIPLE_FAILURE_MARKERS", {
                "close_fsm_phase": "FAILED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "close_peer_status": "ERROR", "close_timeout_status": "TIMEOUT",
            }, "OPEN_UNCLEAN"),
            ("POST_BROKER_NOT_RELEASED", {
                "close_fsm_phase": "FAILED",
                "close_prepare_event_id": "CLOSE-PREPARE-1",
                "broker_closed_evidence_id": "BROKER-CLOSED-1",
                "close_timeout_status": "TIMEOUT",
            }, "OPEN_UNCLEAN"),
            ("PRE_PREPARE_CLOSED_SESSION", {
                "close_fsm_phase": "FAILED", "close_peer_status": "ERROR",
            }, "CLOSED_UNCLEAN"),
        )
        for name, changes, session in invalid_rows:
            observation = _rebuild_observation(
                base, "runtime_close_fsm", **changes
            )
            observation = _rebuild_observation(
                observation, "failstop_and_terminal_gap",
                runtime_session_unclean=True,
            )
            kwargs = _report_kwargs(observation)
            kwargs["runtime_session_status"] = session
            report = build_monitoring_report(**kwargs)
            with self.subTest(name=name):
                self.assertEqual(report.runtime_close_fsm_result, "FAIL")
                self.assertEqual(report.overall_result, "FAIL")
                expected_reason = (
                    "PEE_IU4_RUNTIME_SESSION_CLOSE_INCOMPLETE"
                    if name == "NON_PREFIX_EVIDENCE"
                    else "PEE_IU4_RUNTIME_SESSION_CLOSE_PROTOCOL_INVALID"
                )
                self.assertEqual(
                    report.runtime_close_fsm_reason_code, expected_reason
                )
                self.assertIn(expected_reason, report.reason_codes)

    def test_hard_fail_never_reports_entry_available_and_gap_enum_is_closed(self) -> None:
        observation = _observation()
        kwargs = _report_kwargs(observation)
        kwargs["authorization_valid"] = False
        report = build_monitoring_report(**kwargs)
        self.assertEqual(report.overall_result, "FAIL")
        self.assertEqual(report.entry_capability_result, "BLOCKED")
        self.assertIn("PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH", report.reason_codes)
        kwargs = _report_kwargs(observation)
        kwargs["terminal_gap_status"] = "BOGUS"
        with self.assertRaises(IU4RecoveryProjectionError):
            build_monitoring_report(**kwargs)
        kwargs = _report_kwargs(observation)
        kwargs["expected_authority_generation_id"] = "FOREIGN-GENERATION"
        with self.assertRaises(IU4RecoveryProjectionError):
            build_monitoring_report(**kwargs)

    def test_all_twelve_terminal_groups_drive_fail_without_caller_results(self) -> None:
        base = _observation()
        mutations = {
            "role_readiness": ("parent_guardian_ready", False),
            "lease_and_self_death": ("self_death_timer_armed", False),
            "pidfd_targets": ("trading_self", {**base.pidfd_targets["trading_self"], "sigkill_probe_result": "FAIL"}),
            "control_word_and_memfd": ("broker_cas_sequence", 1),
            "signal_envelope": ("wait_killable_recv", False),
            "runtime_channels": ("channel_records", [{**row, "so_passcred": 1} for row in base.runtime_channels["channel_records"]]),
            "seccomp_lsm_capability": ("seccomp_listener_receive_error_status", "FATAL"),
            "runtime_close_fsm": ("close_fsm_phase", "FAILED"),
            "heartbeat_and_budgets": ("heartbeat_age_ms", 26),
            "failstop_and_terminal_gap": ("runtime_session_unclean", True),
            "completion_provenance": ("direct_first_start_eligible", False),
            "safety_resource_schema": ("resource_reserve_status", "EXHAUSTED"),
        }
        for index, (group, (key, value)) in enumerate(mutations.items()):
            record = base.to_record(); record[group][key] = value
            fields = {name: record[name] for name in record if name not in {
                "schema_version", "artifact_type", "terminal_monitoring_observation_id", "observation_fingerprint"
            }}
            changed = IU4TerminalMonitoringObservationV1.build(**fields)
            kwargs = _report_kwargs(changed)
            if group == "failstop_and_terminal_gap":
                kwargs["runtime_session_status"] = "OPEN_UNCLEAN"
            report = build_monitoring_report(**kwargs)
            self.assertEqual(report.group_results()[index], "FAIL", group)
            self.assertEqual(report.overall_result, "FAIL", group)

    def test_static_terminal_bindings_and_operation_owner_semantics_fail_closed(self) -> None:
        base = _observation()
        static_mutations = (
            ("role_readiness", {"listener_owner_role": "TRADING_CHILD"}),
            ("pidfd_targets", {
                "guardian": {
                    **base.pidfd_targets["guardian"], "target_pid": 999,
                },
            }),
            ("control_word_and_memfd", {"memfd_create_flags": ["MFD_ALLOW_SEALING"]}),
            ("seccomp_lsm_capability", {
                "lsm_hook_coverage": [
                    "wrong_file_open", "wrong_file_permission",
                    "wrong_socket_connect", "wrong_socket_sendmsg",
                    "wrong_task_kill", "wrong_bprm_check_security",
                ],
            }),
        )
        for group, changes in static_mutations:
            changed = _rebuild_observation(base, group, **changes)
            with self.subTest(group=group), self.assertRaises(
                IU4RecoveryProjectionError
            ) as caught:
                build_monitoring_report(**_report_kwargs(changed))
            self.assertEqual(
                caught.exception.reason_code,
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            )

        close = _rebuild_observation(
            base, "runtime_close_fsm", close_prepare_event_id="FORGED-PREPARE"
        )
        close_report = build_monitoring_report(**_report_kwargs(close))
        self.assertEqual(close_report.runtime_close_fsm_result, "FAIL")

        failstop = _rebuild_observation(
            base, "failstop_and_terminal_gap", failstop_asserted=True
        )
        failstop_report = build_monitoring_report(**_report_kwargs(failstop))
        self.assertEqual(failstop_report.failstop_and_terminal_gap_result, "FAIL")

        recovered = _rebuild_observation(
            base, "completion_provenance",
            completion_provenance="RECOVERED_AFTER_PREPARE",
            completion_authorization_id="AUTH-1",
            completion_consumption_event_id="CONSUME-1",
            completion_startup_attempt_id="START-1",
        )
        recovered_kwargs = _report_kwargs(recovered)
        recovered_kwargs["runtime_profile_id"] = "RP-RECOVERED-INVALID"
        recovered_report = build_monitoring_report(**recovered_kwargs)
        self.assertEqual(recovered_report.completion_provenance_result, "FAIL")

        pee_legacy = _rebuild_observation(
            base, "safety_resource_schema", legacy_exit_only_status="ACTIVE"
        )
        pee_legacy_report = build_monitoring_report(**_report_kwargs(pee_legacy))
        self.assertEqual(pee_legacy_report.safety_resource_schema_result, "FAIL")
        self.assertEqual(pee_legacy_report.overall_result, "FAIL")

        recovery_kwargs = _report_kwargs(base)
        recovery_kwargs["report_operation"] = "RECOVER_AND_RESTART"
        recovery_report = build_monitoring_report(**recovery_kwargs)
        self.assertEqual(recovery_report.safety_resource_schema_result, "FAIL")
        self.assertEqual(recovery_report.overall_result, "FAIL")

    def test_terminal_unknown_enums_nested_shape_and_subclass_fail_closed(self) -> None:
        base = _observation()
        rows = [
            ("runtime_close_fsm", "close_fsm_phase", "UNKNOWN"),
            ("heartbeat_and_budgets", "heartbeat_age_ms", True),
            ("safety_resource_schema", "atomic_schema_version", True),
            ("safety_resource_schema", "kill_level", "soft"),
        ]
        for group, key, value in rows:
            record = base.to_record(); record[group][key] = value
            fields = {name: record[name] for name in record if name not in {
                "schema_version", "artifact_type", "terminal_monitoring_observation_id", "observation_fingerprint"
            }}
            with self.subTest(group=group, key=key), self.assertRaises(IU4RecoveryProjectionError):
                IU4TerminalMonitoringObservationV1.build(**fields)
        record = base.to_record(); record["runtime_channels"]["channel_records"][0]["extra"] = 1
        fields = {name: record[name] for name in record if name not in {
            "schema_version", "artifact_type", "terminal_monitoring_observation_id", "observation_fingerprint"
        }}
        with self.assertRaises(IU4RecoveryProjectionError):
            IU4TerminalMonitoringObservationV1.build(**fields)

    def test_budget_boundary_matrix(self) -> None:
        base = _observation()
        for field, accepted, rejected in (
            ("heartbeat_age_ms", (0, 25), (-1, 26)),
            ("capability_probe_age_ms", (0, 25), (-1, 26)),
            ("capability_probe_expiry_ms", (0, 25), (-1, 26)),
            ("termination_latch_deadline_ms", (1, 100), (0, 101)),
        ):
            for value in accepted:
                record = base.to_record(); record["heartbeat_and_budgets"][field] = value
                payload = {name: record[name] for name in record if name not in {
                    "schema_version", "artifact_type", "terminal_monitoring_observation_id", "observation_fingerprint"
                }}
                observation = IU4TerminalMonitoringObservationV1.build(**payload)
                self.assertEqual(build_monitoring_report(**_report_kwargs(observation)).heartbeat_and_budgets_result, "PASS")
            for value in rejected:
                record = base.to_record(); record["heartbeat_and_budgets"][field] = value
                payload = {name: record[name] for name in record if name not in {
                    "schema_version", "artifact_type", "terminal_monitoring_observation_id", "observation_fingerprint"
                }}
                if value < 0:
                    with self.assertRaises(IU4RecoveryProjectionError):
                        IU4TerminalMonitoringObservationV1.build(**payload)
                else:
                    observation = IU4TerminalMonitoringObservationV1.build(**payload)
                    self.assertEqual(build_monitoring_report(**_report_kwargs(observation)).heartbeat_and_budgets_result, "FAIL")

    def test_report_session_manifest_cursor_sentinel_matrix(self) -> None:
        absent_observation = _observation(
            runtime_session_id=NONE, runtime_session_open_record_fingerprint=NONE
        )
        kwargs = _report_kwargs(absent_observation)
        kwargs.update(runtime_session_status="ABSENT")
        self.assertEqual(build_monitoring_report(**kwargs).runtime_session_id, NONE)
        legacy = _report_kwargs(_observation())
        legacy.update(owner_epoch="LEGACY", runtime_session_status="OPEN_CLEAN",
                      handoff_or_genesis_manifest_id=NONE,
                      handoff_or_genesis_manifest_fingerprint=NONE)
        self.assertEqual(build_monitoring_report(**legacy).handoff_or_genesis_manifest_id, NONE)
        for changes in (
            {"runtime_session_status": "ABSENT", "runtime_session_id": "SESSION-1"},
            {"projection_cursor_id": "CURSOR-1", "projection_cursor_fingerprint": NONE},
            {"projection_cursor_sequence": 1},
            {"projection_cursor_journal_head": H},
        ):
            record = build_monitoring_report(**_report_kwargs(_observation())).to_record()
            record.update(changes)
            payload = {name: record[name] for name in record if name not in {
                "schema_version", "artifact_type", "monitoring_report_id", "report_fingerprint"
            }}
            payload["reason_codes"] = tuple(payload["reason_codes"])
            with self.subTest(changes=changes), self.assertRaises(IU4RecoveryProjectionError):
                IU4RecoveryMonitoringReportV1.build(**payload)

    def test_monitoring_precedence_root_before_lag_and_authorization(self) -> None:
        kwargs = _report_kwargs(_observation())
        kwargs.update(atomic_journal_sequence=2, atomic_journal_head=H,
                      authority_root_ancestry_result="FAIL", authorization_valid=False)
        report = build_monitoring_report(**kwargs)
        self.assertEqual(report.overall_result, "FAIL")
        self.assertEqual(report.reason_codes, (
            "PEE_IU4_AUTHORITY_ROOT_MISMATCH", "PEE_IU4_PROJECTION_LAG",
            "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH",
        ))


class I6MonitoringNamespaceBoundaryTests(unittest.TestCase):
    def test_globals_helper_alias_and_type_namespaces_fail_closed(self) -> None:
        import live_l1.state.paper_iu4_recovery_projection as projection_module

        original_builder = build_monitoring_report
        original_report_type = IU4RecoveryMonitoringReportV1
        original_observation_type = IU4TerminalMonitoringObservationV1
        original_error_type = IU4RecoveryProjectionError
        trusted_observation = _observation()
        trusted_kwargs = _report_kwargs(trusted_observation)
        trusted_report = original_builder(**trusted_kwargs)

        forged_channels = deepcopy(trusted_observation.runtime_channels)
        forged_channels["channel_records"][0]["receiver_tid"] = 8383
        forged_observation = _rebuild_observation(
            trusted_observation, "runtime_channels", **forged_channels
        )
        forged_static_fingerprint = terminal_static_bindings_fingerprint(
            forged_observation
        )
        self.assertNotEqual(
            forged_static_fingerprint,
            trusted_report.runtime_profile_fingerprint,
        )
        forged_anchor = IU4TerminalRuntimeProfileAnchorV1.build(
            runtime_profile_id="RP",
            terminal_static_bindings_fingerprint=forged_static_fingerprint,
        )
        forged_registry = IU4TerminalRuntimeProfileRegistryV1.from_anchors(
            (forged_anchor,)
        )
        forged_record = trusted_report.to_record()
        forged_record.update(
            runtime_profile_fingerprint=forged_static_fingerprint,
            runtime_profile_anchor_record=forged_anchor.to_record(),
            profile_registry_id=forged_registry.profile_registry_id,
            profile_registry_fingerprint=(
                forged_registry.profile_registry_fingerprint
            ),
        )
        forged_material = {
            name: value for name, value in forged_record.items()
            if name not in {"monitoring_report_id", "report_fingerprint"}
        }
        forged_record["monitoring_report_id"] = (
            "IU4-RECOVERY-MONITORING-REPORT-V1-" + _fp(forged_material)
        )
        forged_material["monitoring_report_id"] = forged_record[
            "monitoring_report_id"
        ]
        forged_record["report_fingerprint"] = _fp(forged_material)
        forged_constructor_values = dict(forged_record)
        forged_constructor_values["reason_codes"] = tuple(
            forged_constructor_values["reason_codes"]
        )
        forged_build_values = {
            name: value for name, value in forged_constructor_values.items()
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint",
            }
        }

        trusted_record = trusted_report.to_record()
        trusted_constructor_values = dict(trusted_record)
        trusted_constructor_values["reason_codes"] = tuple(
            trusted_constructor_values["reason_codes"]
        )
        trusted_build_values = {
            name: value for name, value in trusted_constructor_values.items()
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint",
            }
        }

        class ObservationLookalike:
            def __init__(self, source) -> None:
                self.__dict__.update(source.__dict__)

            def to_record(self):
                return forged_observation.to_record()

        lookalike = ObservationLookalike(forged_observation)

        class RuntimeChannelsDescriptor:
            def __get__(self, instance, _owner):
                if instance is None:
                    return self
                if instance is forged_observation:
                    return trusted_observation.runtime_channels
                return instance.__dict__["runtime_channels"]

            def __set__(self, instance, value) -> None:
                instance.__dict__["runtime_channels"] = value

        real_builtin_type = builtins.type

        def forged_builtin_type(value, *args):
            if args:
                return real_builtin_type(value, *args)
            if value is lookalike:
                return original_observation_type
            return real_builtin_type(value)

        authorized_count = 0
        forged_count = 0
        boundaries = (
            "HELPER_GLOBAL_ALIAS",
            "OBSERVATION_GLOBAL_AND_HELPER_ALIASES",
            "BUILTIN_TYPE_AND_HELPER_ALIASES",
            "REPORT_IMPORT_AND_CLASS_METADATA_ALIASES",
            "OBSERVATION_CLASS_DESCRIPTOR_AND_HELPER_ALIAS",
        )
        for boundary in boundaries:
            with self.subTest(boundary=boundary), ExitStack() as stack:
                forged_builder_observation = forged_observation
                if boundary == "HELPER_GLOBAL_ALIAS":
                    stack.enter_context(patch.object(
                        projection_module,
                        "terminal_static_bindings_fingerprint",
                        lambda _observation: trusted_report.runtime_profile_fingerprint,
                    ))
                elif boundary == "OBSERVATION_GLOBAL_AND_HELPER_ALIASES":
                    forged_builder_observation = lookalike
                    stack.enter_context(patch.object(
                        projection_module,
                        "IU4TerminalMonitoringObservationV1",
                        ObservationLookalike,
                    ))
                    stack.enter_context(patch.object(
                        projection_module,
                        "terminal_static_bindings_fingerprint",
                        lambda _observation: trusted_report.runtime_profile_fingerprint,
                    ))
                elif boundary == "BUILTIN_TYPE_AND_HELPER_ALIASES":
                    forged_builder_observation = lookalike
                    stack.enter_context(patch.object(
                        builtins, "type", forged_builtin_type
                    ))
                    stack.enter_context(patch.object(
                        projection_module,
                        "terminal_static_bindings_fingerprint",
                        lambda _observation: trusted_report.runtime_profile_fingerprint,
                    ))
                elif boundary == "REPORT_IMPORT_AND_CLASS_METADATA_ALIASES":
                    stack.enter_context(patch.object(
                        projection_module,
                        "IU4RecoveryMonitoringReportV1",
                        object,
                    ))
                    stack.enter_context(patch.object(
                        original_report_type,
                        "pinned_report_type",
                        object,
                        create=True,
                    ))
                else:
                    stack.enter_context(patch.object(
                        original_observation_type,
                        "runtime_channels",
                        RuntimeChannelsDescriptor(),
                        create=True,
                    ))
                    stack.enter_context(patch.object(
                        projection_module,
                        "terminal_static_bindings_fingerprint",
                        lambda _observation: trusted_report.runtime_profile_fingerprint,
                    ))
                    stack.enter_context(patch.object(
                        original_report_type,
                        "pinned_observation_type",
                        ObservationLookalike,
                        create=True,
                    ))

                trusted_rows = (
                    original_builder(**trusted_kwargs),
                    original_report_type(**trusted_constructor_values),
                    original_report_type.build(**trusted_build_values),
                    original_report_type.from_record(trusted_record),
                )
                for value in trusted_rows:
                    self.assertIs(value.__class__, original_report_type)
                    authorized_count += 1

                forged_calls = (
                    lambda: original_builder(**_report_kwargs(
                        forged_builder_observation
                    )),
                    lambda: original_report_type(**forged_constructor_values),
                    lambda: original_report_type.build(**forged_build_values),
                    lambda: original_report_type.from_record(forged_record),
                )
                for entry_index, invoke in enumerate(forged_calls):
                    with self.subTest(boundary=boundary, entry=entry_index):
                        try:
                            invoke()
                        except original_error_type:
                            pass
                        else:
                            self.fail("forged report entry did not fail closed")
                    forged_count += 1

        self.assertEqual(authorized_count, 20)
        self.assertEqual(forged_count, 20)

    def test_all_static_profile_groups_ignore_forged_helper_alias(self) -> None:
        import live_l1.state.paper_iu4_recovery_projection as projection_module

        base = _observation()
        trusted_report = build_monitoring_report(**_report_kwargs(base))
        channels = deepcopy(base.runtime_channels)
        channels["channel_records"][0]["receiver_tid"] = 8484
        mutations = (
            ("role_readiness", {"listener_owner_role": "TRADING_CHILD"}),
            ("lease_and_self_death", {"os_lease_identifier": "LEASE-2"}),
            ("pidfd_targets", {
                "guardian": {
                    **base.pidfd_targets["guardian"], "target_pid": 999,
                },
            }),
            ("control_word_and_memfd", {
                "memfd_create_flags": ["MFD_ALLOW_SEALING"],
            }),
            ("signal_envelope", {"signal_mask_fingerprint": H2}),
            ("runtime_channels", channels),
            ("seccomp_lsm_capability", {
                "lsm_hook_coverage": [
                    "wrong_file_open", "file_permission", "socket_connect",
                    "socket_sendmsg", "task_kill", "bprm_check_security",
                ],
            }),
            ("runtime_close_fsm", {
                "request_owner_role": "PARENT_GUARDIAN_V13",
            }),
            ("heartbeat_and_budgets", {"heartbeat_interval_ms": 11}),
            ("failstop_and_terminal_gap", {
                "liveness_pipe_read_endpoint_id": "PIPE-X",
            }),
            ("completion_provenance", {
                "direct_process_instance_id": "PROCESS-2",
            }),
            ("safety_resource_schema", {"atomic_schema_version": 3}),
        )
        with patch.object(
            projection_module,
            "terminal_static_bindings_fingerprint",
            lambda _observation: trusted_report.runtime_profile_fingerprint,
        ):
            for group, changes in mutations:
                forged = _rebuild_observation(base, group, **changes)
                self.assertNotEqual(
                    terminal_static_bindings_fingerprint(forged),
                    trusted_report.runtime_profile_fingerprint,
                    group,
                )
                with self.subTest(group=group), self.assertRaises(
                    IU4RecoveryProjectionError
                ) as caught:
                    build_monitoring_report(**_report_kwargs(forged))
                self.assertEqual(
                    caught.exception.reason_code,
                    "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                )


class I6MonitoringObservationContentBoundaryTests(unittest.TestCase):
    @staticmethod
    def _readdress(record: dict[str, object]) -> dict[str, object]:
        material = {
            name: value for name, value in record.items()
            if name not in {"monitoring_report_id", "report_fingerprint"}
        }
        report_id = "IU4-RECOVERY-MONITORING-REPORT-V1-" + _fp(material)
        record["monitoring_report_id"] = report_id
        material["monitoring_report_id"] = report_id
        record["report_fingerprint"] = _fp(material)
        return record

    @staticmethod
    def _constructor_values(record: dict[str, object]) -> dict[str, object]:
        values = dict(record)
        values["reason_codes"] = tuple(values["reason_codes"])
        return values

    @classmethod
    def _build_values(cls, record: dict[str, object]) -> dict[str, object]:
        values = cls._constructor_values(record)
        return {
            name: value for name, value in values.items()
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint",
            }
        }

    def test_divergent_content_addressed_static_observation_fails_all_four_entries(self) -> None:
        base = _observation()
        trusted = build_monitoring_report(**_report_kwargs(base))
        channels = deepcopy(base.runtime_channels)
        channels["channel_records"][0]["receiver_tid"] = 9917
        divergent = _rebuild_observation(
            base, "runtime_channels", **channels
        )
        self.assertNotEqual(
            divergent.observation_fingerprint,
            base.observation_fingerprint,
        )
        forged = trusted.to_record()
        forged["terminal_monitoring_observation_id"] = (
            divergent.terminal_monitoring_observation_id
        )
        forged["terminal_monitoring_observation_fingerprint"] = (
            divergent.observation_fingerprint
        )
        forged["terminal_monitoring_observation_record"] = (
            divergent.to_record()
        )
        forged = self._readdress(forged)
        calls = (
            lambda: build_monitoring_report(**_report_kwargs(divergent)),
            lambda: IU4RecoveryMonitoringReportV1(
                **self._constructor_values(forged)
            ),
            lambda: IU4RecoveryMonitoringReportV1.build(
                **self._build_values(forged)
            ),
            lambda: IU4RecoveryMonitoringReportV1.from_record(forged),
        )
        rejected = 0
        for index, invoke in enumerate(calls):
            with self.subTest(entry=index), self.assertRaises(
                IU4RecoveryProjectionError
            ) as caught:
                invoke()
            self.assertEqual(
                caught.exception.reason_code,
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            )
            rejected += 1
        self.assertEqual(rejected, 4)

    def test_nonstatic_content_addressed_observation_is_identical_across_entries(self) -> None:
        base = _observation()
        record = base.to_record()
        record["source_evidence_id"] = "EVIDENCE-NEW-CONTENT"
        payload = {
            name: value for name, value in record.items()
            if name not in {
                "schema_version", "artifact_type",
                "terminal_monitoring_observation_id", "observation_fingerprint",
            }
        }
        changed = IU4TerminalMonitoringObservationV1.build(**payload)
        report = build_monitoring_report(**_report_kwargs(changed))
        report_record = report.to_record()
        rows = (
            report,
            IU4RecoveryMonitoringReportV1(
                **self._constructor_values(report_record)
            ),
            IU4RecoveryMonitoringReportV1.build(
                **self._build_values(report_record)
            ),
            IU4RecoveryMonitoringReportV1.from_record(report_record),
        )
        self.assertTrue(all(row.to_record() == report_record for row in rows))
        self.assertTrue(all(
            row.terminal_monitoring_observation_fingerprint
            == changed.observation_fingerprint
            for row in rows
        ))


class I6MonitoringResultAuthorityBoundaryTests(unittest.TestCase):
    @staticmethod
    def _forged_authorized_record(observation):
        report = build_monitoring_report(**_report_kwargs(observation))
        record = report.to_record()
        record.update(
            role_readiness_result="PASS",
            runtime_close_fsm_result="PASS",
            runtime_close_fsm_reason_code=NONE,
            failstop_and_terminal_gap_result="PASS",
            overall_result="PASS",
            entry_capability_result="AVAILABLE",
            reason_codes=[],
        )
        return I6MonitoringObservationContentBoundaryTests._readdress(record)

    @staticmethod
    def _four_entry_outcomes(observation, forged_record):
        constructor = (
            I6MonitoringObservationContentBoundaryTests._constructor_values(
                forged_record
            )
        )
        build_values = (
            I6MonitoringObservationContentBoundaryTests._build_values(
                forged_record
            )
        )
        return (
            lambda: build_monitoring_report(**_report_kwargs(observation)),
            lambda: IU4RecoveryMonitoringReportV1(**constructor),
            lambda: IU4RecoveryMonitoringReportV1.build(**build_values),
            lambda: IU4RecoveryMonitoringReportV1.from_record(forged_record),
        )

    def test_group_close_and_reason_helpers_cannot_authorize_across_four_entries(self) -> None:
        import live_l1.state.paper_iu4_recovery_projection as module

        base = _observation()
        cases = (
            _rebuild_observation(
                base, "role_readiness", parent_guardian_ready=False
            ),
            _rebuild_observation(
                base, "runtime_close_fsm",
                close_prepare_event_id="UNEXPECTED-CLOSE-PREPARE",
            ),
            _rebuild_observation(
                base, "failstop_and_terminal_gap", failstop_asserted=True
            ),
        )
        originals = {
            name: module.__dict__[name] for name in (
                "_validate_observation_groups", "_classify_runtime_close_fsm",
                "_derived_monitoring_reasons",
            )
        }
        module.__dict__["_validate_observation_groups"] = lambda *_a, **_k: ("PASS",) * 12
        module.__dict__["_classify_runtime_close_fsm"] = lambda *_a, **_k: ("PASS", NONE)
        module.__dict__["_derived_monitoring_reasons"] = lambda **_k: ((), False)
        blocked = 0
        try:
            for case_index, observation in enumerate(cases):
                forged = self._forged_authorized_record(observation)
                for entry_index, invoke in enumerate(
                    self._four_entry_outcomes(observation, forged)
                ):
                    with self.subTest(case=case_index, entry=entry_index):
                        if entry_index == 0:
                            result = invoke()
                            self.assertEqual(result.overall_result, "FAIL")
                            self.assertEqual(
                                result.entry_capability_result, "BLOCKED"
                            )
                        else:
                            with self.assertRaises(IU4RecoveryProjectionError):
                                invoke()
                    blocked += 1
        finally:
            for name, value in originals.items():
                module.__dict__[name] = value
        self.assertEqual(blocked, 12)

    def test_global_builtin_factory_and_literal_alias_matrix_is_fail_closed(self) -> None:
        import live_l1.state.paper_iu4_recovery_projection as module

        original_error = IU4RecoveryProjectionError
        observation = _rebuild_observation(
            _observation(), "role_readiness", parent_guardian_ready=False
        )
        forged = self._forged_authorized_record(observation)
        boundaries = (
            {
                "_validate_observation_groups": lambda *_a, **_k: ("PASS",) * 12,
                "_classify_runtime_close_fsm": lambda *_a, **_k: ("PASS", NONE),
                "_derived_monitoring_reasons": lambda **_k: ((), False),
            },
            {
                "_sha": lambda value, *_a, **_k: value,
                "_integer": lambda value, *_a, **_k: value,
                "_hash": lambda _value: H,
                "NONE": "FORGED-NONE",
                "REPORT_GROUP_RESULT_FIELDS": (),
                "REPORT_GROUP_REASON_CODES": (),
            },
            {
                "dict": lambda *_a, **_k: {}, "set": lambda *_a: set(),
                "type": lambda *_a: IU4TerminalMonitoringObservationV1,
                "zip": lambda *_a: (), "any": lambda *_a: False,
                "getattr": lambda *_a: "PASS", "len": lambda *_a: 0,
                "tuple": lambda *_a: (),
            },
            {
                "fields": lambda *_a: (), "_ContentAddressedArtifact": object,
                "_hash": lambda _value: H,
                "_validate_observation_groups": lambda *_a, **_k: ("PASS",) * 12,
            },
            {"__BUILTINS__": True},
        )
        blocked = 0
        for boundary_index, replacements in enumerate(boundaries):
            module_originals = {}
            missing = []
            builtin_originals = {}
            try:
                if "__BUILTINS__" in replacements:
                    for name, value in (
                        ("any", lambda *_a: False),
                        ("getattr", lambda *_a: "PASS"),
                        ("len", lambda *_a: 0),
                        ("set", lambda *_a: {}),
                        ("tuple", lambda *_a: ()),
                        ("type", lambda *_a: IU4TerminalMonitoringObservationV1),
                    ):
                        builtin_originals[name] = builtins.__dict__[name]
                        builtins.__dict__[name] = value
                else:
                    for name, value in replacements.items():
                        if name in module.__dict__:
                            module_originals[name] = module.__dict__[name]
                        else:
                            missing.append(name)
                        module.__dict__[name] = value
                outcomes = self._four_entry_outcomes(observation, forged)
                for entry_index, invoke in enumerate(outcomes):
                    try:
                        result = invoke()
                    except original_error:
                        if entry_index == 0:
                            self.fail("normal Builder rejected the real failing Observation")
                    else:
                        if entry_index != 0:
                            self.fail("forged PASS survived immutable result authority")
                        self.assertEqual(result.overall_result, "FAIL")
                        self.assertEqual(result.entry_capability_result, "BLOCKED")
                    blocked += 1
            finally:
                for name, value in builtin_originals.items():
                    builtins.__dict__[name] = value
                for name, value in module_originals.items():
                    module.__dict__[name] = value
                for name in missing:
                    module.__dict__.pop(name, None)
        self.assertEqual(blocked, 20)


class I6MonitoringDataclassFactoryBoundaryTests(unittest.TestCase):
    def test_metadata_descriptor_and_factory_changes_cannot_alias_raw_content(self) -> None:
        import live_l1.state.paper_iu4_recovery_projection as module

        report_type = IU4RecoveryMonitoringReportV1
        base_observation = _observation()
        trusted = build_monitoring_report(**_report_kwargs(base_observation))
        trusted_record = trusted.to_record()
        changed_record = deepcopy(trusted_record)
        changed_record["economics_profile_id"] = "EP-CHANGED"
        changed_record = (
            I6MonitoringObservationContentBoundaryTests._readdress(
                changed_record
            )
        )
        changed_constructor = (
            I6MonitoringObservationContentBoundaryTests._constructor_values(
                changed_record
            )
        )
        changed_build = (
            I6MonitoringObservationContentBoundaryTests._build_values(
                changed_record
            )
        )

        class EconomicsDescriptor:
            def __get__(self, instance, _owner):
                if instance is None:
                    return self
                return "EP-FORGED-DESCRIPTOR"

            def __set__(self, instance, value):
                instance.__dict__["economics_profile_id"] = value

        boundaries = (
            "DATACLASS_FIELDS", "ANNOTATIONS", "CLASS_CONSTANTS",
            "FACTORY_GLOBALS", "FIELD_DESCRIPTOR",
        )
        authorized = 0
        collisions = 0
        for boundary in boundaries:
            with self.subTest(boundary=boundary), ExitStack() as stack:
                if boundary == "DATACLASS_FIELDS":
                    mutated = dict(report_type.__dataclass_fields__)
                    mutated.pop("economics_profile_id")
                    stack.enter_context(patch.object(
                        report_type, "__dataclass_fields__", mutated
                    ))
                elif boundary == "ANNOTATIONS":
                    mutated = dict(report_type.__annotations__)
                    mutated.pop("economics_profile_id")
                    stack.enter_context(patch.object(
                        report_type, "__annotations__", mutated
                    ))
                elif boundary == "CLASS_CONSTANTS":
                    for name, value in (
                        ("SCHEMA_VERSION", 99), ("ARTIFACT_TYPE", "forged"),
                        ("ID_FIELD", "economics_profile_id"),
                        ("FINGERPRINT_FIELD", "economics_profile_id"),
                        ("ID_PREFIX", "FORGED-"), ("TUPLE_FIELDS", frozenset()),
                    ):
                        stack.enter_context(patch.object(
                            report_type, name, value
                        ))
                elif boundary == "FACTORY_GLOBALS":
                    stack.enter_context(patch.object(
                        module, "fields", lambda *_a: ()
                    ))
                    stack.enter_context(patch.object(
                        module, "_hash", lambda _value: H
                    ))
                    stack.enter_context(patch.object(
                        module, "dict", lambda *_a, **_k: {}, create=True
                    ))
                else:
                    stack.enter_context(patch.object(
                        report_type, "economics_profile_id",
                        EconomicsDescriptor(), create=True,
                    ))
                builder_kwargs = _report_kwargs(base_observation)
                builder_kwargs["economics_profile_id"] = "EP-CHANGED"
                rows = (
                    build_monitoring_report(**builder_kwargs),
                    report_type(**changed_constructor),
                    report_type.build(**changed_build),
                    report_type.from_record(changed_record),
                )
                for row in rows:
                    record = row.to_record()
                    self.assertEqual(
                        record["economics_profile_id"], "EP-CHANGED"
                    )
                    self.assertEqual(
                        row.monitoring_report_id,
                        changed_record["monitoring_report_id"],
                    )
                    if row.monitoring_report_id == trusted.monitoring_report_id:
                        collisions += 1
                    authorized += 1
        self.assertEqual(authorized, 20)
        self.assertEqual(collisions, 0)

    def test_mutable_instance_dict_is_non_authoritative_and_storage_fails_closed(self) -> None:
        report = build_monitoring_report(**_report_kwargs(_observation()))
        record = report.to_record()

        class ReportSubclass(IU4RecoveryMonitoringReportV1):
            pass

        constructor = (
            I6MonitoringObservationContentBoundaryTests._constructor_values(
                record
            )
        )
        build_values = (
            I6MonitoringObservationContentBoundaryTests._build_values(record)
        )
        for invoke in (
            lambda: ReportSubclass(**constructor),
            lambda: ReportSubclass.build(**build_values),
            lambda: ReportSubclass.from_record(record),
        ):
            with self.assertRaises(IU4RecoveryProjectionError):
                invoke()

        raw = object.__getattribute__(report, "__dict__")
        raw["unexpected_authority_field"] = "FORGED"
        with self.assertRaises(IU4RecoveryProjectionError):
            report.to_record()
        raw.clear()
        raw["economics_profile_id"] = "EP-CHANGED-WITHOUT-READDRESS"
        with self.assertRaises(IU4RecoveryProjectionError):
            report.to_record()
        raw.clear()
        self.assertEqual(report.to_record(), record)

        storage = object.__getattribute__(report, "_authority_storage")
        changed = list(storage)
        changed[19] = "EP-CHANGED-WITHOUT-READDRESS"
        with self.assertRaises(AttributeError):
            object.__setattr__(report, "_authority_storage", tuple(changed))
        self.assertEqual(report.to_record(), record)


class I6MonitoringFactoryExactTypeBoundaryTests(unittest.TestCase):
    def test_own_constructor_subclass_inherited_factories_reject_before_values(self) -> None:
        report = build_monitoring_report(**_report_kwargs(_observation()))
        record = report.to_record()
        constructor_calls = []
        public_value_calls = []

        class GuardedPublicValue:
            def __iter__(self):
                public_value_calls.append("iterate")
                return iter(())

            def __eq__(self, _other):
                public_value_calls.append("compare")
                return False

            def __hash__(self):
                public_value_calls.append("hash")
                return 0

            def __str__(self):
                public_value_calls.append("string")
                return "guarded"

        class OwnConstructorSubclass(IU4RecoveryMonitoringReportV1):
            def __new__(cls, **_values):
                constructor_calls.append("new")
                raise AssertionError("subclass construction must not be delegated")

            def __init__(self, **_values):
                constructor_calls.append("init")

        self.assertNotIn("build", OwnConstructorSubclass.__dict__)
        self.assertNotIn("from_record", OwnConstructorSubclass.__dict__)

        build_values = (
            I6MonitoringObservationContentBoundaryTests._build_values(record)
        )
        with self.assertRaises(IU4RecoveryProjectionError) as build_rejection:
            OwnConstructorSubclass.build(**build_values)
        self.assertEqual(
            build_rejection.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )
        self.assertEqual(constructor_calls, [])

        with self.assertRaises(IU4RecoveryProjectionError) as record_rejection:
            OwnConstructorSubclass.from_record(record)
        self.assertEqual(
            record_rejection.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )
        self.assertEqual(constructor_calls, [])

        guarded_build_values = dict(build_values)
        guarded_build_values["economics_profile_id"] = GuardedPublicValue()
        with self.assertRaises(IU4RecoveryProjectionError) as guarded_build:
            OwnConstructorSubclass.build(**guarded_build_values)
        self.assertEqual(
            guarded_build.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )

        guarded_record = dict(record)
        guarded_record["economics_profile_id"] = GuardedPublicValue()
        with self.assertRaises(IU4RecoveryProjectionError) as guarded_from_record:
            OwnConstructorSubclass.from_record(guarded_record)
        self.assertEqual(
            guarded_from_record.exception.reason_code,
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
        )
        self.assertEqual(constructor_calls, [])
        self.assertEqual(public_value_calls, [])

    def test_base_factories_use_exact_authorized_result_type(self) -> None:
        report_type = IU4RecoveryMonitoringReportV1
        record = build_monitoring_report(**_report_kwargs(_observation())).to_record()
        build_values = (
            I6MonitoringObservationContentBoundaryTests._build_values(record)
        )

        class ResultSubclass(report_type):
            pass

        def replaced_public_constructor(_cls, **_values):
            return tuple.__new__(ResultSubclass)

        with patch.object(report_type, "__new__", replaced_public_constructor):
            built = report_type.build(**build_values)
            reconstructed = report_type.from_record(record)

        self.assertIs(type(built), report_type)
        self.assertIs(type(reconstructed), report_type)
        self.assertEqual(built.to_record(), record)
        self.assertEqual(reconstructed.to_record(), record)


class I6MonitoringBuiltinCanonicalityBoundaryTests(unittest.TestCase):
    def test_public_nested_records_accept_dict_list_and_reject_internal_tags(self) -> None:
        observation = _observation()
        report = build_monitoring_report(**_report_kwargs(observation))
        record = report.to_record()
        constructor = I6MonitoringObservationContentBoundaryTests._constructor_values(
            record
        )
        build_values = I6MonitoringObservationContentBoundaryTests._build_values(
            record
        )
        accepted = (
            report,
            IU4RecoveryMonitoringReportV1(**constructor),
            IU4RecoveryMonitoringReportV1.build(**build_values),
            IU4RecoveryMonitoringReportV1.from_record(record),
        )
        self.assertTrue(all(row.to_record() == record for row in accepted))

        tagged = object.__getattribute__(report, "_authority_storage")[49]
        tagged_record = dict(record)
        tagged_record["terminal_monitoring_observation_record"] = tagged
        tagged_constructor = (
            I6MonitoringObservationContentBoundaryTests._constructor_values(
                tagged_record
            )
        )
        tagged_build = I6MonitoringObservationContentBoundaryTests._build_values(
            tagged_record
        )
        tagged_observation = _observation()
        object.__getattribute__(tagged_observation, "__dict__")[
            "role_readiness"
        ] = tagged
        for invoke in (
            lambda: build_monitoring_report(**_report_kwargs(tagged_observation)),
            lambda: IU4RecoveryMonitoringReportV1(**tagged_constructor),
            lambda: IU4RecoveryMonitoringReportV1.build(**tagged_build),
            lambda: IU4RecoveryMonitoringReportV1.from_record(tagged_record),
        ):
            with self.subTest(entry=invoke), self.assertRaises(
                IU4RecoveryProjectionError
            ):
                invoke()

    def test_recursive_nonbuiltin_value_is_rejected_before_protocol_use(self) -> None:
        class NonBuiltinValue:
            def __getattribute__(self, name):
                if name == "__class__":
                    raise AssertionError("untrusted class protocol was used")
                return object.__getattribute__(self, name)

            def __iter__(self):
                raise AssertionError("untrusted iteration protocol was used")

            def __eq__(self, _other):
                raise AssertionError("untrusted equality protocol was used")

            def __lt__(self, _other):
                raise AssertionError("untrusted ordering protocol was used")

            def __format__(self, _spec):
                raise AssertionError("untrusted formatting protocol was used")

        observation = _observation()
        object.__getattribute__(observation, "__dict__")[
            "role_readiness"
        ] = NonBuiltinValue()
        report = build_monitoring_report(**_report_kwargs(_observation()))
        record = report.to_record()
        record["terminal_monitoring_observation_record"][
            "role_readiness"
        ] = NonBuiltinValue()
        constructor = I6MonitoringObservationContentBoundaryTests._constructor_values(
            record
        )
        build_values = I6MonitoringObservationContentBoundaryTests._build_values(
            record
        )
        for invoke in (
            lambda: build_monitoring_report(**_report_kwargs(observation)),
            lambda: IU4RecoveryMonitoringReportV1(**constructor),
            lambda: IU4RecoveryMonitoringReportV1.build(**build_values),
            lambda: IU4RecoveryMonitoringReportV1.from_record(record),
        ):
            with self.subTest(entry=invoke), self.assertRaises(
                IU4RecoveryProjectionError
            ):
                invoke()

    def test_class_descriptor_key_value_element_and_rejection_paths_fail_closed(self) -> None:
        class DescriptorBoundary:
            __hash__ = object.__hash__

            @property
            def __class__(self):
                raise AssertionError("untrusted class descriptor was used")

            def __iter__(self):
                raise AssertionError("untrusted iteration was used")

            def __eq__(self, _other):
                raise AssertionError("untrusted comparison was used")

            def __lt__(self, _other):
                raise AssertionError("untrusted ordering was used")

            def __format__(self, _spec):
                raise AssertionError("untrusted formatting was used")

        def place(container, boundary, location):
            observation_record = container[
                "terminal_monitoring_observation_record"
            ]
            if location == "KEY":
                observation_record["role_readiness"][boundary] = True
            elif location == "VALUE":
                observation_record["role_readiness"][
                    "parent_guardian_ready"
                ] = boundary
            elif location == "ELEMENT":
                observation_record["control_word_and_memfd"][
                    "memfd_create_flags"
                ] = [boundary]
            else:
                observation_record["role_readiness"] = boundary

        for location in ("KEY", "VALUE", "ELEMENT", "REJECTION"):
            boundary = DescriptorBoundary()

            observation = _observation()
            observation_wrapper = {
                "terminal_monitoring_observation_record": object.__getattribute__(
                    observation, "__dict__"
                )
            }
            place(observation_wrapper, boundary, location)

            record = build_monitoring_report(
                **_report_kwargs(_observation())
            ).to_record()
            place(record, boundary, location)
            constructor = (
                I6MonitoringObservationContentBoundaryTests._constructor_values(
                    record
                )
            )
            build_values = (
                I6MonitoringObservationContentBoundaryTests._build_values(
                    record
                )
            )
            invocations = (
                ("BUILDER", lambda: build_monitoring_report(
                    **_report_kwargs(observation)
                )),
                ("CONSTRUCTOR", lambda: IU4RecoveryMonitoringReportV1(
                    **constructor
                )),
                ("INHERITED_BUILD", lambda: IU4RecoveryMonitoringReportV1.build(
                    **build_values
                )),
                ("FROM_RECORD", lambda: IU4RecoveryMonitoringReportV1.from_record(
                    record
                )),
            )
            for entry, invoke in invocations:
                with self.subTest(
                    location=location, entry=entry
                ), self.assertRaises(IU4RecoveryProjectionError):
                    invoke()

    def test_bytecode_establishes_exact_type_before_untrusted_protocol_use(self) -> None:
        module = __import__(
            "live_l1.state.paper_iu4_recovery_projection", fromlist=["*"]
        )
        entry_rows = (
            (build_monitoring_report.__func__, "observation"),
            (IU4RecoveryMonitoringReportV1.__new__.__func__, "cls"),
            (IU4RecoveryMonitoringReportV1._validate_specific, "subject"),
            (IU4RecoveryMonitoringReportV1.build.__func__, "values"),
            (IU4RecoveryMonitoringReportV1.from_record.__func__, "record"),
            (IU4RecoveryMonitoringReportV1.__getattribute__, "name"),
        )
        forbidden_before_type = {
            "LOAD_ATTR", "LOAD_METHOD", "BINARY_SUBSCR", "GET_ITER",
            "CONTAINS_OP", "COMPARE_OP", "FORMAT_VALUE",
        }
        for function, parameter in entry_rows:
            instructions = tuple(dis.get_instructions(function))
            self.assertNotIn(
                "__mro__", {instruction.argval for instruction in instructions}
            )
            first_parameter = next(
                index for index, instruction in enumerate(instructions)
                if instruction.opname in {
                    "LOAD_FAST", "LOAD_FAST_BORROW", "LOAD_FAST_CHECK",
                    "LOAD_DEREF",
                }
                and instruction.argval == parameter
            )
            first_call = next(
                index for index in range(first_parameter, len(instructions))
                if instructions[index].opname == "CALL"
            )
            self.assertTrue(any(
                instruction.argval == "exact_type"
                for instruction in instructions[:first_parameter]
            ))
            self.assertTrue(all(
                instruction.opname not in forbidden_before_type
                for instruction in instructions[
                    first_parameter:first_call
                ]
            ))
        constructor_authority = IU4RecoveryMonitoringReportV1.__new__.__self__
        self.assertIs(type(constructor_authority), tuple)
        self.assertIs(constructor_authority[0], IU4RecoveryMonitoringReportV1)
        self.assertIs(
            constructor_authority[1],
            module._immutable_monitoring_report_authority,
        )


class I6MonitoringSerializationAuthorityBoundaryTests(unittest.TestCase):
    OBSERVATION_FIELDS = (
        "schema_version", "artifact_type",
        "terminal_monitoring_observation_id", "runtime_session_id",
        "runtime_session_open_record_fingerprint", "authority_generation_id",
        "authority_commit_anchor", "atomic_root_fingerprint",
        "source_collector_id", "source_evidence_id", "source_evidence_sha256",
        "observation_sequence", "observed_at_utc", "role_readiness",
        "lease_and_self_death", "pidfd_targets", "control_word_and_memfd",
        "signal_envelope", "runtime_channels", "seccomp_lsm_capability",
        "runtime_close_fsm", "heartbeat_and_budgets",
        "failstop_and_terminal_gap", "completion_provenance",
        "safety_resource_schema", "observation_fingerprint",
    )
    REPORT_FIELDS = (
        "schema_version", "artifact_type", "monitoring_report_id",
        "runtime_session_id", "runtime_session_open_record_fingerprint",
        "authority_generation_id", "authority_commit_anchor", "owner_epoch",
        "report_operation", "atomic_root_fingerprint",
        "lifecycle_root_inventory_fingerprint",
        "atomic_root_inventory_fingerprint",
        "projection_root_inventory_fingerprint", "authorization_valid",
        "runtime_profile_id", "runtime_profile_fingerprint",
        "runtime_profile_anchor_record", "profile_registry_id",
        "profile_registry_fingerprint", "economics_profile_id",
        "economics_profile_fingerprint", "entry_throttle_profile_id",
        "entry_throttle_profile_fingerprint", "runtime_control_fingerprint",
        "lifecycle_ledger_tip_event_id", "lifecycle_ledger_tip_fingerprint",
        "open_prepare_count", "runtime_session_status",
        "handoff_or_genesis_manifest_id",
        "handoff_or_genesis_manifest_fingerprint", "atomic_journal_sequence",
        "atomic_journal_head", "atomic_snapshot_fingerprint",
        "authority_root_ancestry_result", "projection_cursor_id",
        "projection_cursor_fingerprint", "projection_cursor_sequence",
        "projection_cursor_journal_head", "projection_lag_transactions",
        "s2_fingerprint", "account_fingerprint", "throttle_fingerprint",
        "loss_cluster_fingerprint", "s4_fingerprint",
        "entry_quote_fingerprint", "progress_cursor_fingerprint",
        "terminal_gap_status", "terminal_monitoring_observation_id",
        "terminal_monitoring_observation_fingerprint",
        "terminal_monitoring_observation_record", "role_readiness_result",
        "lease_and_self_death_result", "pidfd_targets_result",
        "control_word_and_memfd_result", "signal_envelope_result",
        "runtime_channels_result", "seccomp_lsm_capability_result",
        "runtime_close_fsm_record", "runtime_close_fsm_result",
        "runtime_close_fsm_reason_code", "heartbeat_and_budgets_result",
        "failstop_and_terminal_gap_result", "completion_provenance_result",
        "safety_resource_schema_result", "entry_capability_result",
        "exit_capability_result", "overall_result", "reason_codes",
        "reported_at_utc", "report_fingerprint",
    )

    def test_literal_field_counts_order_and_reverse_input_order(self) -> None:
        observation_record = _observation().to_record()
        report_record = build_monitoring_report(
            **_report_kwargs(_observation())
        ).to_record()
        self.assertEqual(len(self.OBSERVATION_FIELDS), 26)
        self.assertEqual(tuple(observation_record), self.OBSERVATION_FIELDS)
        self.assertEqual(len(self.REPORT_FIELDS), 70)
        self.assertEqual(tuple(report_record), self.REPORT_FIELDS)

        reverse_record = dict(reversed(tuple(report_record.items())))
        reconstructed = IU4RecoveryMonitoringReportV1.from_record(reverse_record)
        self.assertEqual(tuple(reconstructed.to_record()), self.REPORT_FIELDS)
        self.assertEqual(reconstructed.to_record(), report_record)

    def test_to_record_revalidates_value_cross_binding_id_and_fingerprint(self) -> None:
        report = build_monitoring_report(**_report_kwargs(_observation()))
        record = report.to_record()
        mutable = object.__getattribute__(report, "__dict__")
        mutable["economics_profile_id"] = "EP-NONAUTHORITATIVE"
        with self.assertRaises(IU4RecoveryProjectionError):
            report.to_record()
        mutable.clear()
        storage = object.__getattribute__(report, "_authority_storage")
        mutations = (
            (19, "EP-INCONSISTENT"),
            (3, "SESSION-INCONSISTENT"),
            (47, "OBSERVATION-INCONSISTENT"),
            (58, storage[49]),
            (2, "IU4-RECOVERY-MONITORING-REPORT-V1-" + H),
            (69, H),
        )
        for index, value in mutations:
            with self.subTest(index=index):
                changed = list(storage)
                changed[index] = value
                with self.assertRaises(AttributeError):
                    object.__setattr__(
                        report, "_authority_storage", tuple(changed)
                    )
                self.assertEqual(report.to_record(), record)

        alternative_kwargs = _report_kwargs(_observation())
        alternative_kwargs["economics_profile_id"] = "EP-CONSISTENT-ALTERNATIVE"
        alternative = build_monitoring_report(**alternative_kwargs)
        alternative_storage = object.__getattribute__(
            alternative, "_authority_storage"
        )
        self.assertEqual(len(alternative_storage), 70)
        self.assertNotEqual(alternative.to_record(), record)
        with self.assertRaises(AttributeError):
            object.__setattr__(
                report, "_authority_storage", alternative_storage
            )
        self.assertEqual(
            object.__getattribute__(report, "_authority_storage"), storage
        )
        self.assertEqual(report.monitoring_report_id, record["monitoring_report_id"])
        self.assertEqual(report.report_fingerprint, record["report_fingerprint"])
        self.assertEqual(report.to_record(), record)

        for name in self.REPORT_FIELDS:
            with self.subTest(field=name):
                before = getattr(report, name)
                object.__setattr__(report, name, "INCONSISTENT")
                self.assertEqual(getattr(report, name), before)
                with self.assertRaises(IU4RecoveryProjectionError):
                    report.to_record()
                object.__getattribute__(report, "__dict__").clear()
        self.assertEqual(report.to_record(), record)


class I6RecoveryLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        from tests.live_l1.test_paper_atomic_coordinator_v2 import AtomicV2Tests

        self.fixture = AtomicV2Tests(methodName="test_progress_changes_only_cursor_and_bound_risk")
        self.fixture.setUp()
        self.coordinator = self.fixture._make_coordinator(self.fixture.temp / "i6-lifecycle-atomic")
        self.ledger = IU4LifecycleLedgerV1(self.fixture.temp / "i6-lifecycle-ledger")
        self.orchestrator = _orchestrator(self.ledger, self.coordinator)
        manifest = _genesis_manifest(self.coordinator, self.fixture.initial_state)
        self.genesis = self.orchestrator.atomic_genesis(
            manifest=manifest, target_state_template=self.fixture.initial_state,
            prepare_event_id="I6-LIFECYCLE-GENESIS-PREPARE",
            commit_event_id="I6-LIFECYCLE-GENESIS-COMMIT",
        )

    def tearDown(self) -> None:
        self.fixture.tearDown()

    def _authorization(self, operation: str):
        return _restart_authorization(
            self.coordinator, self.ledger, self.fixture, operation
        )

    def test_recover_and_restart_consumes_once_materializes_without_transaction(self) -> None:
        authorization = self._authorization("RECOVER_AND_RESTART")
        before_transactions = len(self.coordinator._transactions())
        result = self.orchestrator.recover_and_restart(
            authorization=authorization, consumption_event_id="I6-RECOVERY-CONSUME",
            materialization_event_id="I6-RECOVERY-MATERIALIZE",
            consumption_timestamp_utc=UTC,
            expected_startup_attempt_id="START-RECOVER_AND_RESTART",
        )
        self.assertEqual(result.outcome, "RECOVERY_COMPLETE_LOOP_NOT_AUTHORIZED")
        self.assertEqual(len(self.coordinator._transactions()), before_transactions)
        with self.assertRaises(IU4RecoveryProjectionError) as caught:
            self.orchestrator.recover_and_restart(
                authorization=authorization, consumption_event_id="I6-RECOVERY-CONSUME-2",
                materialization_event_id="I6-RECOVERY-MATERIALIZE-2",
                consumption_timestamp_utc=UTC,
                expected_startup_attempt_id="START-RECOVER_AND_RESTART",
            )
        self.assertEqual(caught.exception.reason_code, "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH")

    def test_restart_consumption_resource_error_is_classified(self) -> None:
        authorization = self._authorization("RECOVER_AND_RESTART")
        before = self.ledger.view().record_count
        with patch.object(
            self.ledger,
            "consume_restart_authorization",
            side_effect=OSError(errno.ENOSPC, "synthetic full device"),
        ):
            with self.assertRaises(IU4RecoveryProjectionError) as caught:
                self.orchestrator.consume_restart_authorization(
                    authorization=authorization,
                    operation="RECOVER_AND_RESTART",
                    consumption_event_id="I6-RESOURCE-CONSUME",
                    consumption_timestamp_utc=UTC,
                    expected_startup_attempt_id="START-RECOVER_AND_RESTART",
                )
        self.assertEqual(caught.exception.reason_code, "PEE_IU4_RESOURCE_EXHAUSTED")
        self.assertEqual(self.ledger.view().record_count, before)

    def test_restart_preconsumption_lifecycle_view_resources_are_classified_without_mutation(self) -> None:
        authorization = self._authorization("RECOVER_AND_RESTART")
        before_ledger = self.ledger.view().record_count
        before_state = self.coordinator.state_path.read_bytes()
        before_transactions = len(self.coordinator._transactions())
        for failure in (
            OSError(errno.ENOSPC, "synthetic full device"),
            MemoryError("synthetic memory exhaustion"),
            _runtime_resource_error(OSError(errno.EIO, "wrapped view I/O")),
            _runtime_resource_error(MemoryError("wrapped view memory")),
        ):
            with self.subTest(failure=type(failure).__name__), patch.object(
                self.ledger, "view", side_effect=failure
            ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                self.orchestrator.consume_restart_authorization(
                    authorization=authorization,
                    operation="RECOVER_AND_RESTART",
                    consumption_event_id="I6-PRECONSUMPTION-VIEW",
                    consumption_timestamp_utc=UTC,
                    expected_startup_attempt_id="START-RECOVER_AND_RESTART",
                )
            self.assertEqual(
                caught.exception.reason_code, "PEE_IU4_RESOURCE_EXHAUSTED"
            )
            self.assertEqual(self.ledger.view().record_count, before_ledger)
            self.assertEqual(self.coordinator.state_path.read_bytes(), before_state)
            self.assertEqual(
                len(self.coordinator._transactions()), before_transactions
            )

    def test_nested_consumption_resource_causes_are_stable_and_preterminally_null(self) -> None:
        for resource_error in (
            OSError(errno.ENOSPC, "nested device exhaustion"),
            MemoryError("nested memory exhaustion"),
        ):
            authorization = self._authorization("RECOVER_AND_RESTART")
            before_records = tuple(record.to_mapping() for record in self.ledger.records())
            before_state = self.coordinator.state_path.read_bytes()
            before_transactions = tuple(self.coordinator._transactions())
            nested = _nested_resource_error(resource_error)
            with self.subTest(resource=type(resource_error).__name__), patch.object(
                self.ledger, "consume_restart_authorization", side_effect=nested
            ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                self.orchestrator.consume_restart_authorization(
                    authorization=authorization,
                    operation="RECOVER_AND_RESTART",
                    consumption_event_id="I6-NESTED-CONSUMPTION",
                    consumption_timestamp_utc=UTC,
                    expected_startup_attempt_id="START-RECOVER_AND_RESTART",
                )
            self.assertEqual(
                caught.exception.reason_code, "PEE_IU4_RESOURCE_EXHAUSTED"
            )
            self.assertEqual(
                tuple(record.to_mapping() for record in self.ledger.records()),
                before_records,
            )
            self.assertEqual(self.coordinator.state_path.read_bytes(), before_state)
            self.assertEqual(tuple(self.coordinator._transactions()), before_transactions)

    def test_nested_gap_publication_resource_is_postterminally_exact_and_retryable(self) -> None:
        authorization, _anchor_value, proof, open_event_id, open_record = (
            _terminal_gap_material(
                self.coordinator, self.ledger, self.fixture,
                suffix="NESTED-GAP-PUBLICATION",
            )
        )
        consumption = self.orchestrator.consume_restart_authorization(
            authorization=authorization,
            operation="RECONCILE_TERMINAL_GAP",
            consumption_event_id="I6-NESTED-GAP-CONSUME",
            consumption_timestamp_utc=UTC,
            expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
        )
        before_count = self.ledger.view().record_count
        nested = _nested_resource_error(OSError(errno.ENOSPC, "nested gap full"))
        call = dict(
            consumption=consumption, authorization=authorization, proof=proof,
            open_session_id="SESSION-1",
            runtime_session_open_event_id=open_event_id,
            runtime_session_open_record_fingerprint=open_record.record_fingerprint,
            runtime_session_open_journal_head=EMPTY,
            terminal_event_id="I6-NESTED-GAP-KILL",
            gap_event_id="I6-NESTED-GAP-RECORD",
            consumption_timestamp_utc=UTC, fault_point="",
        )
        with patch.object(
            self.orchestrator, "_append_lifecycle_record_with_lock_held",
            side_effect=nested,
        ), self.assertRaises(IU4RecoveryProjectionError) as caught:
            self.orchestrator._terminal_kill_and_gap_under_lifecycle_lock(**call)
        self.assertEqual(
            caught.exception.reason_code, "PEE_IU4_RESOURCE_EXHAUSTED"
        )
        self.assertEqual(self.ledger.view().record_count, before_count)
        self.assertEqual(self.ledger.view().open_runtime_session_id, "SESSION-1")
        transactions = self.coordinator._transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][1].transaction_event_id, "I6-NESTED-GAP-KILL")
        self.assertEqual(transactions[0][1].state_after.risk.kill_level, "EMERGENCY")
        self.assertEqual(
            [
                record.record_type for record in self.ledger.records()
                if record.record_type == "TERMINAL_GAP_RECONCILIATION"
            ],
            [],
        )

        committed, gap = self.orchestrator._terminal_kill_and_gap_under_lifecycle_lock(
            **call
        )
        self.assertEqual(committed.state.risk.kill_level, "EMERGENCY")
        self.assertEqual(gap.record_type, "TERMINAL_GAP_RECONCILIATION")
        self.assertEqual(len(self.coordinator._transactions()), 1)
        self.assertEqual(self.ledger.view().record_count, before_count + 1)
        self.assertEqual(self.ledger.view().open_runtime_session_id, "")

    def test_terminal_lifecycle_unlock_and_close_resources_preserve_kill_and_gap(self) -> None:
        for cleanup_kind in ("UNLOCK", "CLOSE"):
            for nested in (False, True):
                label = f"{cleanup_kind}-{'NESTED' if nested else 'DIRECT'}"
                coordinator = self.fixture._make_coordinator(
                    self.fixture.temp / f"terminal-cleanup-atomic-{label}"
                )
                ledger = IU4LifecycleLedgerV1(
                    self.fixture.temp / f"terminal-cleanup-ledger-{label}"
                )
                orchestrator = _orchestrator(ledger, coordinator)
                orchestrator.atomic_genesis(
                    manifest=_genesis_manifest(
                        coordinator, self.fixture.initial_state,
                        suffix=f"TERMINAL-CLEANUP-{label}",
                    ),
                    target_state_template=self.fixture.initial_state,
                    prepare_event_id=f"TERMINAL-CLEANUP-GENESIS-PREPARE-{label}",
                    commit_event_id=f"TERMINAL-CLEANUP-GENESIS-COMMIT-{label}",
                )
                authorization, _anchor_value, proof, open_event_id, open_record = (
                    _terminal_gap_material(
                        coordinator, ledger, self.fixture, suffix=label
                    )
                )
                consumption = orchestrator.consume_restart_authorization(
                    authorization=authorization,
                    operation="RECONCILE_TERMINAL_GAP",
                    consumption_event_id=f"TERMINAL-CLEANUP-CONSUME-{label}",
                    consumption_timestamp_utc=UTC,
                    expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
                )
                before_count = ledger.view().record_count
                call = dict(
                    consumption=consumption, authorization=authorization,
                    proof=proof, open_session_id="SESSION-1",
                    runtime_session_open_event_id=open_event_id,
                    runtime_session_open_record_fingerprint=(
                        open_record.record_fingerprint
                    ),
                    runtime_session_open_journal_head=EMPTY,
                    terminal_event_id=f"TERMINAL-CLEANUP-KILL-{label}",
                    gap_event_id=f"TERMINAL-CLEANUP-GAP-{label}",
                    consumption_timestamp_utc=UTC, fault_point="",
                )
                original_flock = __import__("fcntl").flock
                original_close = os.close
                state = {"lifecycle_fd": None, "failed": False}

                def flock_fault(descriptor, operation):
                    if (
                        operation == __import__("fcntl").LOCK_EX
                        and state["lifecycle_fd"] is None
                    ):
                        state["lifecycle_fd"] = descriptor
                    if (
                        cleanup_kind == "UNLOCK"
                        and descriptor == state["lifecycle_fd"]
                        and operation == __import__("fcntl").LOCK_UN
                        and not state["failed"]
                    ):
                        state["failed"] = True
                        failure = OSError(errno.EIO, "terminal unlock failure")
                        raise (
                            _nested_resource_error(failure)
                            if nested else failure
                        )
                    return original_flock(descriptor, operation)

                def close_fault(descriptor):
                    if (
                        cleanup_kind == "CLOSE"
                        and descriptor == state["lifecycle_fd"]
                        and not state["failed"]
                    ):
                        state["failed"] = True
                        failure = MemoryError("terminal close failure")
                        raise (
                            _runtime_resource_error(failure)
                            if nested else failure
                        )
                    return original_close(descriptor)

                try:
                    with self.subTest(label=label), patch(
                        "live_l1.state.paper_iu4_recovery_projection.fcntl.flock",
                        side_effect=flock_fault,
                    ), patch(
                        "live_l1.state.paper_iu4_recovery_projection.os.close",
                        side_effect=close_fault,
                    ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                        orchestrator._terminal_kill_and_gap_under_lifecycle_lock(
                            **call
                        )
                    self.assertEqual(
                        caught.exception.reason_code,
                        "PEE_IU4_RESOURCE_EXHAUSTED",
                    )
                finally:
                    if cleanup_kind == "CLOSE" and state["lifecycle_fd"] is not None:
                        try:
                            original_close(state["lifecycle_fd"])
                        except OSError:
                            pass
                self.assertTrue(state["failed"])
                self.assertEqual(ledger.view().record_count, before_count + 1)
                self.assertEqual(ledger.view().open_runtime_session_id, "")
                transactions = coordinator._transactions()
                self.assertEqual(len(transactions), 1)
                self.assertEqual(
                    transactions[0][1].transaction_event_id,
                    f"TERMINAL-CLEANUP-KILL-{label}",
                )
                self.assertEqual(
                    transactions[0][1].state_after.risk.kill_level, "EMERGENCY"
                )
                gaps = [
                    record for record in ledger.records()
                    if record.record_type == "TERMINAL_GAP_RECONCILIATION"
                ]
                self.assertEqual(len(gaps), 1)
                self.assertEqual(
                    gaps[0].lifecycle_event_id,
                    f"TERMINAL-CLEANUP-GAP-{label}",
                )

    def test_terminal_cleanup_resource_does_not_replace_primary_extension_failure(self) -> None:
        authorization, _anchor_value, proof, open_event_id, open_record = (
            _terminal_gap_material(
                self.coordinator, self.ledger, self.fixture,
                suffix="PRIMARY-CLEANUP",
            )
        )
        consumption = self.orchestrator.consume_restart_authorization(
            authorization=authorization,
            operation="RECONCILE_TERMINAL_GAP",
            consumption_event_id="PRIMARY-CLEANUP-CONSUME",
            consumption_timestamp_utc=UTC,
            expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
        )
        self.ledger.append(
            record_type="RECOVERY_MATERIALIZATION",
            lifecycle_event_id="PRIMARY-CLEANUP-FOREIGN-EXTENSION",
            payload={"foreign": True},
        )
        before_state = self.coordinator.state_path.read_bytes()
        before_transactions = tuple(self.coordinator._transactions())
        original_flock = __import__("fcntl").flock

        def unlock_fault(descriptor, operation):
            if operation == __import__("fcntl").LOCK_UN:
                raise _runtime_resource_error(
                    OSError(errno.EIO, "secondary cleanup failure")
                )
            return original_flock(descriptor, operation)

        with patch(
            "live_l1.state.paper_iu4_recovery_projection.fcntl.flock",
            side_effect=unlock_fault,
        ), self.assertRaises(IU4RecoveryProjectionError) as caught:
            self.orchestrator._terminal_kill_and_gap_under_lifecycle_lock(
                consumption=consumption, authorization=authorization,
                proof=proof, open_session_id="SESSION-1",
                runtime_session_open_event_id=open_event_id,
                runtime_session_open_record_fingerprint=(
                    open_record.record_fingerprint
                ),
                runtime_session_open_journal_head=EMPTY,
                terminal_event_id="PRIMARY-CLEANUP-KILL",
                gap_event_id="PRIMARY-CLEANUP-GAP",
                consumption_timestamp_utc=UTC, fault_point="",
            )
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_LIFECYCLE_EXTENSION_INVALID",
        )
        self.assertEqual(self.coordinator.state_path.read_bytes(), before_state)
        self.assertEqual(tuple(self.coordinator._transactions()), before_transactions)
        self.assertEqual(self.ledger.view().open_runtime_session_id, "SESSION-1")

    def test_terminal_lifecycle_lock_resource_error_is_classified_before_kill(self) -> None:
        authorization, _anchor_value, proof, open_event_id, open_record = (
            _terminal_gap_material(
                self.coordinator, self.ledger, self.fixture, suffix="RESOURCE-LOCK"
            )
        )
        consumption = self.orchestrator.consume_restart_authorization(
            authorization=authorization,
            operation="RECONCILE_TERMINAL_GAP",
            consumption_event_id="I6-RESOURCE-LOCK-CONSUME",
            consumption_timestamp_utc=UTC,
            expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
        )
        before_ledger = self.ledger.view().record_count
        before_state = self.coordinator.state_path.read_bytes()
        before_transactions = len(self.coordinator._transactions())
        for failure in (
            OSError(errno.ENOSPC, "synthetic full device"),
            MemoryError("synthetic memory exhaustion"),
            _runtime_resource_error(OSError(errno.EIO, "wrapped init I/O")),
            _runtime_resource_error(MemoryError("wrapped init memory")),
        ):
            with self.subTest(failure=type(failure).__name__), patch.object(
                self.ledger, "initialize", side_effect=failure
            ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                self.orchestrator._terminal_kill_and_gap_under_lifecycle_lock(
                    consumption=consumption,
                    authorization=authorization,
                    proof=proof,
                    open_session_id="SESSION-1",
                    runtime_session_open_event_id=open_event_id,
                    runtime_session_open_record_fingerprint=(
                        open_record.record_fingerprint
                    ),
                    runtime_session_open_journal_head=EMPTY,
                    terminal_event_id="I6-RESOURCE-LOCK-KILL",
                    gap_event_id="I6-RESOURCE-LOCK-GAP",
                    consumption_timestamp_utc=UTC,
                    fault_point="",
                )
            self.assertEqual(
                caught.exception.reason_code, "PEE_IU4_RESOURCE_EXHAUSTED"
            )
            self.assertEqual(self.ledger.view().record_count, before_ledger)
            self.assertEqual(self.coordinator.state_path.read_bytes(), before_state)
            self.assertEqual(
                len(self.coordinator._transactions()), before_transactions
            )

    def test_terminal_preconsumption_lifecycle_reads_are_classified_without_follow_on_mutation(self) -> None:
        authorization, anchor, proof, open_event_id, open_record = (
            _terminal_gap_material(
                self.coordinator, self.ledger, self.fixture,
                suffix="RESOURCE-PRECONSUMPTION",
            )
        )
        kwargs = dict(
            authorization=authorization, anchor=anchor, proof=proof,
            expected_death_trust_anchor_id=anchor.trust_anchor_id,
            expected_death_trust_anchor_fingerprint=anchor.trust_anchor_fingerprint,
            expected_approval_fingerprint=H,
            expected_trusted_anchor_registry_fingerprint=H2,
            consumption_event_id="I6-RESOURCE-PRECONSUMPTION-CONSUME",
            terminal_event_id="I6-RESOURCE-PRECONSUMPTION-KILL",
            gap_event_id="I6-RESOURCE-PRECONSUMPTION-GAP",
            consumption_timestamp_utc=UTC,
            runtime_session_open_event_id=open_event_id,
            runtime_session_open_record_fingerprint=open_record.record_fingerprint,
            runtime_session_open_journal_head=EMPTY,
            expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
            expected_journal_root_fingerprint=H,
            expected_old_worker_id="WORKER-1",
            expected_old_worker_boot_id="BOOT-1",
        )
        before_ledger = self.ledger.view().record_count
        before_state = self.coordinator.state_path.read_bytes()
        before_transactions = len(self.coordinator._transactions())
        for method in ("records", "view"):
            for failure in (
                OSError(errno.EIO, "synthetic Lifecycle read failure"),
                MemoryError("synthetic Lifecycle read exhaustion"),
                _runtime_resource_error(
                    OSError(errno.EIO, "wrapped Lifecycle read failure")
                ),
                _runtime_resource_error(
                    MemoryError("wrapped Lifecycle read exhaustion")
                ),
            ):
                with self.subTest(
                    method=method, failure=type(failure).__name__
                ), patch.object(
                    self.ledger, method, side_effect=failure
                ), self.assertRaises(IU4RecoveryProjectionError) as caught:
                    self.orchestrator.reconcile_terminal_gap(**kwargs)
                self.assertEqual(
                    caught.exception.reason_code, "PEE_IU4_RESOURCE_EXHAUSTED"
                )
                self.assertEqual(self.ledger.view().record_count, before_ledger)
                self.assertEqual(
                    self.coordinator.state_path.read_bytes(), before_state
                )
                self.assertEqual(
                    len(self.coordinator._transactions()), before_transactions
                )

    def test_restart_authorization_is_bound_to_trusted_environment_before_consumption(self) -> None:
        authorization = self._authorization("RECOVER_AND_RESTART")
        before = self.ledger.view().record_count
        rows = {
            "operator": "OTHER", "repository_commit_sha": "d" * 40,
            "secured_logs_manifest_sha256": H2,
            "environment_check_sha256": H,
            "last_state_timestamp_utc": "2026-08-21T12:00:01Z",
            "startup_attempt_id": "FOREIGN-STARTUP",
            "economics_config_fingerprint": H2,
            "throttle_policy_fingerprint": H2,
            "runtime_control_fingerprint": H2,
            "pre_attempt_ledger_tip": H2,
            "source_authority_generation_id": "FOREIGN-GENERATION",
            "source_authority_commit_anchor": H2,
            "expected_snapshot_fingerprint": H2,
            "expected_transaction_sequence": 1,
            "expected_journal_head": H2,
            "previous_kill_level": "HARD",
        }
        for index, (field, value) in enumerate(rows.items(), 1):
            divergent = replace(
                authorization, restart_recovery_authorization_id="",
                **{field: value},
            )
            with self.subTest(field=field), self.assertRaises(IU4RecoveryProjectionError) as caught:
                self.orchestrator.recover_and_restart(
                    authorization=divergent,
                    consumption_event_id=f"I6-DIVERGENT-AUTH-CONSUME-{index}",
                    materialization_event_id=f"I6-DIVERGENT-AUTH-MATERIALIZE-{index}",
                    consumption_timestamp_utc=UTC,
                    expected_startup_attempt_id="START-RECOVER_AND_RESTART",
                )
            self.assertEqual(
                caught.exception.reason_code,
                "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH",
            )
            self.assertEqual(self.ledger.view().record_count, before)

    def test_recovery_materialization_complete_fault_grid(self) -> None:
        points = (
            "BEFORE_CONSUMPTION", "AFTER_CONSUMPTION",
            "BEFORE_SNAPSHOT_MATERIALIZATION", "AFTER_SNAPSHOT_MATERIALIZATION",
            "BEFORE_RECOVERY_MATERIALIZATION", "AFTER_RECOVERY_MATERIALIZATION",
        )
        for index, point in enumerate(points, 1):
            coordinator = self.fixture._make_coordinator(
                self.fixture.temp / f"recovery-grid-atomic-{index}"
            )
            ledger = IU4LifecycleLedgerV1(
                self.fixture.temp / f"recovery-grid-ledger-{index}"
            )
            orchestrator = _orchestrator(ledger, coordinator)
            orchestrator.atomic_genesis(
                manifest=_genesis_manifest(
                    coordinator, self.fixture.initial_state,
                    suffix=f"RECOVERY-GRID-{index}",
                ),
                target_state_template=self.fixture.initial_state,
                prepare_event_id=f"RECOVERY-GRID-GENESIS-PREPARE-{index}",
                commit_event_id=f"RECOVERY-GRID-GENESIS-COMMIT-{index}",
            )
            authorization = _restart_authorization(
                coordinator, ledger, self.fixture, "RECOVER_AND_RESTART"
            )
            with self.subTest(point=point), self.assertRaises(IU4RecoveryProjectionError):
                orchestrator.recover_and_restart(
                    authorization=authorization,
                    consumption_event_id=f"RECOVERY-GRID-CONSUME-{index}",
                    materialization_event_id=f"RECOVERY-GRID-MATERIALIZE-{index}",
                    consumption_timestamp_utc=UTC,
                    expected_startup_attempt_id="START-RECOVER_AND_RESTART",
                    fault_point=point,
                )
            expected_records = (
                2 if point == "BEFORE_CONSUMPTION"
                else 4 if point == "AFTER_RECOVERY_MATERIALIZATION"
                else 3
            )
            self.assertEqual(ledger.view().record_count, expected_records)
            self.assertEqual(len(coordinator._transactions()), 0)

    def test_authority_root_rejects_foreign_target_without_mutation(self) -> None:
        from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinatorError

        state = self.coordinator.load_state(); before = self.coordinator.state_path.read_bytes()
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.i6_validate_authority_root(
                committed_target_state_fingerprint=H,
                authority_generation_id=state.authority_generation_id,
                authority_prepare_record_fingerprint=state.authority_prepare_record_fingerprint,
            )
        self.assertEqual(self.coordinator.state_path.read_bytes(), before)

    def test_terminal_gap_requires_death_reap_then_commits_one_emergency_kill(self) -> None:
        open_record = self.ledger.append(
            record_type="RUNTIME_SESSION_OPEN", lifecycle_event_id="I6-SESSION-OPEN",
            payload={"session_id": "SESSION-1", "journal_head": EMPTY},
        )
        authorization = self._authorization("RECONCILE_TERMINAL_GAP")
        state = self.coordinator.load_state(); view = self.ledger.view()
        anchor = _anchor()
        proof = IU4PersistenceWorkerExclusionProofV1.build(
            proof_mode="PROCESS_DEATH", runtime_session_id="SESSION-1",
            runtime_session_open_event_id="I6-SESSION-OPEN",
            runtime_session_open_record_fingerprint=open_record.record_fingerprint,
            authority_generation_id=state.authority_generation_id,
            authority_commit_anchor=view.authority_commit_anchor,
            coordinator_id=self.coordinator.coordinator_id, journal_root_fingerprint=H,
            old_worker_id="WORKER-1", old_worker_boot_id="BOOT-1", old_worker_pid=123,
            old_worker_start_time_ns=1, old_broker_generation_id=0,
            old_worker_generation_id=1, attestor_type="TERMINAL_PARENT_GUARDIAN_V13",
            attestor_id="GUARDIAN-1", attestor_executable_sha256=H,
            collector_id="COLLECTOR-1", source_evidence_id="EVIDENCE-1",
            source_evidence_sha256=H2, observed_at_utc=UTC,
            death_evidence_kind="PIDFD_EXIT_AND_REAP_ATTESTATION", observed_pidfd_id="PIDFD-1",
            pidfd_exit_observed=True, waitid_reaped=True, death_exit_status_class="EXITED",
            reap_evidence_fingerprint=H, death_observation_sequence=1,
            worker_append_handle_closed=True, surviving_writer_holder_count=0,
            append_handle_inventory_fingerprint=H2,
        )
        forged = _rebuild_artifact(
            proof, runtime_session_open_event_id="FORGED-OPEN"
        )
        before = self.ledger.view().record_count
        with self.assertRaises(IU4RecoveryProjectionError):
            self.orchestrator.reconcile_terminal_gap(
                authorization=authorization, anchor=anchor, proof=forged,
                expected_death_trust_anchor_id=anchor.trust_anchor_id,
                expected_death_trust_anchor_fingerprint=anchor.trust_anchor_fingerprint,
                expected_approval_fingerprint=H,
                expected_trusted_anchor_registry_fingerprint=H2,
                consumption_event_id="I6-FORGED-GAP-CONSUME",
                terminal_event_id="I6-FORGED-GAP-KILL",
                gap_event_id="I6-FORGED-GAP-RECORD",
                consumption_timestamp_utc=UTC,
                runtime_session_open_event_id="I6-SESSION-OPEN",
                runtime_session_open_record_fingerprint=open_record.record_fingerprint,
                runtime_session_open_journal_head=EMPTY,
                expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
                expected_journal_root_fingerprint=H,
                expected_old_worker_id="WORKER-1",
                expected_old_worker_boot_id="BOOT-1",
            )
        self.assertEqual(self.ledger.view().record_count, before)
        result = self.orchestrator.reconcile_terminal_gap(
            authorization=authorization, anchor=anchor, proof=proof,
            expected_death_trust_anchor_id=anchor.trust_anchor_id,
            expected_death_trust_anchor_fingerprint=anchor.trust_anchor_fingerprint,
            expected_approval_fingerprint=H,
            expected_trusted_anchor_registry_fingerprint=H2,
            consumption_event_id="I6-GAP-CONSUME", terminal_event_id="I6-GAP-KILL",
            gap_event_id="I6-GAP-RECORD", consumption_timestamp_utc=UTC,
            runtime_session_open_event_id="I6-SESSION-OPEN",
            runtime_session_open_record_fingerprint=open_record.record_fingerprint,
            runtime_session_open_journal_head=EMPTY,
            expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
            expected_journal_root_fingerprint=H,
            expected_old_worker_id="WORKER-1",
            expected_old_worker_boot_id="BOOT-1",
        )
        self.assertEqual(result.outcome, "TERMINAL_GAP_RECONCILED_LOOP_NOT_AUTHORIZED")
        self.assertEqual(self.coordinator.load_state().risk.kill_level, "EMERGENCY")
        self.assertEqual(len(self.coordinator._transactions()), 1)
        self.assertEqual(self.ledger.view().open_runtime_session_id, "")
        from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinatorError
        with self.assertRaises(PaperAtomicCoordinatorError):
            self.coordinator.i6_reconcile_terminal_journal(
                runtime_session_open_journal_head=EMPTY,
                worker_exclusion_proof_fingerprint=proof.proof_fingerprint,
                transaction_event_id="UNRELATED-KILL",
                transaction_timestamp_utc=UTC,
                causal_tick_id=0,
                control_authorization_reference=authorization.restart_recovery_authorization_id,
                reason_code="PEE_IU4_TERMINAL_GAP_RECONCILIATION_REQUIRED",
            )

    def test_terminal_gap_lifecycle_extension_before_lock_never_commits_kill(self) -> None:
        authorization, anchor, proof, open_event_id, open_record = (
            _terminal_gap_material(
                self.coordinator, self.ledger, self.fixture,
                suffix="INTERLEAVE",
            )
        )
        original = self.orchestrator._terminal_kill_and_gap_under_lifecycle_lock

        def append_foreign_extension_then_continue(**kwargs):
            self.ledger.append(
                record_type="RECOVERY_MATERIALIZATION",
                lifecycle_event_id="I6-FOREIGN-LIFECYCLE-EXTENSION",
                payload={"foreign": True},
            )
            return original(**kwargs)

        with patch.object(
            self.orchestrator,
            "_terminal_kill_and_gap_under_lifecycle_lock",
            side_effect=append_foreign_extension_then_continue,
        ), self.assertRaises(IU4RecoveryProjectionError) as caught:
            self.orchestrator.reconcile_terminal_gap(
                authorization=authorization, anchor=anchor, proof=proof,
                expected_death_trust_anchor_id=anchor.trust_anchor_id,
                expected_death_trust_anchor_fingerprint=(
                    anchor.trust_anchor_fingerprint
                ),
                expected_approval_fingerprint=H,
                expected_trusted_anchor_registry_fingerprint=H2,
                consumption_event_id="I6-INTERLEAVE-CONSUME",
                terminal_event_id="I6-INTERLEAVE-KILL",
                gap_event_id="I6-INTERLEAVE-GAP",
                consumption_timestamp_utc=UTC,
                runtime_session_open_event_id=open_event_id,
                runtime_session_open_record_fingerprint=(
                    open_record.record_fingerprint
                ),
                runtime_session_open_journal_head=EMPTY,
                expected_startup_attempt_id=(
                    "START-RECONCILE_TERMINAL_GAP"
                ),
                expected_journal_root_fingerprint=H,
                expected_old_worker_id="WORKER-1",
                expected_old_worker_boot_id="BOOT-1",
            )
        self.assertEqual(
            caught.exception.reason_code,
            "PEE_IU4_LIFECYCLE_EXTENSION_INVALID",
        )
        self.assertEqual(len(self.coordinator._transactions()), 0)
        self.assertEqual(self.coordinator.load_state().risk.kill_level, "NONE")
        self.assertEqual(self.ledger.view().record_count, 5)
        self.assertEqual(self.ledger.view().open_runtime_session_id, "SESSION-1")

    def test_terminal_gap_rejects_live_unreaped_and_surviving_holder_before_mutation(self) -> None:
        before = (self.coordinator.load_state().state_fingerprint, len(self.coordinator._transactions()), self.ledger.view().record_count)
        for field, value in (("pidfd_exit_observed", False), ("waitid_reaped", False),
                             ("worker_append_handle_closed", False), ("surviving_writer_holder_count", 1)):
            record = _proof().to_record(); record[field] = value
            with self.subTest(field=field), self.assertRaises(IU4RecoveryProjectionError):
                IU4PersistenceWorkerExclusionProofV1.from_record(record)
        self.assertEqual(before, (self.coordinator.load_state().state_fingerprint, len(self.coordinator._transactions()), self.ledger.view().record_count))

    def test_terminal_gap_after_kill_crash_requires_fresh_authority_and_reuses_exact_kill(self) -> None:
        open_record = self.ledger.append(
            record_type="RUNTIME_SESSION_OPEN",
            lifecycle_event_id="I6-CRASH-SESSION-OPEN",
            payload={"session_id": "SESSION-1", "journal_head": EMPTY},
        )
        state = self.coordinator.load_state(); view = self.ledger.view()
        anchor = _anchor()
        proof = IU4PersistenceWorkerExclusionProofV1.build(
            proof_mode="PROCESS_DEATH", runtime_session_id="SESSION-1",
            runtime_session_open_event_id="I6-CRASH-SESSION-OPEN",
            runtime_session_open_record_fingerprint=open_record.record_fingerprint,
            authority_generation_id=state.authority_generation_id,
            authority_commit_anchor=view.authority_commit_anchor,
            coordinator_id=self.coordinator.coordinator_id,
            journal_root_fingerprint=H, old_worker_id="WORKER-1",
            old_worker_boot_id="BOOT-1", old_worker_pid=123,
            old_worker_start_time_ns=1, old_broker_generation_id=0,
            old_worker_generation_id=1,
            attestor_type="TERMINAL_PARENT_GUARDIAN_V13",
            attestor_id="GUARDIAN-1", attestor_executable_sha256=H,
            collector_id="COLLECTOR-1", source_evidence_id="EVIDENCE-1",
            source_evidence_sha256=H2, observed_at_utc=UTC,
            death_evidence_kind="PIDFD_EXIT_AND_REAP_ATTESTATION",
            observed_pidfd_id="PIDFD-1", pidfd_exit_observed=True,
            waitid_reaped=True, death_exit_status_class="EXITED",
            reap_evidence_fingerprint=H, death_observation_sequence=1,
            worker_append_handle_closed=True, surviving_writer_holder_count=0,
            append_handle_inventory_fingerprint=H2,
        )
        common = dict(
            anchor=anchor, proof=proof,
            expected_death_trust_anchor_id=anchor.trust_anchor_id,
            expected_death_trust_anchor_fingerprint=anchor.trust_anchor_fingerprint,
            expected_approval_fingerprint=H,
            expected_trusted_anchor_registry_fingerprint=H2,
            terminal_event_id="I6-CRASH-GAP-KILL",
            consumption_timestamp_utc=UTC,
            runtime_session_open_event_id="I6-CRASH-SESSION-OPEN",
            runtime_session_open_record_fingerprint=open_record.record_fingerprint,
            runtime_session_open_journal_head=EMPTY,
            expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
            expected_journal_root_fingerprint=H,
            expected_old_worker_id="WORKER-1",
            expected_old_worker_boot_id="BOOT-1",
        )
        with self.assertRaises(IU4RecoveryProjectionError):
            self.orchestrator.reconcile_terminal_gap(
                authorization=self._authorization("RECONCILE_TERMINAL_GAP"),
                consumption_event_id="I6-CRASH-GAP-CONSUME-1",
                gap_event_id="I6-CRASH-GAP-RECORD-1",
                fault_point="AFTER_KILL", **common,
            )
        self.assertEqual(len(self.coordinator._transactions()), 1)
        result = self.orchestrator.reconcile_terminal_gap(
            authorization=self._authorization("RECONCILE_TERMINAL_GAP"),
            consumption_event_id="I6-CRASH-GAP-CONSUME-2",
            gap_event_id="I6-CRASH-GAP-RECORD-2", **common,
        )
        self.assertEqual(result.outcome, "TERMINAL_GAP_RECONCILED_LOOP_NOT_AUTHORIZED")
        self.assertEqual(len(self.coordinator._transactions()), 1)
        self.assertEqual(self.ledger.view().open_runtime_session_id, "")

    def test_terminal_gap_complete_fault_grid_preserves_exact_boundaries(self) -> None:
        points = (
            "BEFORE_PROOF_VALIDATION", "AFTER_PROOF_VALIDATION",
            "BEFORE_CONSUMPTION", "AFTER_CONSUMPTION", "BEFORE_KILL",
            "AFTER_KILL", "BEFORE_GAP_RECORD", "AFTER_GAP_RECORD",
        )
        for index, point in enumerate(points, 1):
            coordinator = self.fixture._make_coordinator(
                self.fixture.temp / f"terminal-grid-atomic-{index}"
            )
            ledger = IU4LifecycleLedgerV1(
                self.fixture.temp / f"terminal-grid-ledger-{index}"
            )
            orchestrator = _orchestrator(ledger, coordinator)
            orchestrator.atomic_genesis(
                manifest=_genesis_manifest(
                    coordinator, self.fixture.initial_state,
                    suffix=f"TERMINAL-GRID-{index}",
                ),
                target_state_template=self.fixture.initial_state,
                prepare_event_id=f"TERMINAL-GRID-GENESIS-PREPARE-{index}",
                commit_event_id=f"TERMINAL-GRID-GENESIS-COMMIT-{index}",
            )
            authorization, anchor, proof, open_event_id, open_record = (
                _terminal_gap_material(
                    coordinator, ledger, self.fixture, suffix=str(index)
                )
            )
            with self.subTest(point=point), self.assertRaises(IU4RecoveryProjectionError):
                orchestrator.reconcile_terminal_gap(
                    authorization=authorization, anchor=anchor, proof=proof,
                    expected_death_trust_anchor_id=anchor.trust_anchor_id,
                    expected_death_trust_anchor_fingerprint=anchor.trust_anchor_fingerprint,
                    expected_approval_fingerprint=H,
                    expected_trusted_anchor_registry_fingerprint=H2,
                    consumption_event_id=f"TERMINAL-GRID-CONSUME-{index}",
                    terminal_event_id=f"TERMINAL-GRID-KILL-{index}",
                    gap_event_id=f"TERMINAL-GRID-GAP-{index}",
                    consumption_timestamp_utc=UTC,
                    runtime_session_open_event_id=open_event_id,
                    runtime_session_open_record_fingerprint=open_record.record_fingerprint,
                    runtime_session_open_journal_head=EMPTY,
                    expected_startup_attempt_id="START-RECONCILE_TERMINAL_GAP",
                    expected_journal_root_fingerprint=H,
                    expected_old_worker_id="WORKER-1",
                    expected_old_worker_boot_id="BOOT-1", fault_point=point,
                )
            consumed = point in {
                "AFTER_CONSUMPTION", "BEFORE_KILL", "AFTER_KILL",
                "BEFORE_GAP_RECORD", "AFTER_GAP_RECORD",
            }
            killed = point in {
                "AFTER_KILL", "BEFORE_GAP_RECORD", "AFTER_GAP_RECORD",
            }
            gap_written = point == "AFTER_GAP_RECORD"
            self.assertEqual(ledger.view().record_count, 3 + consumed + gap_written)
            self.assertEqual(len(coordinator._transactions()), int(killed))
            self.assertEqual(
                coordinator.load_state().risk.kill_level,
                "EMERGENCY" if killed else "NONE",
            )
            self.assertEqual(
                ledger.view().open_runtime_session_id,
                "" if gap_written else "SESSION-1",
            )

    def test_handoff_rejects_every_mapping_conflict_before_mutation(self) -> None:
        target_path = str(self.fixture.temp / "mapping-conflict-target.json")
        manifest, target = _pee_to_legacy_material(
            self.coordinator, self.ledger, target_path
        )
        baseline = (
            self.ledger.view().record_count,
            self.coordinator.state_path.read_bytes(),
            Path(target_path).exists(),
        )
        for key, value in manifest.mapping_record.items():
            changed_mapping = dict(manifest.mapping_record)
            if key == "direction":
                changed_mapping[key] = "LEGACY_TO_PEE"
            elif key.endswith("_fingerprint"):
                changed_mapping[key] = H2 if value != H2 else H
            else:
                changed_mapping[key] = "FOREIGN-MAPPING-ID"
            with self.subTest(key=key), self.assertRaises(IU4RecoveryProjectionError):
                _rebuild_artifact(manifest, mapping_record=changed_mapping)
            self.assertEqual(
                (
                    self.ledger.view().record_count,
                    self.coordinator.state_path.read_bytes(),
                    Path(target_path).exists(),
                ),
                baseline,
            )

    def test_pee_to_legacy_handoff_prepare_target_commit(self) -> None:
        state = self.coordinator.load_state(); view = self.ledger.view()
        target_path = str(self.fixture.temp / "legacy-target.json")
        target = _legacy_snapshot(
            owner_epoch="LEGACY", source_path=target_path,
            system_state_id=state.system_state_id,
        )
        source_snapshot = _legacy_snapshot(
            owner_epoch="PEE", source_path=str(self.coordinator.state_path),
            system_state_id=state.system_state_id,
            source_bytes_sha256=hashlib.sha256(
                self.coordinator.state_path.read_bytes()
            ).hexdigest(),
            authority_generation_id=state.authority_generation_id,
        )
        target_business_fingerprint = _fp(target.to_record())
        target_core_fingerprint = _fp(target.to_record())
        generation = handoff_planned_generation_id(
            operation="PEE_TO_LEGACY",
            source_authority_generation_id=state.authority_generation_id,
            source_authority_commit_anchor=view.authority_commit_anchor,
            approval_fingerprint=H,
            target_business_payload=target.to_record(),
        )
        manifest = IU4StateHandoffManifestV1.build(
            direction="PEE_TO_LEGACY", repository_commit="c" * 40,
            symbol="BTCUSDT", coordinator_id=self.coordinator.coordinator_id,
            system_state_id=state.system_state_id, source_state_path=str(self.coordinator.state_path),
            source_state_schema=2, source_state_bytes_sha256=hashlib.sha256(self.coordinator.state_path.read_bytes()).hexdigest(),
            source_state_fingerprint=state.state_fingerprint,
            competing_state_path=target_path,
            competing_state_schema=1, competing_state_bytes_sha256=H,
            competing_state_fingerprint=H2,
            source_safety_snapshot=source_snapshot.to_record(),
            target_business_fingerprint=target_business_fingerprint,
            target_core_fingerprint=target_core_fingerprint,
            previous_owner_epoch=view.owner_epoch,
            new_owner_epoch=view.owner_epoch + 1,
            source_authority_generation_id=state.authority_generation_id,
            source_authority_commit_anchor=view.authority_commit_anchor,
            planned_authority_generation_id=generation,
            mapping_record=handoff_mapping_record(
                direction="PEE_TO_LEGACY", source_snapshot=source_snapshot,
                target_business_fingerprint=target_business_fingerprint,
                target_core_fingerprint=target_core_fingerprint,
            ),
            operator="OP", operation_timestamp_utc=UTC, approval_reference="APP",
            approval_fingerprint=H, operation_attempt_id="PEE-TO-LEGACY-1",
        )
        before = self.ledger.view().record_count
        with self.assertRaises(IU4RecoveryProjectionError):
            self.orchestrator.handoff(
                manifest=manifest,
                target=target,
                target_path=str(self.fixture.temp / "foreign-target.json"),
                prepare_event_id="I6-FOREIGN-PEE-LEGACY-PREPARE",
                commit_event_id="I6-FOREIGN-PEE-LEGACY-COMMIT",
            )
        self.assertEqual(self.ledger.view().record_count, before)
        result = self.orchestrator.handoff(
            manifest=manifest, target=target,
            target_path=target_path,
            prepare_event_id="I6-PEE-LEGACY-PREPARE", commit_event_id="I6-PEE-LEGACY-COMMIT",
        )
        self.assertEqual(result.outcome, "HANDOFF_COMPLETE_LOOP_NOT_AUTHORIZED")
        self.assertEqual(self.ledger.view().owner_epoch, 2)
        self.assertEqual(read_legacy_safety_projection(target_path), target.to_record())
        self.assertEqual(self.orchestrator.handoff(
            manifest=manifest, target=target,
            target_path=target_path,
            prepare_event_id="I6-PEE-LEGACY-PREPARE", commit_event_id="I6-PEE-LEGACY-COMMIT",
        ), result)

    def test_legacy_to_pee_handoff_on_fresh_target(self) -> None:
        ledger = IU4LifecycleLedgerV1(self.fixture.temp / "legacy-source-ledger")
        prepare = ledger.append(
            record_type="LEGACY_GENESIS_PREPARE", lifecycle_event_id="LEGACY-GENESIS-PREPARE",
            payload={"authority_generation_id": "LEGACY-GEN", "new_owner_epoch": 1},
        )
        ledger.append(
            record_type="LEGACY_GENESIS_COMMIT", lifecycle_event_id="LEGACY-GENESIS-COMMIT",
            payload={"prepare_record_fingerprint": prepare.record_fingerprint,
                     "authority_generation_id": "LEGACY-GEN", "new_owner_epoch": 1},
        )
        coordinator = self.fixture._make_coordinator(self.fixture.temp / "legacy-to-pee-target")
        orchestrator = _orchestrator(ledger, coordinator)
        view = ledger.view(); target = self.fixture.initial_state
        generation = handoff_planned_generation_id(
            operation="LEGACY_TO_PEE", source_authority_generation_id=view.authority_generation_id,
            source_authority_commit_anchor=view.authority_commit_anchor,
            approval_fingerprint=H, target_business_payload=target.business_payload(),
        )
        source_snapshot = _legacy_snapshot(
            owner_epoch="LEGACY", source_path="/tmp/legacy-source.json",
            system_state_id=target.system_state_id,
            authority_generation_id=view.authority_generation_id,
        )
        target_business_fingerprint = _fp(target.business_payload())
        target_core_fingerprint = _fp(target.core_payload())
        manifest = IU4StateHandoffManifestV1.build(
            direction="LEGACY_TO_PEE", repository_commit="c" * 40,
            symbol="BTCUSDT", coordinator_id=coordinator.coordinator_id,
            system_state_id=target.system_state_id, source_state_path="/tmp/legacy-source.json",
            source_state_schema=1,
            source_state_bytes_sha256=source_snapshot.source_bytes_sha256,
            source_state_fingerprint=source_snapshot.snapshot_fingerprint,
            competing_state_path=str(coordinator.state_path), competing_state_schema=2,
            competing_state_bytes_sha256=H2, competing_state_fingerprint=target.state_fingerprint,
            source_safety_snapshot=source_snapshot.to_record(),
            target_business_fingerprint=target_business_fingerprint,
            target_core_fingerprint=target_core_fingerprint,
            previous_owner_epoch=1, new_owner_epoch=2,
            source_authority_generation_id=view.authority_generation_id,
            source_authority_commit_anchor=view.authority_commit_anchor,
            planned_authority_generation_id=generation,
            mapping_record=handoff_mapping_record(
                direction="LEGACY_TO_PEE", source_snapshot=source_snapshot,
                target_business_fingerprint=target_business_fingerprint,
                target_core_fingerprint=target_core_fingerprint,
            ),
            operator="OP", operation_timestamp_utc=UTC, approval_reference="APP",
            approval_fingerprint=H, operation_attempt_id="LEGACY-TO-PEE-1",
        )
        result = orchestrator.handoff(
            manifest=manifest, target=target, target_path=str(coordinator.state_path),
            prepare_event_id="I6-LEGACY-PEE-PREPARE", commit_event_id="I6-LEGACY-PEE-COMMIT",
        )
        self.assertEqual(result.outcome, "HANDOFF_COMPLETE_LOOP_NOT_AUTHORIZED")
        self.assertEqual(ledger.view().owner_epoch, 2)
        self.assertEqual(coordinator.load_state().authority_generation_id, generation)
        self.assertEqual(orchestrator.handoff(
            manifest=manifest, target=target, target_path=str(coordinator.state_path),
            prepare_event_id="I6-LEGACY-PEE-PREPARE", commit_event_id="I6-LEGACY-PEE-COMMIT",
        ), result)

    def test_pee_to_legacy_handoff_complete_fault_grid(self) -> None:
        points = (
            "BEFORE_PREPARE", "AFTER_PREPARE", "BEFORE_TARGET_REPLACE",
            "AFTER_TARGET_REPLACE", "AFTER_TARGET_FILE_SYNC",
            "AFTER_TARGET_DIRECTORY_SYNC", "AFTER_RECONCILIATION",
            "BEFORE_COMMIT", "AFTER_COMMIT",
        )
        for index, point in enumerate(points, 1):
            coordinator = self.fixture._make_coordinator(
                self.fixture.temp / f"handoff-grid-atomic-{index}"
            )
            ledger = IU4LifecycleLedgerV1(
                self.fixture.temp / f"handoff-grid-ledger-{index}"
            )
            orchestrator = _orchestrator(ledger, coordinator)
            orchestrator.atomic_genesis(
                manifest=_genesis_manifest(
                    coordinator, self.fixture.initial_state,
                    suffix=f"HANDOFF-GRID-{index}",
                ),
                target_state_template=self.fixture.initial_state,
                prepare_event_id=f"HANDOFF-GRID-GENESIS-PREPARE-{index}",
                commit_event_id=f"HANDOFF-GRID-GENESIS-COMMIT-{index}",
            )
            target_path = str(
                self.fixture.temp / f"handoff-grid-target-{index}.json"
            )
            manifest, target = _pee_to_legacy_material(
                coordinator, ledger, target_path
            )
            with self.subTest(point=point), self.assertRaises(IU4RecoveryProjectionError):
                orchestrator.handoff(
                    manifest=manifest, target=target, target_path=target_path,
                    prepare_event_id=f"HANDOFF-GRID-PREPARE-{index}",
                    commit_event_id=f"HANDOFF-GRID-COMMIT-{index}",
                    fault_point=point,
                )
            expected_records = (
                2 if point == "BEFORE_PREPARE"
                else 4 if point == "AFTER_COMMIT"
                else 3
            )
            self.assertEqual(ledger.view().record_count, expected_records)
            self.assertEqual(
                ledger.view().owner_epoch,
                2 if point == "AFTER_COMMIT" else 1,
            )
            if point == "AFTER_COMMIT":
                replay = orchestrator.handoff(
                    manifest=manifest, target=target, target_path=target_path,
                    prepare_event_id=f"HANDOFF-GRID-PREPARE-{index}",
                    commit_event_id=f"HANDOFF-GRID-COMMIT-{index}",
                )
                self.assertEqual(
                    replay.outcome, "HANDOFF_COMPLETE_LOOP_NOT_AUTHORIZED"
                )

    def test_genesis_prepare_completion_requires_fresh_consumed_authority(self) -> None:
        from live_l1.core.paper_iu4_startup_gate import IU4RestartRecoveryAuthorizationV1

        coordinator = self.fixture._make_coordinator(self.fixture.temp / "completion-atomic")
        ledger = IU4LifecycleLedgerV1(self.fixture.temp / "completion-ledger")
        orchestrator = _orchestrator(ledger, coordinator)
        manifest = _genesis_manifest(coordinator, self.fixture.initial_state, suffix="C")
        with self.assertRaises(IU4RecoveryProjectionError):
            orchestrator.atomic_genesis(
                manifest=manifest, target_state_template=self.fixture.initial_state,
                prepare_event_id="I6-COMPLETE-PREPARE", commit_event_id="I6-COMPLETE-COMMIT",
                fault_point="AFTER_PREPARE",
            )
        prepare = ledger.records()[0]
        generation = prepare.payload["authority_generation_id"]
        materialized = replace(
            self.fixture.initial_state,
            authority_generation_id=generation,
            authority_prepare_record_fingerprint=prepare.record_fingerprint,
            authority_manifest_id=manifest.clean_genesis_manifest_id,
            authority_manifest_fingerprint=manifest.manifest_fingerprint,
            risk=replace(self.fixture.initial_state.risk, authority_generation_id=generation),
        )
        authorization = IU4RestartRecoveryAuthorizationV1(
            schema_version=1, restart_recovery_authorization_id="", operator="OP",
            decision_timestamp_utc=UTC, stop_recovery_reason="COMPLETE-I6",
            previous_kill_level="NONE", secured_logs_manifest_sha256=H,
            last_state_timestamp_utc=UTC, no_open_intents_confirmed=True,
            environment_check_sha256=H2, repository_commit_sha="c" * 40,
            coordinator_id=coordinator.coordinator_id,
            economics_config_fingerprint=self.fixture.config.config_fingerprint,
            throttle_policy_fingerprint=self.fixture.policy.policy_fingerprint,
            runtime_control_fingerprint=self.fixture.runtime_control_fingerprint,
            pre_attempt_ledger_tip=ledger.view().ledger_tip, startup_attempt_id="START-COMPLETE",
            source_authority_commit_anchor=NONE, source_authority_generation_id=NONE,
            expected_transaction_sequence=0, expected_journal_head=EMPTY,
            expected_snapshot_fingerprint="NO_ATOMIC_STATE",
            operation="COMPLETE_AUTHORITY_PREPARE",
            completion_prepare_event_id=prepare.lifecycle_event_id,
            completion_prepare_fingerprint=prepare.record_fingerprint,
            completion_operation_type="ATOMIC_GENESIS",
            planned_authority_generation_id=generation,
            completion_source_authority_anchor="GENESIS-SOURCE-NONE",
            target_core_fingerprint=prepare.payload["target_state_core_fingerprint"],
            expected_target_schema="2", expected_target_path=str(coordinator.state_path),
            expected_commit_type="ATOMIC_GENESIS_COMMIT",
            valid_from_utc="2026-08-21T11:00:00Z", valid_until_utc="2026-08-21T13:00:00Z",
        )
        result = orchestrator.complete_authority_prepare(
            authorization=authorization, target=self.fixture.initial_state,
            target_fingerprint=materialized.state_fingerprint,
            target_core_fingerprint=prepare.payload["target_state_core_fingerprint"],
            target_path=str(coordinator.state_path), consumption_event_id="I6-COMPLETE-CONSUME",
            materialization_event_id="I6-COMPLETE-MATERIALIZE",
            commit_event_id="I6-COMPLETE-COMMIT", consumption_timestamp_utc=UTC,
            expected_startup_attempt_id="START-COMPLETE",
        )
        self.assertEqual(result.outcome, "AUTHORITY_PREPARE_COMPLETE_RESTART_ONLY")
        self.assertEqual(ledger.view().owner_epoch, 1)
        with self.assertRaises(IU4RecoveryProjectionError):
            orchestrator.complete_authority_prepare(
                authorization=authorization, target=self.fixture.initial_state,
                target_fingerprint=materialized.state_fingerprint,
                target_core_fingerprint=prepare.payload["target_state_core_fingerprint"],
                target_path=str(coordinator.state_path), consumption_event_id="I6-COMPLETE-CONSUME-2",
                materialization_event_id="I6-COMPLETE-MATERIALIZE-2",
                commit_event_id="I6-COMPLETE-COMMIT-2", consumption_timestamp_utc=UTC,
                expected_startup_attempt_id="START-COMPLETE",
            )

    def test_genesis_direct_fault_boundary_grid(self) -> None:
        points = (
            "BEFORE_PREPARE", "AFTER_PREPARE", "BEFORE_TARGET_REPLACE",
            "AFTER_TARGET_REPLACE", "AFTER_TARGET_FILE_SYNC",
            "AFTER_TARGET_DIRECTORY_SYNC", "AFTER_RECONCILIATION",
            "BEFORE_COMMIT", "AFTER_COMMIT",
        )
        for index, point in enumerate(points, 1):
            coordinator = self.fixture._make_coordinator(self.fixture.temp / f"genesis-grid-atomic-{index}")
            ledger = IU4LifecycleLedgerV1(self.fixture.temp / f"genesis-grid-ledger-{index}")
            orchestrator = _orchestrator(ledger, coordinator)
            manifest = _genesis_manifest(
                coordinator, self.fixture.initial_state, suffix=f"G-{index}"
            )
            with self.subTest(point=point), self.assertRaises(IU4RecoveryProjectionError):
                orchestrator.atomic_genesis(
                    manifest=manifest, target_state_template=self.fixture.initial_state,
                    prepare_event_id=f"GRID-PREPARE-{index}", commit_event_id=f"GRID-COMMIT-{index}",
                    fault_point=point,
                )
            records = ledger.records()
            if point == "BEFORE_PREPARE":
                self.assertEqual(len(records), 0); self.assertFalse(coordinator.state_path.exists())
            elif point in {"AFTER_PREPARE", "BEFORE_TARGET_REPLACE"}:
                self.assertEqual(len(records), 1); self.assertFalse(coordinator.state_path.exists())
            elif point == "AFTER_COMMIT":
                self.assertEqual(len(records), 2); self.assertEqual(ledger.view().owner_epoch, 1)
                self.assertEqual(orchestrator.atomic_genesis(
                    manifest=manifest, target_state_template=self.fixture.initial_state,
                    prepare_event_id=f"GRID-PREPARE-{index}", commit_event_id=f"GRID-COMMIT-{index}",
                ).outcome, "GENESIS_COMPLETE_LOOP_NOT_AUTHORIZED")
            else:
                self.assertEqual(len(records), 1); self.assertTrue(coordinator.state_path.exists())


if __name__ == "__main__":
    unittest.main()
