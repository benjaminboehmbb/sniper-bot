#!/usr/bin/env python3
"""Bounded, fail-closed per-tick IU-4 SHADOW observation gate."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

from live_l1.core.paper_economics_shadow import (
    DECIMAL_CONTEXT,
    ONE,
    load_shadow_settings,
)
from live_l1.core.paper_iu4_adapter import (
    IU4AdapterRequestV1,
    PaperIU4Adapter,
    PaperIU4AdapterError,
)
from live_l1.core.paper_iu4_shadow_runtime_gate import IU4ShadowRuntimeGateV1
from live_l1.state.paper_artifacts import canonical_decimal
from live_l1.state.paper_atomic_coordinator import (
    PaperAtomicCoordinator,
    PaperAtomicCoordinatorError,
)


ENV_OBSERVATION_ENABLED = "L1_IU4_SHADOW_OBSERVATION_ENABLED"
ENV_OBSERVATION_EVIDENCE_PATH = "L1_IU4_SHADOW_OBSERVATION_EVIDENCE_PATH"
ENV_OBSERVATION_MAX_RECORDS = "L1_IU4_SHADOW_OBSERVATION_MAX_RECORDS"
ENV_OBSERVATION_WORK_DIRECTORY = "L1_IU4_SHADOW_OBSERVATION_WORK_DIRECTORY"
MAX_OBSERVATION_RECORDS = 10_000


class IU4ShadowObservationReasonCode:
    READY = "PEE_IU4_SHADOW_OBSERVATION_READY"
    DISABLED = "PEE_IU4_SHADOW_OBSERVATION_DISABLED"
    CONFIG_INVALID = "PEE_IU4_SHADOW_OBSERVATION_CONFIG_INVALID"
    GATE_INVALID = "PEE_IU4_SHADOW_OBSERVATION_GATE_INVALID"
    SOURCE_CHANGED = "PEE_IU4_SHADOW_OBSERVATION_SOURCE_CHANGED"
    SANDBOX_INVALID = "PEE_IU4_SHADOW_OBSERVATION_SANDBOX_INVALID"
    LIMIT_REACHED = "PEE_IU4_SHADOW_OBSERVATION_LIMIT_REACHED"
    EVIDENCE_INVALID = "PEE_IU4_SHADOW_OBSERVATION_EVIDENCE_INVALID"


class IU4ShadowObservationError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _atomic_write(path: Path, payload: Mapping[str, Any]) -> None:
    encoded = _canonical_json(payload) + b"\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def _source_entries(coordinator: PaperAtomicCoordinator) -> tuple[dict[str, Any], ...]:
    root = coordinator.root_directory.resolve()
    paths = [coordinator.state_path]
    if coordinator.transaction_directory.exists():
        if (
            not coordinator.transaction_directory.is_dir()
            or coordinator.transaction_directory.is_symlink()
        ):
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SANDBOX_INVALID,
                "atomic transaction source must be a regular directory",
            )
        paths.extend(sorted(coordinator.transaction_directory.glob("*.json")))
    entries: list[dict[str, Any]] = []
    for path in paths:
        if not path.is_file() or path.is_symlink():
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SANDBOX_INVALID,
                "atomic source contains a non-regular file",
            )
        payload = path.read_bytes()
        entries.append(
            {
                "relative_path": path.resolve().relative_to(root).as_posix(),
                "size_bytes": len(payload),
                "sha256": _sha256(payload),
            }
        )
    return tuple(entries)


def _manifest_fingerprint(entries: tuple[dict[str, Any], ...]) -> str:
    return _sha256(_canonical_json(entries))


def _positive_integer(value: object, name: str) -> int:
    text = str(value).strip()
    try:
        result = int(text)
    except ValueError as exc:
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            f"{name} must be a positive integer",
        ) from exc
    if str(result) != text or result < 1:
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            f"{name} must be a canonical positive integer",
        )
    return result


def _candidate_stop(intent: str, price: Decimal, stop_rate: Decimal) -> Decimal | None:
    if intent not in ("BUY", "SELL"):
        return None
    multiplier = (
        DECIMAL_CONTEXT.subtract(ONE, stop_rate)
        if intent == "BUY"
        else DECIMAL_CONTEXT.add(ONE, stop_rate)
    )
    return DECIMAL_CONTEXT.multiply(price, multiplier)


def _trade_id(
    *,
    source_intent_id: str,
    system_state_id: str,
    tick_id: int,
    timestamp_utc: str,
    intent: str,
    reference_price: Decimal,
    reference_stop_price: Decimal,
) -> str:
    identity = {
        "source_intent_id": source_intent_id,
        "system_state_id": system_state_id,
        "source_tick": tick_id,
        "timestamp_utc": timestamp_utc,
        "intent": intent,
        "reference_price": canonical_decimal(reference_price),
        "reference_stop_price": canonical_decimal(reference_stop_price),
    }
    return f"PEE-IU4-TRADE-{_sha256(_canonical_json(identity))}"


class PaperIU4ShadowRuntimeObserver:
    """Execute IU-4 only against a disposable clone and persist bounded evidence."""

    def __init__(
        self,
        *,
        runtime_gate: IU4ShadowRuntimeGateV1,
        evidence_path: Path,
        max_records: int,
        reference_stop_rate: Decimal,
        work_directory: Path | None,
    ) -> None:
        coordinator = runtime_gate.coordinator
        if coordinator is None or not runtime_gate.shadow_enabled:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.GATE_INVALID,
                "observer requires the passed read-only IU4 SHADOW runtime gate",
            )
        runtime_gate.assert_current_binding()
        self.runtime_gate = runtime_gate
        self.source = coordinator
        self.evidence_path = evidence_path
        self.max_records = max_records
        self.reference_stop_rate = reference_stop_rate
        self.records: list[dict[str, Any]] = []
        self.source_intent_ids: set[str] = set()
        self._last_evidence_sha256 = ""
        self.source_entries = _source_entries(self.source)
        self.source_manifest_fingerprint = _manifest_fingerprint(self.source_entries)
        self.source_state = self.source.load_state()
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="pee-iu4-runtime-shadow-",
            dir=None if work_directory is None else str(work_directory),
        )
        self.sandbox_root = Path(self._temporary_directory.name).resolve()
        source_root = self.source.root_directory.resolve()
        for entry in self.source_entries:
            source_path = source_root / str(entry["relative_path"])
            target_path = self.sandbox_root / str(entry["relative_path"])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target_path)
        if _manifest_fingerprint(_source_entries(self.source)) != self.source_manifest_fingerprint:
            self.close()
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SOURCE_CHANGED,
                "atomic source changed while the runtime sandbox was cloned",
            )
        self.sandbox = PaperAtomicCoordinator(
            self.sandbox_root,
            self.source.config,
            self.source.throttle_policy,
            coordinator_id=self.source.coordinator_id,
            symbol=self.source.symbol,
        )
        sandbox_report = self.sandbox.reconciliation_report()
        sandbox_state = self.sandbox.load_state()
        if not sandbox_report.consistent or sandbox_state != self.source_state:
            self.close()
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SANDBOX_INVALID,
                "runtime sandbox is not an exact reconciled source clone",
            )
        self.adapter = PaperIU4Adapter(self.sandbox)
        self._publish()

    def _payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "artifact_type": "PEE_IU4_SHADOW_RUNTIME_OBSERVATION_EVIDENCE",
            "schema_version": 1,
            "repository_commit_sha": self.runtime_gate.running_repository_commit_sha,
            "source_manifest_fingerprint": self.source_manifest_fingerprint,
            "source_initial_state_fingerprint": self.source_state.state_fingerprint,
            "source_initial_transaction_sequence": self.source_state.transaction_sequence,
            "max_records": self.max_records,
            "record_count": len(self.records),
            "adapter_execution_scope": "DISPOSABLE_SANDBOX_ONLY",
            "source_state_mutation_allowed": False,
            "exchange_enabled": False,
            "live_enabled": False,
            "records": self.records,
        }
        payload["evidence_fingerprint"] = _sha256(_canonical_json(payload))
        return payload

    def _publish(self) -> None:
        try:
            if self.evidence_path.exists():
                current_sha256 = _sha256(self.evidence_path.read_bytes())
                if (
                    not self._last_evidence_sha256
                    or current_sha256 != self._last_evidence_sha256
                ):
                    raise IU4ShadowObservationError(
                        IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
                        "observation evidence changed outside the active observer",
                    )
            _atomic_write(self.evidence_path, self._payload())
            self._last_evidence_sha256 = _sha256(self.evidence_path.read_bytes())
        except IU4ShadowObservationError:
            raise
        except Exception as exc:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
                str(exc),
            ) from exc

    def _assert_source_unchanged(self) -> None:
        self.runtime_gate.assert_current_binding()
        if _manifest_fingerprint(_source_entries(self.source)) != self.source_manifest_fingerprint:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SOURCE_CHANGED,
                "atomic source changed during runtime observation",
            )

    def observe_tick(
        self,
        *,
        system_state_id: str,
        tick_id: int,
        snapshot_id: str,
        timestamp_utc: str,
        source_intent_id: str,
        intent_final: str,
        intent_reason_code: str,
        reference_price_text: str,
        legacy_execution: object,
        guard_reason: str,
        s4_kill_level: str,
    ) -> dict[str, Any]:
        if len(self.records) >= self.max_records:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.LIMIT_REACHED,
                "bounded IU4 observation evidence limit was reached",
            )
        if source_intent_id in self.source_intent_ids:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
                "duplicate source intent ID in runtime observation",
            )
        self._assert_source_unchanged()
        try:
            before = self.sandbox.load_state()
        except PaperAtomicCoordinatorError as exc:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SANDBOX_INVALID,
                str(exc),
            ) from exc
        legacy_before = str(getattr(legacy_execution, "position_before", "")).strip().upper()
        intent = str(intent_final).strip().upper()
        legacy_action = str(getattr(legacy_execution, "action", "")).strip().upper()
        legacy_executed = bool(getattr(legacy_execution, "executed", False))
        autonomous_exit = intent == "HOLD" and legacy_executed and legacy_action in (
            "CLOSE_LONG",
            "CLOSE_SHORT",
        )
        autonomous_exit_required_position = {
            "CLOSE_LONG": "LONG",
            "CLOSE_SHORT": "SHORT",
        }.get(legacy_action, "")
        autonomous_exit_position_match = (
            not autonomous_exit
            or before.position.position == autonomous_exit_required_position
        )
        if autonomous_exit and autonomous_exit_position_match:
            intent = "SELL" if legacy_action == "CLOSE_LONG" else "BUY"
        try:
            price = Decimal(str(reference_price_text).strip())
        except Exception as exc:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SANDBOX_INVALID,
                "reference price is not a decimal",
            ) from exc
        if not price.is_finite() or price <= 0:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SANDBOX_INVALID,
                "reference price must be finite and positive",
            )
        opens = before.position.position == "FLAT" and intent in ("BUY", "SELL")
        closes = (
            before.position.position == "LONG" and intent == "SELL"
        ) or (
            before.position.position == "SHORT" and intent == "BUY"
        )
        stop = _candidate_stop(intent, price, self.reference_stop_rate) if opens else None
        trade_id = (
            _trade_id(
                source_intent_id=source_intent_id,
                system_state_id=system_state_id,
                tick_id=tick_id,
                timestamp_utc=timestamp_utc,
                intent=intent,
                reference_price=price,
                reference_stop_price=stop,
            )
            if stop is not None
            else getattr(before.position, "trade_id", "")
        )
        request = IU4AdapterRequestV1(
            schema_version=1,
            request_id="",
            source_intent_id=source_intent_id,
            intent_final=intent,
            intent_reason_code=(
                str(getattr(legacy_execution, "reason", intent_reason_code))
                if intent != intent_final and closes
                else intent_reason_code
            ),
            expected_state_fingerprint=before.state_fingerprint,
            target_system_state_id=(
                system_state_id if opens or closes else before.position.system_state_id
            ),
            timestamp_utc=timestamp_utc,
            tick_id=tick_id,
            reference_price=price,
            reference_stop_price=stop,
            trade_id=trade_id,
        )
        try:
            result = self.adapter.execute(request)
            after = self.sandbox.load_state()
        except (PaperIU4AdapterError, PaperAtomicCoordinatorError) as exc:
            raise IU4ShadowObservationError(
                IU4ShadowObservationReasonCode.SANDBOX_INVALID,
                str(exc),
            ) from exc
        self._assert_source_unchanged()
        record = {
            "sequence": len(self.records) + 1,
            "tick_id": tick_id,
            "snapshot_id": snapshot_id,
            "timestamp_utc": timestamp_utc,
            "system_state_id": system_state_id,
            "source_intent_id": source_intent_id,
            "source_intent_final": intent_final,
            "observed_intent_final": intent,
            "autonomous_exit": autonomous_exit,
            "autonomous_exit_required_position": autonomous_exit_required_position,
            "autonomous_exit_position_match": autonomous_exit_position_match,
            "autonomous_exit_suppressed": (
                autonomous_exit and not autonomous_exit_position_match
            ),
            "intent_reason_code": intent_reason_code,
            "reference_price": canonical_decimal(price),
            "legacy": {
                "action": legacy_action,
                "executed": legacy_executed,
                "position_before": legacy_before,
                "position_after": str(
                    getattr(legacy_execution, "position_after", "")
                ).strip().upper(),
                "reason": str(getattr(legacy_execution, "reason", "")),
                "guard_reason": str(guard_reason),
                "s4_kill_level": str(s4_kill_level),
            },
            "iu4": {
                "request_id": request.request_id,
                "status": result.status,
                "action": result.action,
                "reason_code": result.reason_code,
                "position_before": before.position.position,
                "position_after": after.position.position,
                "state_fingerprint_before": before.state_fingerprint,
                "state_fingerprint_after": after.state_fingerprint,
                "transaction_sequence_before": before.transaction_sequence,
                "transaction_sequence_after": after.transaction_sequence,
            },
            "parity": {
                "position_before_equal": legacy_before == before.position.position,
                "action_equal": legacy_action == result.action,
                "position_after_equal": str(
                    getattr(legacy_execution, "position_after", "")
                ).strip().upper()
                == after.position.position,
            },
        }
        self.source_intent_ids.add(source_intent_id)
        self.records.append(record)
        self._publish()
        return record

    def close(self) -> None:
        temporary = getattr(self, "_temporary_directory", None)
        if temporary is not None:
            temporary.cleanup()
            self._temporary_directory = None


@dataclass(frozen=True)
class IU4ShadowObservationGateV1:
    enabled: bool
    reason_code: str
    max_records: int
    evidence_path: Path | None
    observer: PaperIU4ShadowRuntimeObserver | None

    def startup_log_fields(self) -> dict[str, object]:
        return {
            "iu4_shadow_observation_enabled": int(self.enabled),
            "iu4_shadow_observation_reason_code": self.reason_code,
            "iu4_shadow_observation_max_records": self.max_records,
            "iu4_shadow_observation_evidence_path": (
                "" if self.evidence_path is None else str(self.evidence_path)
            ),
            "iu4_shadow_observation_adapter_scope": (
                "DISABLED" if not self.enabled else "DISPOSABLE_SANDBOX_ONLY"
            ),
        }


def _disabled() -> IU4ShadowObservationGateV1:
    return IU4ShadowObservationGateV1(
        enabled=False,
        reason_code=IU4ShadowObservationReasonCode.DISABLED,
        max_records=0,
        evidence_path=None,
        observer=None,
    )


def evaluate_iu4_shadow_observation_gate(
    *,
    repo_root: str | Path,
    environment: Mapping[str, str],
    runtime_gate: IU4ShadowRuntimeGateV1,
    requested_max_ticks: int,
) -> IU4ShadowObservationGateV1:
    enabled_text = str(environment.get(ENV_OBSERVATION_ENABLED, "0")).strip()
    if enabled_text not in ("0", "1"):
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            f"{ENV_OBSERVATION_ENABLED} must be exactly 0 or 1",
        )
    if enabled_text == "0":
        return _disabled()
    if not runtime_gate.shadow_enabled or runtime_gate.coordinator is None:
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.GATE_INVALID,
            "observation requires an active read-only IU4 SHADOW runtime gate",
        )
    max_records = _positive_integer(
        environment.get(ENV_OBSERVATION_MAX_RECORDS, ""),
        ENV_OBSERVATION_MAX_RECORDS,
    )
    if max_records > MAX_OBSERVATION_RECORDS:
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            f"observation max exceeds hard limit {MAX_OBSERVATION_RECORDS}",
        )
    if requested_max_ticks < 1 or requested_max_ticks > max_records:
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            "requested max ticks must be positive and no greater than evidence max records",
        )
    root = Path(repo_root).resolve()
    evidence_text = str(environment.get(ENV_OBSERVATION_EVIDENCE_PATH, "")).strip()
    if not evidence_text:
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            "observation evidence path is required",
        )
    evidence_path = Path(evidence_text)
    if not evidence_path.is_absolute():
        evidence_path = root / evidence_path
    evidence_path = evidence_path.absolute()
    if evidence_path.exists():
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
            "observation evidence path already exists",
        )
    parent = evidence_path.parent
    if not parent.is_dir() or parent.is_symlink() or parent.resolve() != parent.absolute():
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
            "observation evidence parent must be an existing non-symlink directory",
        )
    source_root = runtime_gate.coordinator.root_directory.resolve()
    if evidence_path == source_root or source_root in evidence_path.parents:
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.EVIDENCE_INVALID,
            "observation evidence must be outside the atomic source tree",
        )
    work_text = str(environment.get(ENV_OBSERVATION_WORK_DIRECTORY, "")).strip()
    work_directory = None if not work_text else Path(work_text)
    if work_directory is not None and not work_directory.is_absolute():
        work_directory = root / work_directory
    if work_directory is not None:
        work_directory = work_directory.absolute()
    if work_directory is not None and (
        not work_directory.is_dir()
        or work_directory.is_symlink()
        or work_directory.resolve() != work_directory
        or work_directory == source_root
        or source_root in work_directory.parents
    ):
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            "observation work directory must be an existing non-symlink directory outside the source tree",
        )
    settings = load_shadow_settings(environment)
    if not settings.ready or settings.reference_stop_rate is None:
        raise IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            "approved shadow economics stop-rate configuration is required",
        )
    observer = PaperIU4ShadowRuntimeObserver(
        runtime_gate=runtime_gate,
        evidence_path=evidence_path,
        max_records=max_records,
        reference_stop_rate=settings.reference_stop_rate,
        work_directory=work_directory,
    )
    return IU4ShadowObservationGateV1(
        enabled=True,
        reason_code=IU4ShadowObservationReasonCode.READY,
        max_records=max_records,
        evidence_path=evidence_path,
        observer=observer,
    )


__all__ = [
    "ENV_OBSERVATION_ENABLED",
    "ENV_OBSERVATION_EVIDENCE_PATH",
    "ENV_OBSERVATION_MAX_RECORDS",
    "ENV_OBSERVATION_WORK_DIRECTORY",
    "IU4ShadowObservationError",
    "IU4ShadowObservationGateV1",
    "IU4ShadowObservationReasonCode",
    "MAX_OBSERVATION_RECORDS",
    "PaperIU4ShadowRuntimeObserver",
    "evaluate_iu4_shadow_observation_gate",
]
