#!/usr/bin/env python3
"""Isolated SHADOW dry-run harness for the inactive IU-4 Paper adapter.

The harness clones validated atomic state into a temporary directory and lets
the real IU-4 adapter mutate only that disposable clone.  Source coordinator
files are hashed before and after every run and are never opened for writing.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence

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

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "IU4ShadowIntentStepV1 requires schema_version 1",
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

    def to_record(self) -> dict[str, Any]:
        return {
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

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "IU4ShadowIntentStepV1":
        expected_fields = set(cls.__dataclass_fields__)
        if set(record) != expected_fields:
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "IU4 shadow replay step fields are missing or unknown",
            )
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})


@dataclass(frozen=True)
class IU4ShadowSourceFileV1:
    relative_path: str
    size_bytes: int
    sha256: str


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
    source_unchanged: bool
    sandbox_consistent: bool
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
        return IU4AdapterRequestV1(
            schema_version=1,
            request_id="",
            source_intent_id=step.source_intent_id,
            intent_final=step.intent_final,
            intent_reason_code=step.intent_reason_code,
            expected_state_fingerprint=state.state_fingerprint,
            target_system_state_id=step.target_system_state_id,
            timestamp_utc=step.timestamp_utc,
            tick_id=step.tick_id,
            reference_price=step.reference_price,
            reference_stop_price=step.reference_stop_price,
            trade_id=step.trade_id,
        )

    def run(
        self,
        steps: Sequence[IU4ShadowIntentStepV1],
    ) -> IU4ShadowDryRunReportV1:
        if isinstance(steps, (str, bytes)) or not isinstance(steps, Sequence):
            raise IU4ShadowHarnessError(
                IU4ShadowHarnessReasonCode.STEP_INVALID,
                "steps must be a finite sequence",
            )
        step_values = tuple(steps)
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
            for step in step_values:
                try:
                    outcome_values.append(
                        adapter.execute(self._request_for(step, sandbox))
                    )
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
            outcomes = tuple(outcome_values)
            final_report = sandbox.reconciliation_report()
            final_state = sandbox.load_state()
            if not final_report.consistent:
                raise IU4ShadowHarnessError(
                    IU4ShadowHarnessReasonCode.SANDBOX_INVALID,
                    "sandbox became inconsistent during dry-run execution",
                )

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
            step_count=len(step_values),
            committed_step_count=statuses.count(STATUS_COMMITTED),
            noop_step_count=statuses.count(STATUS_NOOP),
            rejected_step_count=statuses.count(STATUS_REJECTED),
            source_unchanged=True,
            sandbox_consistent=True,
            outcomes=outcomes,
        )


__all__ = [
    "IU4ShadowDryRunReportV1",
    "IU4ShadowHarnessError",
    "IU4ShadowHarnessReasonCode",
    "IU4ShadowIntentStepV1",
    "PaperIU4ShadowDryRunHarness",
]
