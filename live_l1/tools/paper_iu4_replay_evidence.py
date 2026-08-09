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
from typing import Any, Mapping

from live_l1.core.paper_entry_throttle import canonical_utc_timestamp
from live_l1.core.paper_iu4_adapter import IU4AdapterResultV1
from live_l1.core.paper_iu4_shadow_harness import (
    IU4ShadowDryRunReportV1,
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


def _outcome_record(index: int, outcome: IU4AdapterResultV1) -> dict[str, Any]:
    state = outcome.state
    position = state.position
    return {
        "index": index,
        "source_intent_id": outcome.source_intent_id,
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
    }


def _evidence_record(
    *,
    replay: IU4ReplayInputV1,
    report: IU4ShadowDryRunReportV1,
    replay_id: str,
    generated_at_utc: str,
) -> dict[str, Any]:
    base = {
        "artifact_type": "PEE_IU4_SHADOW_REPLAY_EVIDENCE",
        "schema_version": 1,
        "replay_id": replay_id,
        "generated_at_utc": generated_at_utc,
        "input": {
            "logical_name": replay.path.name,
            "sha256": replay.sha256,
            "size_bytes": replay.size_bytes,
            "line_count": replay.line_count,
        },
        "validation": {
            "source_manifest_fingerprint": report.source_manifest_fingerprint,
            "source_initial_state_fingerprint": report.source_initial_state_fingerprint,
            "source_final_state_fingerprint": report.source_final_state_fingerprint,
            "sandbox_final_state_fingerprint": report.sandbox_final_state_fingerprint,
            "source_initial_transaction_sequence": report.source_initial_transaction_sequence,
            "sandbox_final_transaction_sequence": report.sandbox_final_transaction_sequence,
            "simulated_transaction_count": report.simulated_transaction_count,
            "step_count": report.step_count,
            "committed_step_count": report.committed_step_count,
            "noop_step_count": report.noop_step_count,
            "rejected_step_count": report.rejected_step_count,
            "source_unchanged": report.source_unchanged,
            "sandbox_consistent": report.sandbox_consistent,
        },
        "outcomes": [
            _outcome_record(index, outcome)
            for index, outcome in enumerate(report.outcomes, start=1)
        ],
    }
    return {**base, "evidence_fingerprint": _sha256(_canonical_json(base))}


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
            "existing evidence differs; overwrite is forbidden",
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
                "concurrent evidence differs; overwrite is forbidden",
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


def export_iu4_replay_evidence(
    *,
    input_path: str | Path,
    output_path: str | Path,
    harness: PaperIU4ShadowDryRunHarness,
    replay_id: str,
    generated_at_utc: str,
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
    report = harness.run(replay.steps)
    evidence = _evidence_record(
        replay=replay,
        report=report,
        replay_id=replay_id,
        generated_at_utc=generated,
    )
    payload = _canonical_json(evidence) + b"\n"
    newly_written, already_exists = _publish_no_clobber(output, payload)
    return IU4ReplayEvidenceExportV1(
        output_path=output,
        evidence=evidence,
        output_sha256=_sha256(payload),
        newly_written=newly_written,
        already_exists=already_exists,
    )


__all__ = [
    "IU4ReplayEvidenceError",
    "IU4ReplayEvidenceExportV1",
    "IU4ReplayEvidenceReasonCode",
    "IU4ReplayInputV1",
    "export_iu4_replay_evidence",
    "load_iu4_replay_jsonl",
]
