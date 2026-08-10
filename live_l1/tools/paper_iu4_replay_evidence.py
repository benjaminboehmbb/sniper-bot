#!/usr/bin/env python3
"""Strict IU-4 SHADOW JSONL replay and immutable evidence export."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from live_l1.core.paper_entry_throttle import canonical_utc_timestamp
from live_l1.core.paper_iu4_adapter import IU4AdapterResultV1
from live_l1.core.paper_iu4_shadow_harness import (
    GUARD_DIVERGENCE_EXIT_SUPPRESSED,
    IU4ShadowDryRunReportV1,
    IU4ShadowGuardDivergenceV1,
    IU4ShadowIntentStepV1,
    PaperIU4ShadowDryRunHarness,
)


class IU4ReplayEvidenceReasonCode:
    INPUT_INVALID = "PEE_IU4_REPLAY_INPUT_INVALID"
    ORDER_INVALID = "PEE_IU4_REPLAY_ORDER_INVALID"
    OUTPUT_INVALID = "PEE_IU4_REPLAY_OUTPUT_INVALID"
    OUTPUT_CONFLICT = "PEE_IU4_REPLAY_OUTPUT_CONFLICT"
    WRITE_FAILED = "PEE_IU4_REPLAY_WRITE_FAILED"


class IU4ReplayEvidenceError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


@dataclass(frozen=True)
class IU4ReplayInputV1:
    path: Path
    sha256: str
    size_bytes: int
    line_count: int
    steps: tuple[IU4ShadowIntentStepV1, ...]


@dataclass(frozen=True)
class IU4ReplayEvidenceExportV1:
    output_path: Path
    evidence: Mapping[str, Any]
    output_sha256: str
    newly_written: bool
    already_exists: bool


@dataclass(frozen=True)
class IU4ReplayJsonlExportV1:
    output_path: Path
    output_sha256: str
    size_bytes: int
    line_count: int
    newly_written: bool
    already_exists: bool


def _reject_float(_: str) -> None:
    raise ValueError("JSON floating-point numbers are forbidden; use decimal strings")


def _reject_constant(_: str) -> None:
    raise ValueError("non-finite JSON constants are forbidden")


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


def load_iu4_replay_jsonl(path: str | Path) -> IU4ReplayInputV1:
    source = Path(path)
    if not source.is_file() or source.is_symlink():
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "replay input must be a regular, non-symlink file",
        )
    source = source.resolve()
    raw = source.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "replay input must be UTF-8",
        ) from exc

    lines = text.splitlines()
    if not lines:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "replay input must contain at least one JSONL step",
        )

    steps: list[IU4ShadowIntentStepV1] = []
    seen_ids: set[str] = set()
    previous_timestamp = ""
    previous_tick = -1
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                f"blank JSONL line {line_number} is forbidden",
            )
        try:
            record = json.loads(
                line,
                parse_float=_reject_float,
                parse_constant=_reject_constant,
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                f"invalid JSONL line {line_number}: {exc}",
            ) from exc
        if not isinstance(record, dict):
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                f"JSONL line {line_number} must be an object",
            )
        try:
            step = IU4ShadowIntentStepV1.from_record(record)
        except Exception as exc:
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                f"invalid replay step on line {line_number}: {exc}",
            ) from exc
        if step.source_intent_id in seen_ids:
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.ORDER_INVALID,
                f"duplicate source_intent_id on line {line_number}",
            )
        if previous_timestamp and step.timestamp_utc <= previous_timestamp:
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.ORDER_INVALID,
                f"timestamps must be strictly increasing at line {line_number}",
            )
        if step.tick_id <= previous_tick:
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.ORDER_INVALID,
                f"tick_id values must be strictly increasing at line {line_number}",
            )
        seen_ids.add(step.source_intent_id)
        previous_timestamp = step.timestamp_utc
        previous_tick = step.tick_id
        steps.append(step)

    return IU4ReplayInputV1(
        path=source,
        sha256=_sha256(raw),
        size_bytes=len(raw),
        line_count=len(lines),
        steps=tuple(steps),
    )


def _outcome_record(
    index: int,
    outcome: IU4AdapterResultV1,
    step: IU4ShadowIntentStepV1,
    guard_divergence: IU4ShadowGuardDivergenceV1 | None = None,
) -> dict[str, Any]:
    state = outcome.state
    position = state.position
    return {
        "index": index,
        "source_intent_id": outcome.source_intent_id,
        "source_event_kind": step.source_event_kind,
        "source_intent_final": step.source_intent_final,
        "source_execution_action": step.source_execution_action,
        "source_execution_sequence": step.source_execution_sequence,
        "request_id": outcome.request_id,
        "status": outcome.status,
        "action": outcome.action,
        "reason_code": outcome.reason_code,
        "transaction_event_id": outcome.transaction_event_id,
        "newly_committed": outcome.newly_committed,
        "already_committed": outcome.already_committed,
        "recovered_incomplete_commit": outcome.recovered_incomplete_commit,
        "state_fingerprint": state.state_fingerprint,
        "transaction_sequence": state.transaction_sequence,
        "position": position.position,
        "trade_id": getattr(position, "trade_id", ""),
        "last_closed_trade_id": getattr(position, "last_closed_trade_id", ""),
        "position_fingerprint": position.state_fingerprint,
        "account_fingerprint": state.account.state_fingerprint,
        "throttle_fingerprint": state.throttle.state_fingerprint,
        "risk_fingerprint": state.risk.state_fingerprint,
        "kill_level": state.risk.kill_level,
        "entry_allowed": state.risk.entry_allowed,
        "exit_allowed": state.risk.exit_allowed,
        "guard_divergence": (
            None
            if guard_divergence is None
            else _guard_divergence_record(guard_divergence)
        ),
    }


def _guard_divergence_record(
    divergence: IU4ShadowGuardDivergenceV1,
) -> dict[str, Any]:
    return {
        "schema_version": divergence.schema_version,
        "position_side": divergence.position_side,
        "first_rejected_step_index": divergence.first_rejected_step_index,
        "first_rejected_source_intent_id": (
            divergence.first_rejected_source_intent_id
        ),
        "last_rejected_step_index": divergence.last_rejected_step_index,
        "last_rejected_source_intent_id": (
            divergence.last_rejected_source_intent_id
        ),
        "rejected_entry_count": divergence.rejected_entry_count,
        "guard_reason_codes": list(divergence.guard_reason_codes),
        "sandbox_state_fingerprint": divergence.sandbox_state_fingerprint,
        "suppressed_exit_step_index": divergence.suppressed_exit_step_index,
        "suppressed_exit_source_intent_id": (
            divergence.suppressed_exit_source_intent_id
        ),
        "suppressed_exit_action": divergence.suppressed_exit_action,
        "suppressed_exit_sequence": divergence.suppressed_exit_sequence,
    }


def _validated_guard_divergences(
    *,
    replay: IU4ReplayInputV1,
    report: IU4ShadowDryRunReportV1,
) -> dict[int, IU4ShadowGuardDivergenceV1]:
    if report.guard_divergence_count != len(report.guard_divergences):
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "guard-divergence report count is inconsistent",
        )
    by_exit: dict[int, IU4ShadowGuardDivergenceV1] = {}
    for divergence in report.guard_divergences:
        exit_index = divergence.suppressed_exit_step_index
        if (
            divergence.schema_version != 1
            or divergence.position_side not in ("LONG", "SHORT")
            or divergence.first_rejected_step_index < 1
            or divergence.first_rejected_step_index
            > divergence.last_rejected_step_index
            or divergence.last_rejected_step_index >= exit_index
            or exit_index > report.step_count
            or divergence.rejected_entry_count < 1
            or not divergence.guard_reason_codes
            or len(set(divergence.guard_reason_codes))
            != len(divergence.guard_reason_codes)
            or exit_index in by_exit
        ):
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                "guard-divergence indices or identity are invalid",
            )
        exit_step = replay.steps[exit_index - 1]
        exit_outcome = report.outcomes[exit_index - 1]
        expected_open_action = (
            "OPEN_LONG" if divergence.position_side == "LONG" else "OPEN_SHORT"
        )
        expected_close_action = (
            "CLOSE_LONG" if divergence.position_side == "LONG" else "CLOSE_SHORT"
        )
        if (
            exit_step.source_event_kind != "AUTONOMOUS_EXIT_EXECUTION"
            or exit_step.source_execution_action != expected_close_action
            or exit_step.source_intent_id
            != divergence.suppressed_exit_source_intent_id
            or exit_step.source_execution_sequence
            != divergence.suppressed_exit_sequence
            or divergence.suppressed_exit_action != expected_close_action
            or exit_outcome.status != "NOOP"
            or exit_outcome.action != "NOOP"
            or exit_outcome.reason_code != GUARD_DIVERGENCE_EXIT_SUPPRESSED
            or exit_outcome.state.state_fingerprint
            != divergence.sandbox_state_fingerprint
        ):
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                "guard-divergence autonomous exit binding is invalid",
            )
        bound_rejections = []
        for index in range(
            divergence.first_rejected_step_index,
            divergence.last_rejected_step_index + 1,
        ):
            step = replay.steps[index - 1]
            outcome = report.outcomes[index - 1]
            if (
                step.source_event_kind == "INTENT"
                and outcome.status == "REJECTED"
                and outcome.action == expected_open_action
                and outcome.reason_code in divergence.guard_reason_codes
                and outcome.state.state_fingerprint
                == divergence.sandbox_state_fingerprint
            ):
                bound_rejections.append((index, step.source_intent_id))
        if (
            len(bound_rejections) != divergence.rejected_entry_count
            or bound_rejections[0]
            != (
                divergence.first_rejected_step_index,
                divergence.first_rejected_source_intent_id,
            )
            or bound_rejections[-1]
            != (
                divergence.last_rejected_step_index,
                divergence.last_rejected_source_intent_id,
            )
        ):
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                "guard-divergence rejected-entry binding is invalid",
            )
        by_exit[exit_index] = divergence
    return by_exit


def _evidence_components(
    *,
    replay: IU4ReplayInputV1,
    report: IU4ShadowDryRunReportV1,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[int, IU4ShadowGuardDivergenceV1],
]:
    if report.continuation_blocked:
        if (
            not report.restart_fault_detected
            or report.step_count != report.restart_after_step
            or report.step_count >= len(replay.steps)
            or len(report.outcomes) != report.step_count
        ):
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.INPUT_INVALID,
                "blocked fault-injection report has inconsistent replay counts",
            )
    elif len(report.outcomes) != len(replay.steps):
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "completed replay report must contain one outcome per input step",
        )
    guard_divergences = _validated_guard_divergences(
        replay=replay,
        report=report,
    )
    autonomous_pairs = (
        (index, step, outcome)
        for index, (step, outcome) in enumerate(
            zip(replay.steps, report.outcomes),
            start=1,
        )
        if step.source_event_kind == "AUTONOMOUS_EXIT_EXECUTION"
    )
    autonomous_step_count = 0
    autonomous_committed_count = 0
    autonomous_guard_suppressed_count = 0
    for index, step, outcome in autonomous_pairs:
        autonomous_step_count += 1
        autonomous_committed_count += (
            outcome.status == "COMMITTED"
            and outcome.action == step.source_execution_action
        )
        autonomous_guard_suppressed_count += index in guard_divergences
    autonomous_accounted_count = (
        autonomous_committed_count + autonomous_guard_suppressed_count
    )
    if autonomous_accounted_count != autonomous_step_count:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "every processed autonomous exit must commit or carry guard-divergence evidence",
        )
    input_record = {
        "logical_name": replay.path.name,
        "sha256": replay.sha256,
        "size_bytes": replay.size_bytes,
        "line_count": replay.line_count,
    }
    validation = {
        "source_manifest_fingerprint": report.source_manifest_fingerprint,
        "source_initial_state_fingerprint": report.source_initial_state_fingerprint,
        "source_final_state_fingerprint": report.source_final_state_fingerprint,
        "sandbox_final_state_fingerprint": report.sandbox_final_state_fingerprint,
        "source_initial_transaction_sequence": (
            report.source_initial_transaction_sequence
        ),
        "sandbox_final_transaction_sequence": (
            report.sandbox_final_transaction_sequence
        ),
        "simulated_transaction_count": report.simulated_transaction_count,
        "step_count": report.step_count,
        "requested_step_count": report.requested_step_count,
        "committed_step_count": report.committed_step_count,
        "noop_step_count": report.noop_step_count,
        "rejected_step_count": report.rejected_step_count,
        "autonomous_exit_step_count": autonomous_step_count,
        "autonomous_exit_committed_count": autonomous_committed_count,
        "autonomous_exit_guard_suppressed_count": (
            autonomous_guard_suppressed_count
        ),
        "autonomous_exit_accounted_count": autonomous_accounted_count,
        "guard_divergence_count": len(guard_divergences),
        "guard_divergence_rejected_entry_count": sum(
            divergence.rejected_entry_count
            for divergence in guard_divergences.values()
        ),
        "restart_enabled": report.restart_enabled,
        "restart_after_step": report.restart_after_step,
        "restart_count": report.restart_count,
        "restart_position": report.restart_position,
        "restart_state_fingerprint": report.restart_state_fingerprint,
        "restart_transaction_sequence": report.restart_transaction_sequence,
        "restart_state_restored": report.restart_state_restored,
        "restart_fault_injection": report.restart_fault_injection,
        "restart_fault_detected": report.restart_fault_detected,
        "restart_fault_reason_codes": list(report.restart_fault_reason_codes),
        "restart_fault_snapshot_sha256_before": (
            report.restart_fault_snapshot_sha256_before
        ),
        "restart_fault_snapshot_sha256_after": (
            report.restart_fault_snapshot_sha256_after
        ),
        "continuation_blocked": report.continuation_blocked,
        "source_unchanged": report.source_unchanged,
        "sandbox_consistent": report.sandbox_consistent,
    }
    return input_record, validation, guard_divergences


def _evidence_record(
    *,
    replay: IU4ReplayInputV1,
    report: IU4ShadowDryRunReportV1,
    replay_id: str,
    generated_at_utc: str,
) -> dict[str, Any]:
    input_record, validation, guard_divergences = _evidence_components(
        replay=replay,
        report=report,
    )
    base = {
        "artifact_type": "PEE_IU4_SHADOW_REPLAY_EVIDENCE",
        "schema_version": 2,
        "replay_id": replay_id,
        "generated_at_utc": generated_at_utc,
        "input": input_record,
        "validation": validation,
        "outcomes": [
            _outcome_record(
                index,
                outcome,
                replay.steps[index - 1],
                guard_divergences.get(index),
            )
            for index, outcome in enumerate(report.outcomes, start=1)
        ],
    }
    return {**base, "evidence_fingerprint": _sha256(_canonical_json(base))}


def _stream_evidence(
    *,
    output: Path,
    replay: IU4ReplayInputV1,
    report: IU4ShadowDryRunReportV1,
    replay_id: str,
    generated_at_utc: str,
) -> tuple[dict[str, Any], str, bool, bool]:
    input_record, validation, guard_divergences = _evidence_components(
        replay=replay,
        report=report,
    )
    artifact_type = "PEE_IU4_SHADOW_REPLAY_EVIDENCE"
    base_prefix = (
        b'{"artifact_type":'
        + _canonical_json(artifact_type)
        + b',"generated_at_utc":'
        + _canonical_json(generated_at_utc)
        + b',"input":'
        + _canonical_json(input_record)
        + b',"outcomes":['
    )
    base_suffix = (
        b'],"replay_id":'
        + _canonical_json(replay_id)
        + b',"schema_version":2,"validation":'
        + _canonical_json(validation)
        + b'}'
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent)
    )
    temporary = Path(temporary_name)
    fingerprint_hash = hashlib.sha256()
    fingerprint_hash.update(base_prefix)
    placeholder = b"0" * 64
    final_prefix_before_hash = (
        b'{"artifact_type":'
        + _canonical_json(artifact_type)
        + b',"evidence_fingerprint":"'
    )
    final_prefix_after_hash = (
        b'","generated_at_utc":'
        + _canonical_json(generated_at_utc)
        + b',"input":'
        + _canonical_json(input_record)
        + b',"outcomes":['
    )
    try:
        with os.fdopen(descriptor, "w+b") as handle:
            handle.write(final_prefix_before_hash)
            fingerprint_offset = handle.tell()
            handle.write(placeholder)
            handle.write(final_prefix_after_hash)
            for index, outcome in enumerate(report.outcomes, start=1):
                if index > 1:
                    handle.write(b",")
                    fingerprint_hash.update(b",")
                payload = _canonical_json(
                    _outcome_record(
                        index,
                        outcome,
                        replay.steps[index - 1],
                        guard_divergences.get(index),
                    )
                )
                handle.write(payload)
                fingerprint_hash.update(payload)
            handle.write(base_suffix + b"\n")
            fingerprint_hash.update(base_suffix)
            evidence_fingerprint = fingerprint_hash.hexdigest()
            handle.seek(fingerprint_offset)
            handle.write(evidence_fingerprint.encode("ascii"))
            handle.flush()
            os.fsync(handle.fileno())
        output_hash = hashlib.sha256()
        with temporary.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                output_hash.update(block)
        try:
            os.link(temporary, output)
            newly_written, already_exists = True, False
        except FileExistsError as exc:
            existing_hash = hashlib.sha256()
            with output.open("rb") as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    existing_hash.update(block)
            if existing_hash.hexdigest() != output_hash.hexdigest():
                raise IU4ReplayEvidenceError(
                    IU4ReplayEvidenceReasonCode.OUTPUT_CONFLICT,
                    "existing immutable artifact differs; overwrite is forbidden",
                ) from exc
            newly_written, already_exists = False, True
        directory_descriptor = os.open(output.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
        summary = {
            "artifact_type": artifact_type,
            "schema_version": 2,
            "replay_id": replay_id,
            "generated_at_utc": generated_at_utc,
            "input": input_record,
            "validation": validation,
            "evidence_fingerprint": evidence_fingerprint,
        }
        return summary, output_hash.hexdigest(), newly_written, already_exists
    except IU4ReplayEvidenceError:
        raise
    except OSError as exc:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.WRITE_FAILED,
            f"streaming evidence publish failed: {exc}",
        ) from exc
    finally:
        temporary.unlink(missing_ok=True)


def _validate_output_path(
    output_path: str | Path,
    *,
    input_path: Path,
    source_root: Path,
) -> Path:
    output = Path(output_path)
    if output.is_symlink() or (output.exists() and not output.is_file()):
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_INVALID,
            "evidence output must be a regular, non-symlink file",
        )
    parent = output.parent
    if not parent.is_dir() or parent.is_symlink():
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_INVALID,
            "evidence output directory must already exist and not be a symlink",
        )
    resolved = output.resolve()
    if resolved == input_path:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_INVALID,
            "replay input and evidence output must differ",
        )
    resolved_source = source_root.resolve()
    if resolved == resolved_source or resolved_source in resolved.parents:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_INVALID,
            "evidence output must not be inside the source coordinator root",
        )
    return resolved


def _publish_no_clobber(output: Path, payload: bytes) -> tuple[bool, bool]:
    if output.exists():
        if output.read_bytes() == payload:
            return False, True
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_CONFLICT,
            "existing immutable artifact differs; overwrite is forbidden",
        )

    descriptor, temporary_text = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp",
        dir=output.parent,
    )
    temporary = Path(temporary_text)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, output)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            if output.is_file() and not output.is_symlink() and output.read_bytes() == payload:
                return False, True
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.OUTPUT_CONFLICT,
                "concurrent immutable artifact differs; overwrite is forbidden",
            ) from exc
        directory_descriptor = os.open(output.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
        return True, False
    except IU4ReplayEvidenceError:
        raise
    except OSError as exc:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.WRITE_FAILED,
            f"atomic evidence publish failed: {exc}",
        ) from exc
    finally:
        temporary.unlink(missing_ok=True)


def publish_immutable_bytes(
    *,
    output_path: str | Path,
    payload: bytes,
) -> tuple[bool, bool]:
    if not isinstance(payload, bytes) or not payload:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_INVALID,
            "immutable artifact payload must be non-empty bytes",
        )
    output = Path(output_path)
    if output.is_symlink() or (output.exists() and not output.is_file()):
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_INVALID,
            "immutable artifact output must be a regular, non-symlink file",
        )
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_INVALID,
            "immutable artifact directory must exist and not be a symlink",
        )
    return _publish_no_clobber(output.resolve(), payload)


def write_iu4_replay_jsonl(
    *,
    steps: tuple[IU4ShadowIntentStepV1, ...],
    output_path: str | Path,
) -> IU4ReplayJsonlExportV1:
    if not isinstance(steps, tuple) or not steps:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "replay output requires a non-empty tuple of steps",
        )
    if not all(isinstance(step, IU4ShadowIntentStepV1) for step in steps):
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "replay output requires IU4ShadowIntentStepV1 values",
        )
    seen_ids: set[str] = set()
    previous_timestamp = ""
    previous_tick = -1
    for step in steps:
        if step.source_intent_id in seen_ids:
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.ORDER_INVALID,
                "replay output source_intent_id values must be unique",
            )
        if previous_timestamp and step.timestamp_utc <= previous_timestamp:
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.ORDER_INVALID,
                "replay output timestamps must be strictly increasing",
            )
        if step.tick_id <= previous_tick:
            raise IU4ReplayEvidenceError(
                IU4ReplayEvidenceReasonCode.ORDER_INVALID,
                "replay output tick_id values must be strictly increasing",
            )
        seen_ids.add(step.source_intent_id)
        previous_timestamp = step.timestamp_utc
        previous_tick = step.tick_id
    output = Path(output_path)
    payload = b"".join(_canonical_json(step.to_record()) + b"\n" for step in steps)
    newly_written, already_exists = publish_immutable_bytes(
        output_path=output,
        payload=payload,
    )
    output = output.resolve()
    loaded = load_iu4_replay_jsonl(output)
    if loaded.steps != steps:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.OUTPUT_CONFLICT,
            "published replay does not equal the requested canonical steps",
        )
    return IU4ReplayJsonlExportV1(
        output_path=output,
        output_sha256=_sha256(payload),
        size_bytes=len(payload),
        line_count=len(steps),
        newly_written=newly_written,
        already_exists=already_exists,
    )


def export_iu4_replay_evidence(
    *,
    input_path: str | Path,
    output_path: str | Path,
    harness: PaperIU4ShadowDryRunHarness,
    replay_id: str,
    generated_at_utc: str,
    restart_after_steps: int | None = None,
    restart_fault_injection: str | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    progress_interval_steps: int = 10_000,
    stream_output: bool = False,
) -> IU4ReplayEvidenceExportV1:
    if not isinstance(harness, PaperIU4ShadowDryRunHarness):
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "harness must be PaperIU4ShadowDryRunHarness",
        )
    if not isinstance(replay_id, str) or not replay_id.strip():
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "replay_id must be a non-empty string",
        )
    replay_id = replay_id.strip()
    try:
        generated = canonical_utc_timestamp(generated_at_utc, "generated_at_utc")
    except Exception as exc:
        raise IU4ReplayEvidenceError(
            IU4ReplayEvidenceReasonCode.INPUT_INVALID,
            "generated_at_utc must be canonical UTC whole seconds",
        ) from exc

    replay = load_iu4_replay_jsonl(input_path)
    output = _validate_output_path(
        output_path,
        input_path=replay.path,
        source_root=harness.source_coordinator.root_directory,
    )
    report = harness.run(
        replay.steps,
        restart_after_steps=restart_after_steps,
        restart_fault_injection=restart_fault_injection,
        progress_callback=progress_callback,
        progress_interval_steps=progress_interval_steps,
    )
    if stream_output:
        evidence, output_sha256, newly_written, already_exists = _stream_evidence(
            output=output,
            replay=replay,
            report=report,
            replay_id=replay_id,
            generated_at_utc=generated,
        )
    else:
        evidence = _evidence_record(
            replay=replay,
            report=report,
            replay_id=replay_id,
            generated_at_utc=generated,
        )
        payload = _canonical_json(evidence) + b"\n"
        newly_written, already_exists = _publish_no_clobber(output, payload)
        output_sha256 = _sha256(payload)
    return IU4ReplayEvidenceExportV1(
        output_path=output,
        evidence=evidence,
        output_sha256=output_sha256,
        newly_written=newly_written,
        already_exists=already_exists,
    )


__all__ = [
    "IU4ReplayEvidenceError",
    "IU4ReplayEvidenceExportV1",
    "IU4ReplayEvidenceReasonCode",
    "IU4ReplayInputV1",
    "IU4ReplayJsonlExportV1",
    "export_iu4_replay_evidence",
    "load_iu4_replay_jsonl",
    "publish_immutable_bytes",
    "write_iu4_replay_jsonl",
]
