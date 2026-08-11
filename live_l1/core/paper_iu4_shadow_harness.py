#!/usr/bin/env python3
"""Isolated SHADOW dry-run harness for the inactive IU-4 Paper adapter.

The harness clones validated atomic state into a temporary directory and lets
the real IU-4 adapter mutate only that disposable clone.  Source coordinator
files are hashed before and after every run and are never opened for writing.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from live_l1.core.paper_entry_throttle import canonical_utc_timestamp
from live_l1.core.paper_iu4_adapter import (
    IU4AdapterRequestV1,
    IU4AdapterResultV1,
    PaperIU4Adapter,
    PaperIU4AdapterError,
    STATUS_COMMITTED,
    STATUS_NOOP,
    STATUS_REJECTED,
)
from live_l1.core.paper_iu4_startup_gate import (
    IU4StartupGateDecisionV1,
    MODE_SHADOW,
)
from live_l1.state.paper_artifacts import canonical_decimal
from live_l1.state.paper_atomic_coordinator import (
    PaperAtomicCoordinator,
    PaperAtomicCoordinatorError,
)


class IU4ShadowHarnessReasonCode:
    GATE_INVALID = "PEE_IU4_SHADOW_GATE_INVALID"
    SOURCE_INVALID = "PEE_IU4_SHADOW_SOURCE_INVALID"
    SOURCE_CHANGED = "PEE_IU4_SHADOW_SOURCE_CHANGED"
    SANDBOX_INVALID = "PEE_IU4_SHADOW_SANDBOX_INVALID"
    WORK_DIRECTORY_INVALID = "PEE_IU4_SHADOW_WORK_DIRECTORY_INVALID"
    STEP_INVALID = "PEE_IU4_SHADOW_STEP_INVALID"
    DUPLICATE_SOURCE_INTENT = "PEE_IU4_SHADOW_DUPLICATE_SOURCE_INTENT"


SOURCE_EVENT_INTENT = "INTENT"
SOURCE_EVENT_AUTONOMOUS_EXIT = "AUTONOMOUS_EXIT_EXECUTION"
RESTART_FAULT_SNAPSHOT_TRUNCATED = "SNAPSHOT_TRUNCATED"
GUARD_DIVERGENCE_EXIT_SUPPRESSED = (
    "PEE_IU4_SHADOW_GUARD_DIVERGENCE_EXIT_SUPPRESSED"
)


class IU4ShadowHarnessError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


def _text(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.STEP_INVALID,
            f"{field_name} must be a string",
        )
    result = value.strip()
    if not allow_empty and not result:
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.STEP_INVALID,
            f"{field_name} must not be empty",
        )
    return result


def _integer(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.STEP_INVALID,
            f"{field_name} must be a non-negative integer",
        )
    return value


def _positive_decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.STEP_INVALID,
            f"{field_name} must be Decimal, int, or a decimal string",
        )
    try:
        result = value if isinstance(value, Decimal) else Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.STEP_INVALID,
            f"{field_name} is not a valid decimal",
        ) from exc
    if not result.is_finite() or result <= 0:
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.STEP_INVALID,
            f"{field_name} must be finite and greater than zero",
        )
    return result


@dataclass(frozen=True)
class IU4ShadowIntentStepV1:
    schema_version: int
    source_intent_id: str
    intent_final: str
    intent_reason_code: str
    target_system_state_id: str
    timestamp_utc: str
    tick_id: int
    reference_price: Decimal | int | str
    reference_stop_price: Decimal | int | str | None
    trade_id: str
    source_event_kind: str = SOURCE_EVENT_INTENT
    source_intent_final: str = ""
    source_execution_action: str = ""
    source_execution_sequence: int = 0

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version not in (1, 2)
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "IU4ShadowIntentStepV1 requires schema_version 1 or 2",
            )
        for name in (
            "source_intent_id",
            "intent_reason_code",
            "target_system_state_id",
            "timestamp_utc",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(
            self,
            "intent_final",
            _text(self.intent_final, "intent_final").upper(),
        )
        if self.intent_final not in ("BUY", "SELL", "HOLD"):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "intent_final must be BUY, SELL, or HOLD",
            )
        try:
            timestamp = canonical_utc_timestamp(self.timestamp_utc, "timestamp_utc")
        except Exception as exc:
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "timestamp_utc must be canonical UTC whole seconds",
            ) from exc
        object.__setattr__(self, "timestamp_utc", timestamp)
        object.__setattr__(self, "tick_id", _integer(self.tick_id, "tick_id"))
        object.__setattr__(
            self,
            "reference_price",
            _positive_decimal(self.reference_price, "reference_price"),
        )
        if self.reference_stop_price is not None:
            object.__setattr__(
                self,
                "reference_stop_price",
                _positive_decimal(self.reference_stop_price, "reference_stop_price"),
            )
        object.__setattr__(self, "trade_id", _text(self.trade_id, "trade_id", allow_empty=True))

        if self.schema_version == 1:
            if (
                self.source_event_kind != SOURCE_EVENT_INTENT
                or self.source_intent_final not in ("", self.intent_final)
                or self.source_execution_action
                or self.source_execution_sequence != 0
            ):
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.STEP_INVALID,
                    "schema version 1 cannot carry source execution provenance",
                )
            object.__setattr__(self, "source_intent_final", self.intent_final)
            return

        source_event_kind = _text(self.source_event_kind, "source_event_kind").upper()
        source_intent_final = _text(
            self.source_intent_final,
            "source_intent_final",
        ).upper()
        source_execution_action = _text(
            self.source_execution_action,
            "source_execution_action",
            allow_empty=True,
        ).upper()
        source_execution_sequence = _integer(
            self.source_execution_sequence,
            "source_execution_sequence",
        )
        if source_intent_final not in ("BUY", "SELL", "HOLD"):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "source_intent_final must be BUY, SELL, or HOLD",
            )
        if source_event_kind == SOURCE_EVENT_INTENT:
            if (
                source_intent_final != self.intent_final
                or source_execution_action
                or source_execution_sequence != 0
            ):
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.STEP_INVALID,
                    "INTENT provenance cannot alter the fused source intent",
                )
        elif source_event_kind == SOURCE_EVENT_AUTONOMOUS_EXIT:
            expected_intent = {
                "CLOSE_LONG": "SELL",
                "CLOSE_SHORT": "BUY",
            }.get(source_execution_action)
            if (
                source_intent_final != "HOLD"
                or expected_intent != self.intent_final
                or source_execution_sequence < 1
                or self.reference_stop_price is not None
                or self.trade_id
            ):
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.STEP_INVALID,
                    "autonomous exit provenance must bind HOLD to one close-only execution",
                )
        else:
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "source_event_kind is unsupported",
            )
        object.__setattr__(self, "source_event_kind", source_event_kind)
        object.__setattr__(self, "source_intent_final", source_intent_final)
        object.__setattr__(self, "source_execution_action", source_execution_action)
        object.__setattr__(self, "source_execution_sequence", source_execution_sequence)

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema_version": self.schema_version,
            "source_intent_id": self.source_intent_id,
            "intent_final": self.intent_final,
            "intent_reason_code": self.intent_reason_code,
            "target_system_state_id": self.target_system_state_id,
            "timestamp_utc": self.timestamp_utc,
            "tick_id": self.tick_id,
            "reference_price": canonical_decimal(self.reference_price),
            "reference_stop_price": (
                None
                if self.reference_stop_price is None
                else canonical_decimal(self.reference_stop_price)
            ),
            "trade_id": self.trade_id,
        }
        if self.schema_version == 2:
            record.update(
                {
                    "source_event_kind": self.source_event_kind,
                    "source_intent_final": self.source_intent_final,
                    "source_execution_action": self.source_execution_action,
                    "source_execution_sequence": self.source_execution_sequence,
                }
            )
        return record

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "IU4ShadowIntentStepV1":
        schema_version = record.get("schema_version")
        provenance_fields = {
            "source_event_kind",
            "source_intent_final",
            "source_execution_action",
            "source_execution_sequence",
        }
        expected_fields = set(cls.__dataclass_fields__)
        if schema_version == 1:
            expected_fields -= provenance_fields
        if set(record) != expected_fields:
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "IU4 shadow replay step fields are missing or unknown",
            )
        return cls(**record)


@dataclass(frozen=True)
class IU4ShadowSourceFileV1:
    relative_path: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class IU4ShadowGuardDivergenceV1:
    schema_version: int
    position_side: str
    first_rejected_step_index: int
    first_rejected_source_intent_id: str
    last_rejected_step_index: int
    last_rejected_source_intent_id: str
    rejected_entry_count: int
    guard_reason_codes: tuple[str, ...]
    sandbox_state_fingerprint: str
    suppressed_exit_step_index: int
    suppressed_exit_source_intent_id: str
    suppressed_exit_action: str
    suppressed_exit_sequence: int


@dataclass(frozen=True)
class _PendingGuardDivergence:
    position_side: str
    first_rejected_step_index: int
    first_rejected_source_intent_id: str
    last_rejected_step_index: int
    last_rejected_source_intent_id: str
    rejected_entry_count: int
    guard_reason_codes: tuple[str, ...]
    sandbox_state_fingerprint: str


@dataclass(frozen=True)
class IU4ShadowDryRunReportV1:
    schema_version: int
    source_manifest_fingerprint: str
    source_initial_state_fingerprint: str
    source_final_state_fingerprint: str
    sandbox_final_state_fingerprint: str
    source_initial_transaction_sequence: int
    sandbox_final_transaction_sequence: int
    simulated_transaction_count: int
    step_count: int
    committed_step_count: int
    noop_step_count: int
    rejected_step_count: int
    requested_step_count: int
    restart_enabled: bool
    restart_after_step: int
    restart_count: int
    restart_position: str
    restart_state_fingerprint: str
    restart_transaction_sequence: int
    restart_state_restored: bool
    restart_fault_injection: str
    restart_fault_detected: bool
    restart_fault_reason_codes: tuple[str, ...]
    restart_fault_snapshot_sha256_before: str
    restart_fault_snapshot_sha256_after: str
    continuation_blocked: bool
    source_unchanged: bool
    sandbox_consistent: bool
    guard_divergence_count: int
    guard_divergences: tuple[IU4ShadowGuardDivergenceV1, ...]
    outcomes: tuple[IU4AdapterResultV1, ...]


def _source_files(coordinator: PaperAtomicCoordinator) -> tuple[Path, ...]:
    state_path = coordinator.state_path
    if not state_path.is_file() or state_path.is_symlink():
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.SOURCE_INVALID,
            "atomic source snapshot must be a regular file",
        )
    journal_paths: tuple[Path, ...] = ()
    if coordinator.transaction_directory.exists():
        if (
            not coordinator.transaction_directory.is_dir()
            or coordinator.transaction_directory.is_symlink()
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.SOURCE_INVALID,
                "atomic transaction source must be a regular directory",
            )
        journal_paths = tuple(sorted(coordinator.transaction_directory.glob("*.json")))
        if any(not path.is_file() or path.is_symlink() for path in journal_paths):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.SOURCE_INVALID,
                "atomic journal contains a non-regular JSON path",
            )
    return (state_path, *journal_paths)


def _manifest(
    coordinator: PaperAtomicCoordinator,
) -> tuple[tuple[IU4ShadowSourceFileV1, ...], str]:
    root = coordinator.root_directory.resolve()
    entries: list[IU4ShadowSourceFileV1] = []
    for path in _source_files(coordinator):
        payload = path.read_bytes()
        entries.append(
            IU4ShadowSourceFileV1(
                relative_path=path.resolve().relative_to(root).as_posix(),
                size_bytes=len(payload),
                sha256=hashlib.sha256(payload).hexdigest(),
            )
        )
    canonical = [
        {
            "relative_path": entry.relative_path,
            "size_bytes": entry.size_bytes,
            "sha256": entry.sha256,
        }
        for entry in entries
    ]
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return tuple(entries), hashlib.sha256(encoded).hexdigest()


def _validate_work_directory(
    source_root: Path,
    work_directory: str | Path | None,
) -> Path | None:
    if work_directory is None:
        return None
    work_root = Path(work_directory).resolve()
    if not work_root.is_dir():
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.WORK_DIRECTORY_INVALID,
            "shadow work directory must already exist",
        )
    if work_root == source_root or source_root in work_root.parents:
        raise IU4ShadowHarnessError(
            IU4ShadowHarnessReasonCode.WORK_DIRECTORY_INVALID,
            "shadow work directory must not be inside the source coordinator root",
        )
    return work_root


def _clone_source(
    source: PaperAtomicCoordinator,
    sandbox_root: Path,
    entries: tuple[IU4ShadowSourceFileV1, ...],
) -> None:
    source_root = source.root_directory.resolve()
    for entry in entries:
        source_path = source_root / entry.relative_path
        target_path = sandbox_root / entry.relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_path)


def _inject_truncated_snapshot(path: Path) -> tuple[str, str]:
    before = path.read_bytes()
    payload = b'{"schema_version":1,"fault":"TRUNCATED"\n'
    with path.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    return hashlib.sha256(before).hexdigest(), hashlib.sha256(payload).hexdigest()


class PaperIU4ShadowDryRunHarness:
    def __init__(
        self,
        source_coordinator: PaperAtomicCoordinator,
        shadow_gate_decision: IU4StartupGateDecisionV1,
        *,
        work_directory: str | Path | None = None,
    ) -> None:
        if not isinstance(source_coordinator, PaperAtomicCoordinator):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.SOURCE_INVALID,
                "source_coordinator must be PaperAtomicCoordinator",
            )
        if (
            not isinstance(shadow_gate_decision, IU4StartupGateDecisionV1)
            or not shadow_gate_decision.passed
            or shadow_gate_decision.mode != MODE_SHADOW
            or not shadow_gate_decision.shadow_observation_enabled
            or shadow_gate_decision.adapter_execution_enabled
            or shadow_gate_decision.state_mutation_allowed
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.GATE_INVALID,
                "harness requires a passed, read-only SHADOW gate decision",
            )
        self.source_coordinator = source_coordinator
        self.shadow_gate_decision = shadow_gate_decision
        self.work_directory = _validate_work_directory(
            source_coordinator.root_directory.resolve(),
            work_directory,
        )

    @staticmethod
    def _request_for(
        step: IU4ShadowIntentStepV1,
        sandbox: PaperAtomicCoordinator,
    ) -> IU4AdapterRequestV1:
        if not isinstance(step, IU4ShadowIntentStepV1):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "every shadow step must be IU4ShadowIntentStepV1",
            )
        state = sandbox.load_state()
        position = state.position.position
        if step.source_event_kind == SOURCE_EVENT_AUTONOMOUS_EXIT:
            required_position = (
                "LONG"
                if step.source_execution_action == "CLOSE_LONG"
                else "SHORT"
            )
            if position != required_position:
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.STEP_INVALID,
                    "autonomous exit execution does not match the sandbox position",
                )
        opens = position == "FLAT" and step.intent_final in ("BUY", "SELL")
        closes = (position == "LONG" and step.intent_final == "SELL") or (
            position == "SHORT" and step.intent_final == "BUY"
        )
        if opens:
            trade_id = step.trade_id
            reference_stop_price = step.reference_stop_price
            target_system_state_id = step.target_system_state_id
        else:
            trade_id = getattr(state.position, "trade_id", "")
            reference_stop_price = None
            target_system_state_id = (
                step.target_system_state_id
                if closes
                else state.position.system_state_id
            )
        return IU4AdapterRequestV1(
            schema_version=1,
            request_id="",
            source_intent_id=step.source_intent_id,
            intent_final=step.intent_final,
            intent_reason_code=step.intent_reason_code,
            expected_state_fingerprint=state.state_fingerprint,
            target_system_state_id=target_system_state_id,
            timestamp_utc=step.timestamp_utc,
            tick_id=step.tick_id,
            reference_price=step.reference_price,
            reference_stop_price=reference_stop_price,
            trade_id=trade_id,
        )

    @staticmethod
    def _guard_divergence_noop_request(
        step: IU4ShadowIntentStepV1,
        sandbox: PaperAtomicCoordinator,
    ) -> IU4AdapterRequestV1:
        state = sandbox.load_state()
        return IU4AdapterRequestV1(
            schema_version=1,
            request_id="",
            source_intent_id=step.source_intent_id,
            intent_final="HOLD",
            intent_reason_code=step.intent_reason_code,
            expected_state_fingerprint=state.state_fingerprint,
            target_system_state_id=state.position.system_state_id,
            timestamp_utc=step.timestamp_utc,
            tick_id=step.tick_id,
            reference_price=step.reference_price,
            reference_stop_price=None,
            trade_id="",
        )

    def run(
        self,
        steps: Sequence[IU4ShadowIntentStepV1],
        *,
        restart_after_steps: int | None = None,
        restart_fault_injection: str | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
        progress_interval_steps: int = 10_000,
    ) -> IU4ShadowDryRunReportV1:
        if isinstance(steps, (str, bytes)) or not isinstance(steps, Sequence):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "steps must be a finite sequence",
            )
        step_values = tuple(steps)
        if (
            isinstance(progress_interval_steps, bool)
            or not isinstance(progress_interval_steps, int)
            or progress_interval_steps < 1
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "progress_interval_steps must be a positive integer",
            )
        if restart_after_steps is not None and (
            isinstance(restart_after_steps, bool)
            or not isinstance(restart_after_steps, int)
            or restart_after_steps < 1
            or restart_after_steps >= len(step_values)
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "restart_after_steps must split the finite replay into two non-empty segments",
            )
        if restart_fault_injection is not None and (
            restart_fault_injection != RESTART_FAULT_SNAPSHOT_TRUNCATED
            or restart_after_steps is None
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "restart fault injection requires SNAPSHOT_TRUNCATED and a valid restart boundary",
            )
        source_report = self.source_coordinator.reconciliation_report()
        if not source_report.consistent:
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.SOURCE_INVALID,
                f"source reconciliation failed: {source_report.reason_codes}",
            )
        source_state = self.source_coordinator.load_state()
        if (
            source_state.state_fingerprint
            != self.shadow_gate_decision.atomic_state_fingerprint
            or source_state.transaction_sequence
            != self.shadow_gate_decision.atomic_transaction_sequence
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.GATE_INVALID,
                "source state changed after the SHADOW startup gate decision",
            )
        source_entries, manifest_fingerprint = _manifest(self.source_coordinator)

        seen_intents: set[str] = set()
        for step in step_values:
            if not isinstance(step, IU4ShadowIntentStepV1):
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.STEP_INVALID,
                    "every shadow step must be IU4ShadowIntentStepV1",
                )
            if step.source_intent_id in seen_intents:
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.DUPLICATE_SOURCE_INTENT,
                    f"duplicate source intent {step.source_intent_id}",
                )
            seen_intents.add(step.source_intent_id)

        with tempfile.TemporaryDirectory(
            prefix="pee-iu4-shadow-",
            dir=None if self.work_directory is None else str(self.work_directory),
        ) as sandbox_text:
            sandbox_root = Path(sandbox_text).resolve()
            source_root = self.source_coordinator.root_directory.resolve()
            if sandbox_root == source_root or source_root in sandbox_root.parents:
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.WORK_DIRECTORY_INVALID,
                    "temporary shadow sandbox overlaps source coordinator root",
                )
            _clone_source(self.source_coordinator, sandbox_root, source_entries)
            if _manifest(self.source_coordinator)[1] != manifest_fingerprint:
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.SOURCE_CHANGED,
                    "source coordinator changed while its sandbox clone was built",
                )
            sandbox = PaperAtomicCoordinator(
                sandbox_root,
                self.source_coordinator.config,
                self.source_coordinator.throttle_policy,
                coordinator_id=self.source_coordinator.coordinator_id,
                symbol=self.source_coordinator.symbol,
            )
            sandbox_report = sandbox.reconciliation_report()
            sandbox_state = sandbox.load_state()
            if not sandbox_report.consistent or sandbox_state != source_state:
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.SANDBOX_INVALID,
                    "sandbox is not an exact reconciled source clone",
                )
            adapter = PaperIU4Adapter(sandbox)
            outcome_values: list[IU4AdapterResultV1] = []
            pending_guard_divergences: dict[str, _PendingGuardDivergence] = {}
            guard_divergence_values: list[IU4ShadowGuardDivergenceV1] = []
            restart_position = ""
            restart_state_fingerprint = ""
            restart_transaction_sequence = 0
            restart_state_restored = False
            restart_fault_detected = False
            restart_fault_reason_codes: tuple[str, ...] = ()
            restart_fault_snapshot_sha256_before = ""
            restart_fault_snapshot_sha256_after = ""
            continuation_blocked = False
            if progress_callback is not None:
                progress_callback(0, len(step_values))
            for index, step in enumerate(step_values, start=1):
                try:
                    state_before = sandbox.load_state()
                    position_before = state_before.position.position
                    required_position = (
                        "LONG"
                        if step.source_execution_action == "CLOSE_LONG"
                        else "SHORT"
                    )
                    unmatched_autonomous_exit = (
                        step.source_event_kind == SOURCE_EVENT_AUTONOMOUS_EXIT
                        and position_before != required_position
                    )
                    if unmatched_autonomous_exit:
                        pending = pending_guard_divergences.get(required_position)
                        current_reasons = sandbox.evaluate_entry_block_reasons(
                            entry_timestamp_utc=step.timestamp_utc,
                        )
                        shared_reasons = (
                            ()
                            if pending is None
                            else tuple(
                                reason
                                for reason in pending.guard_reason_codes
                                if reason in current_reasons
                            )
                        )
                        if (
                            position_before != "FLAT"
                            or pending is None
                            or state_before.state_fingerprint
                            != pending.sandbox_state_fingerprint
                            or not shared_reasons
                        ):
                            raise IU4ShadowHarnessError(
                                IU4ShadowHarnessReasonCode.STEP_INVALID,
                                "autonomous exit execution does not match the sandbox position",
                            )
                        noop = adapter.execute(
                            self._guard_divergence_noop_request(step, sandbox)
                        )
                        if (
                            noop.status != STATUS_NOOP
                            or noop.state != state_before
                            or noop.action != "NOOP"
                        ):
                            raise IU4ShadowHarnessError(
                                IU4ShadowHarnessReasonCode.SANDBOX_INVALID,
                                "guard-divergence exit suppression must be a state-exact NOOP",
                            )
                        outcome = replace(
                            noop,
                            reason_code=GUARD_DIVERGENCE_EXIT_SUPPRESSED,
                        )
                        guard_divergence_values.append(
                            IU4ShadowGuardDivergenceV1(
                                schema_version=1,
                                position_side=required_position,
                                first_rejected_step_index=(
                                    pending.first_rejected_step_index
                                ),
                                first_rejected_source_intent_id=(
                                    pending.first_rejected_source_intent_id
                                ),
                                last_rejected_step_index=(
                                    pending.last_rejected_step_index
                                ),
                                last_rejected_source_intent_id=(
                                    pending.last_rejected_source_intent_id
                                ),
                                rejected_entry_count=pending.rejected_entry_count,
                                guard_reason_codes=shared_reasons,
                                sandbox_state_fingerprint=(
                                    pending.sandbox_state_fingerprint
                                ),
                                suppressed_exit_step_index=index,
                                suppressed_exit_source_intent_id=(
                                    step.source_intent_id
                                ),
                                suppressed_exit_action=(
                                    step.source_execution_action
                                ),
                                suppressed_exit_sequence=(
                                    step.source_execution_sequence
                                ),
                            )
                        )
                        pending_guard_divergences.pop(required_position, None)
                    else:
                        candidate_guard_reasons = (
                            sandbox.evaluate_entry_block_reasons(
                                entry_timestamp_utc=step.timestamp_utc,
                            )
                            if position_before == "FLAT"
                            and step.source_event_kind == SOURCE_EVENT_INTENT
                            and step.intent_final in ("BUY", "SELL")
                            else ()
                        )
                        outcome = adapter.execute(self._request_for(step, sandbox))
                        opening_side = {
                            "OPEN_LONG": "LONG",
                            "OPEN_SHORT": "SHORT",
                        }.get(outcome.action)
                        if (
                            outcome.status == STATUS_REJECTED
                            and opening_side is not None
                            and candidate_guard_reasons
                            and outcome.reason_code in candidate_guard_reasons
                        ):
                            existing = pending_guard_divergences.get(opening_side)
                            shared_reasons = (
                                candidate_guard_reasons
                                if existing is None
                                else tuple(
                                    reason
                                    for reason in existing.guard_reason_codes
                                    if reason in candidate_guard_reasons
                                )
                            )
                            if (
                                existing is None
                                or existing.sandbox_state_fingerprint
                                != state_before.state_fingerprint
                                or not shared_reasons
                            ):
                                pending_guard_divergences[opening_side] = (
                                    _PendingGuardDivergence(
                                        position_side=opening_side,
                                        first_rejected_step_index=index,
                                        first_rejected_source_intent_id=(
                                            step.source_intent_id
                                        ),
                                        last_rejected_step_index=index,
                                        last_rejected_source_intent_id=(
                                            step.source_intent_id
                                        ),
                                        rejected_entry_count=1,
                                        guard_reason_codes=candidate_guard_reasons,
                                        sandbox_state_fingerprint=(
                                            state_before.state_fingerprint
                                        ),
                                    )
                                )
                            else:
                                pending_guard_divergences[opening_side] = replace(
                                    existing,
                                    last_rejected_step_index=index,
                                    last_rejected_source_intent_id=(
                                        step.source_intent_id
                                    ),
                                    rejected_entry_count=(
                                        existing.rejected_entry_count + 1
                                    ),
                                    guard_reason_codes=shared_reasons,
                                )
                        elif outcome.status == STATUS_COMMITTED:
                            pending_guard_divergences.clear()
                    outcome_values.append(outcome)
                except PaperIU4AdapterError as exc:
                    raise IU4ShadowHarnessError(
                        IU4ShadowHarnessReasonCode.STEP_INVALID,
                        exc.detail,
                    ) from exc
                except PaperAtomicCoordinatorError as exc:
                    raise IU4ShadowHarnessError(
                        IU4ShadowHarnessReasonCode.SANDBOX_INVALID,
                        str(exc),
                    ) from exc
                if progress_callback is not None and (
                    index % progress_interval_steps == 0
                    or index == len(step_values)
                ):
                    progress_callback(index, len(step_values))
                if index == restart_after_steps:
                    restart_report = sandbox.reconciliation_report()
                    restart_state = sandbox.load_state()
                    if not restart_report.consistent:
                        raise IU4ShadowHarnessError(
                            IU4ShadowHarnessReasonCode.SANDBOX_INVALID,
                            "sandbox is inconsistent at the controlled restart boundary",
                        )
                    restart_position = restart_state.position.position
                    restart_state_fingerprint = restart_state.state_fingerprint
                    restart_transaction_sequence = restart_state.transaction_sequence
                    if restart_fault_injection is not None:
                        (
                            restart_fault_snapshot_sha256_before,
                            restart_fault_snapshot_sha256_after,
                        ) = _inject_truncated_snapshot(sandbox.state_path)
                        sandbox = PaperAtomicCoordinator(
                            sandbox_root,
                            self.source_coordinator.config,
                            self.source_coordinator.throttle_policy,
                            coordinator_id=self.source_coordinator.coordinator_id,
                            symbol=self.source_coordinator.symbol,
                        )
                        fault_report = sandbox.reconciliation_report()
                        restart_fault_detected = not fault_report.consistent
                        restart_fault_reason_codes = fault_report.reason_codes
                        continuation_blocked = restart_fault_detected
                        if not restart_fault_detected:
                            raise IU4ShadowHarnessError(
                                IU4ShadowHarnessReasonCode.SANDBOX_INVALID,
                                "injected restart fault was not detected",
                            )
                        break
                    sandbox = PaperAtomicCoordinator(
                        sandbox_root,
                        self.source_coordinator.config,
                        self.source_coordinator.throttle_policy,
                        coordinator_id=self.source_coordinator.coordinator_id,
                        symbol=self.source_coordinator.symbol,
                    )
                    recovered_report = sandbox.reconciliation_report()
                    recovered_state = sandbox.load_state()
                    restart_state_restored = (
                        recovered_report.consistent
                        and recovered_state == restart_state
                        and recovered_state.state_fingerprint
                        == restart_state_fingerprint
                        and recovered_state.transaction_sequence
                        == restart_transaction_sequence
                    )
                    if not restart_state_restored:
                        raise IU4ShadowHarnessError(
                            IU4ShadowHarnessReasonCode.SANDBOX_INVALID,
                            "controlled restart did not restore the exact atomic state",
                        )
                    adapter = PaperIU4Adapter(sandbox)
            outcomes = tuple(outcome_values)
            if continuation_blocked:
                final_state = restart_state
                sandbox_consistent = False
            else:
                final_report = sandbox.reconciliation_report()
                final_state = sandbox.load_state()
                if not final_report.consistent:
                    raise IU4ShadowHarnessError(
                        IU4ShadowHarnessReasonCode.SANDBOX_INVALID,
                        "sandbox became inconsistent during dry-run execution",
                    )
                sandbox_consistent = True

        final_source_entries, final_manifest_fingerprint = _manifest(
            self.source_coordinator
        )
        final_source_state = self.source_coordinator.load_state()
        if (
            final_source_entries != source_entries
            or final_manifest_fingerprint != manifest_fingerprint
            or final_source_state != source_state
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.SOURCE_CHANGED,
                "source coordinator changed during the dry run",
            )
        statuses = tuple(outcome.status for outcome in outcomes)
        return IU4ShadowDryRunReportV1(
            schema_version=1,
            source_manifest_fingerprint=manifest_fingerprint,
            source_initial_state_fingerprint=source_state.state_fingerprint,
            source_final_state_fingerprint=final_source_state.state_fingerprint,
            sandbox_final_state_fingerprint=final_state.state_fingerprint,
            source_initial_transaction_sequence=source_state.transaction_sequence,
            sandbox_final_transaction_sequence=final_state.transaction_sequence,
            simulated_transaction_count=(
                final_state.transaction_sequence - source_state.transaction_sequence
            ),
            step_count=len(outcomes),
            committed_step_count=statuses.count(STATUS_COMMITTED),
            noop_step_count=statuses.count(STATUS_NOOP),
            rejected_step_count=statuses.count(STATUS_REJECTED),
            requested_step_count=len(step_values),
            restart_enabled=restart_after_steps is not None,
            restart_after_step=(
                0 if restart_after_steps is None else restart_after_steps
            ),
            restart_count=0 if restart_after_steps is None else 1,
            restart_position=restart_position,
            restart_state_fingerprint=restart_state_fingerprint,
            restart_transaction_sequence=restart_transaction_sequence,
            restart_state_restored=restart_state_restored,
            restart_fault_injection=(
                "" if restart_fault_injection is None else restart_fault_injection
            ),
            restart_fault_detected=restart_fault_detected,
            restart_fault_reason_codes=restart_fault_reason_codes,
            restart_fault_snapshot_sha256_before=(
                restart_fault_snapshot_sha256_before
            ),
            restart_fault_snapshot_sha256_after=(
                restart_fault_snapshot_sha256_after
            ),
            continuation_blocked=continuation_blocked,
            source_unchanged=True,
            sandbox_consistent=sandbox_consistent,
            guard_divergence_count=len(guard_divergence_values),
            guard_divergences=tuple(guard_divergence_values),
            outcomes=outcomes,
        )


__all__ = [
    "IU4ShadowDryRunReportV1",
    "IU4ShadowHarnessError",
    "IU4ShadowHarnessReasonCode",
    "IU4ShadowGuardDivergenceV1",
    "IU4ShadowIntentStepV1",
    "GUARD_DIVERGENCE_EXIT_SUPPRESSED",
    "PaperIU4ShadowDryRunHarness",
    "RESTART_FAULT_SNAPSHOT_TRUNCATED",
    "SOURCE_EVENT_AUTONOMOUS_EXIT",
    "SOURCE_EVENT_INTENT",
]
