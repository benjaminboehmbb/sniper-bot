#!/usr/bin/env python3
"""End-to-end local smoke pipeline for isolated IU-4 SHADOW replay."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from live_l1.core.paper_entry_throttle import canonical_utc_timestamp
from live_l1.core.paper_iu4_shadow_harness import PaperIU4ShadowDryRunHarness
from live_l1.core.paper_iu4_startup_gate import IU4StartupGateDecisionV1
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator
from live_l1.tools.paper_iu4_replay_evidence import (
    IU4ReplayEvidenceExportV1,
    IU4ReplayJsonlExportV1,
    export_iu4_replay_evidence,
    publish_immutable_bytes,
)
from live_l1.tools.paper_iu4_replay_input import (
    IU4ReplayInputBuildV1,
    build_iu4_replay_input_from_l1_log,
)


class IU4ReplayPipelineReasonCode:
    INPUT_INVALID = "PEE_IU4_REPLAY_PIPELINE_INPUT_INVALID"
    OUTPUT_INVALID = "PEE_IU4_REPLAY_PIPELINE_OUTPUT_INVALID"
    CHAIN_INVALID = "PEE_IU4_REPLAY_PIPELINE_CHAIN_INVALID"
    SOURCE_CHANGED = "PEE_IU4_REPLAY_PIPELINE_SOURCE_CHANGED"


class IU4ReplayPipelineError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


@dataclass(frozen=True)
class IU4ReplayPipelineSmokeV1:
    source_log_path: Path
    input_build: IU4ReplayInputBuildV1
    evidence_export: IU4ReplayEvidenceExportV1
    receipt_path: Path
    receipt_sha256: str
    receipt_newly_written: bool
    receipt_already_exists: bool


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _existing_input_build(
    *,
    source: Path,
    replay_output: Path,
    replay_manifest: Path,
    reference_stop_rate: str,
) -> IU4ReplayInputBuildV1:
    if not replay_output.is_file() or not replay_manifest.is_file():
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.INPUT_INVALID,
            "resume requires existing replay input and manifest",
        )
    record = _json_object(replay_manifest)
    if not _verify_record_fingerprint(record, field_name="manifest_fingerprint"):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            "replay input manifest fingerprint is invalid",
        )
    source_record = record.get("source")
    replay_record = record.get("replay")
    builder_record = record.get("builder")
    if not all(
        isinstance(value, Mapping)
        for value in (source_record, replay_record, builder_record)
    ):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            "replay input manifest misses required objects",
        )
    source_size = source.stat().st_size
    replay_size = replay_output.stat().st_size
    source_hash = _sha256_file(source)
    replay_hash = _sha256_file(replay_output)
    with replay_output.open("rb") as handle:
        line_count = sum(1 for _ in handle)
    checks = (
        record.get("artifact_type") == "PEE_IU4_REPLAY_INPUT_MANIFEST",
        record.get("schema_version") == 2,
        source_record.get("logical_name") == source.name,
        source_record.get("sha256") == source_hash,
        source_record.get("size_bytes") == source_size,
        replay_record.get("logical_name") == replay_output.name,
        replay_record.get("sha256") == replay_hash,
        replay_record.get("size_bytes") == replay_size,
        replay_record.get("line_count") == line_count,
        builder_record.get("reference_stop_rate") == reference_stop_rate,
    )
    statistic_names = (
        "source_non_empty_lines",
        "parsed_event_count",
        "market_event_count",
        "intent_event_count",
        "execution_event_count",
        "executed_exit_event_count",
        "autonomous_exit_event_count",
    )
    statistics = {name: source_record.get(name) for name in statistic_names}
    if not all(checks) or any(
        isinstance(value, bool) or not isinstance(value, int) or value < 0
        for value in statistics.values()
    ):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            "existing replay input does not match its immutable manifest",
        )
    manifest_payload = replay_manifest.read_bytes()
    replay = IU4ReplayJsonlExportV1(
        output_path=replay_output,
        output_sha256=replay_hash,
        size_bytes=replay_size,
        line_count=line_count,
        newly_written=False,
        already_exists=True,
    )
    return IU4ReplayInputBuildV1(
        source_path=source,
        source_sha256=source_hash,
        source_size_bytes=source_size,
        replay=replay,
        manifest_path=replay_manifest,
        manifest_sha256=_sha256(manifest_payload),
        manifest_newly_written=False,
        manifest_already_exists=True,
        **statistics,
    )


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            f"invalid JSON artifact {path.name}",
        ) from exc
    if not isinstance(value, dict):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            f"JSON artifact {path.name} must contain an object",
        )
    return value


def _verify_record_fingerprint(
    record: Mapping[str, Any],
    *,
    field_name: str,
) -> bool:
    fingerprint = record.get(field_name)
    if not isinstance(fingerprint, str):
        return False
    base = {key: value for key, value in record.items() if key != field_name}
    return _sha256(_canonical_json(base)) == fingerprint


def _coordinator_manifest(
    coordinator: PaperAtomicCoordinator,
) -> tuple[dict[str, dict[str, int | str]], str]:
    root = coordinator.root_directory.resolve()
    paths = [coordinator.state_path]
    if coordinator.transaction_directory.exists():
        paths.extend(sorted(coordinator.transaction_directory.glob("*.json")))
    entries: dict[str, dict[str, int | str]] = {}
    for path in paths:
        if not path.is_file() or path.is_symlink():
            raise IU4ReplayPipelineError(
                IU4ReplayPipelineReasonCode.INPUT_INVALID,
                "atomic source contains a non-regular state path",
            )
        payload = path.read_bytes()
        entries[path.resolve().relative_to(root).as_posix()] = {
            "size_bytes": len(payload),
            "sha256": _sha256(payload),
        }
    return entries, _sha256(_canonical_json(entries))


def _validate_paths(
    *,
    source_log_path: str | Path,
    output_paths: tuple[str | Path, ...],
    source_root: Path,
) -> tuple[Path, tuple[Path, ...]]:
    source = Path(source_log_path)
    if not source.is_file() or source.is_symlink():
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.INPUT_INVALID,
            "source L1 log must be a regular, non-symlink file",
        )
    candidates = tuple(Path(path) for path in output_paths)
    if any(path.is_symlink() for path in candidates):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.OUTPUT_INVALID,
            "pipeline outputs must not be symlinks",
        )
    source = source.resolve()
    outputs = tuple(path.resolve() for path in candidates)
    if len({source, *outputs}) != len(outputs) + 1:
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.OUTPUT_INVALID,
            "source and all pipeline output paths must differ",
        )
    resolved_root = source_root.resolve()
    for output in outputs:
        if output == resolved_root or resolved_root in output.parents:
            raise IU4ReplayPipelineError(
                IU4ReplayPipelineReasonCode.OUTPUT_INVALID,
                "pipeline outputs must be outside the atomic source root",
            )
    return source, outputs


def run_iu4_replay_pipeline_smoke(
    *,
    source_log_path: str | Path,
    replay_output_path: str | Path,
    replay_manifest_path: str | Path,
    replay_evidence_path: str | Path,
    pipeline_receipt_path: str | Path,
    source_coordinator: PaperAtomicCoordinator,
    shadow_gate_decision: IU4StartupGateDecisionV1,
    reference_stop_rate: str,
    replay_id: str,
    generated_at_utc: str,
    restart_after_steps: int | None = None,
    restart_fault_injection: str | None = None,
    reuse_existing_replay_input: bool = False,
    progress_callback: Callable[[int, int], None] | None = None,
    progress_interval_steps: int = 10_000,
    stream_evidence_output: bool = False,
) -> IU4ReplayPipelineSmokeV1:
    if not isinstance(source_coordinator, PaperAtomicCoordinator):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.INPUT_INVALID,
            "source_coordinator must be PaperAtomicCoordinator",
        )
    if not isinstance(shadow_gate_decision, IU4StartupGateDecisionV1):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.INPUT_INVALID,
            "shadow_gate_decision must be IU4StartupGateDecisionV1",
        )
    source, outputs = _validate_paths(
        source_log_path=source_log_path,
        output_paths=(
            replay_output_path,
            replay_manifest_path,
            replay_evidence_path,
            pipeline_receipt_path,
        ),
        source_root=source_coordinator.root_directory,
    )
    replay_output, replay_manifest, replay_evidence, pipeline_receipt = outputs
    source_hash = _sha256_file(source)
    source_size = source.stat().st_size
    atomic_before, atomic_manifest_before = _coordinator_manifest(source_coordinator)
    state_before = source_coordinator.load_state()

    input_build = (
        _existing_input_build(
            source=source,
            replay_output=replay_output,
            replay_manifest=replay_manifest,
            reference_stop_rate=reference_stop_rate,
        )
        if reuse_existing_replay_input
        else build_iu4_replay_input_from_l1_log(
            source_path=source,
            output_path=replay_output,
            manifest_path=replay_manifest,
            reference_stop_rate=reference_stop_rate,
        )
    )
    harness = PaperIU4ShadowDryRunHarness(
        source_coordinator,
        shadow_gate_decision,
    )
    evidence_export = export_iu4_replay_evidence(
        input_path=replay_output,
        output_path=replay_evidence,
        harness=harness,
        replay_id=replay_id,
        generated_at_utc=generated_at_utc,
        restart_after_steps=restart_after_steps,
        restart_fault_injection=restart_fault_injection,
        progress_callback=progress_callback,
        progress_interval_steps=progress_interval_steps,
        stream_output=stream_evidence_output,
    )

    input_manifest_record = _json_object(replay_manifest)
    evidence_record = (
        dict(evidence_export.evidence)
        if stream_evidence_output
        else _json_object(replay_evidence)
    )
    if not _verify_record_fingerprint(
        input_manifest_record,
        field_name="manifest_fingerprint",
    ):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            "replay input manifest fingerprint is invalid",
        )
    if not stream_evidence_output and not _verify_record_fingerprint(
        evidence_record, field_name="evidence_fingerprint"
    ):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            "replay evidence fingerprint is invalid",
        )

    manifest_source = input_manifest_record.get("source")
    manifest_replay = input_manifest_record.get("replay")
    evidence_input = evidence_record.get("input")
    validation = evidence_record.get("validation")
    if not all(
        isinstance(value, Mapping)
        for value in (manifest_source, manifest_replay, evidence_input, validation)
    ):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            "pipeline artifacts miss required chain objects",
        )
    replay_hash = _sha256_file(replay_output)
    replay_size = replay_output.stat().st_size
    input_manifest_bytes = replay_manifest.read_bytes()
    input_manifest_hash = _sha256(input_manifest_bytes)
    evidence_hash = _sha256_file(replay_evidence)
    evidence_size = replay_evidence.stat().st_size
    expected_restart_fault = restart_fault_injection is not None
    chain_checks = {
        "source_log_unchanged": (
            source.stat().st_size == source_size
            and _sha256_file(source) == source_hash
        ),
        "builder_source_hash": input_build.source_sha256 == source_hash,
        "source_to_input_manifest": manifest_source.get("sha256") == source_hash,
        "input_manifest_whole_file_hash": (
            input_build.manifest_sha256 == input_manifest_hash
        ),
        "input_manifest_to_replay": manifest_replay.get("sha256") == replay_hash,
        "builder_replay_whole_file_hash": (
            input_build.replay.output_sha256 == replay_hash
        ),
        "replay_to_evidence": evidence_input.get("sha256") == replay_hash,
        "evidence_whole_file_hash": evidence_export.output_sha256 == evidence_hash,
        "replay_identity": evidence_record.get("replay_id") == replay_id.strip(),
        "generation_timestamp": (
            evidence_record.get("generated_at_utc")
            == canonical_utc_timestamp(generated_at_utc, "generated_at_utc")
        ),
        "source_state_unchanged": validation.get("source_unchanged") is True,
        "sandbox_state_matches_expected_mode": (
            validation.get("sandbox_consistent") is (not expected_restart_fault)
        ),
        "restart_fault_expectation": (
            validation.get("restart_fault_injection")
            == ("" if restart_fault_injection is None else restart_fault_injection)
            and validation.get("restart_fault_detected") is expected_restart_fault
            and validation.get("continuation_blocked") is expected_restart_fault
        ),
        "processed_step_count_matches_mode": (
            validation.get("step_count")
            == (
                restart_after_steps
                if expected_restart_fault
                else validation.get("requested_step_count")
            )
        ),
        "source_state_fingerprint_stable": (
            validation.get("source_initial_state_fingerprint")
            == state_before.state_fingerprint
            == validation.get("source_final_state_fingerprint")
        ),
    }
    atomic_after, atomic_manifest_after = _coordinator_manifest(source_coordinator)
    chain_checks["atomic_source_bytes_unchanged"] = (
        atomic_after == atomic_before
        and atomic_manifest_after == atomic_manifest_before
        and source_coordinator.load_state() == state_before
    )
    failed = tuple(name for name, passed in chain_checks.items() if not passed)
    if failed:
        reason = (
            IU4ReplayPipelineReasonCode.SOURCE_CHANGED
            if "source_log_unchanged" in failed or "atomic_source_bytes_unchanged" in failed
            else IU4ReplayPipelineReasonCode.CHAIN_INVALID
        )
        raise IU4ReplayPipelineError(
            reason,
            "pipeline chain checks failed: " + ",".join(failed),
        )

    receipt_base = {
        "artifact_type": "PEE_IU4_REPLAY_PIPELINE_SMOKE_RECEIPT",
        "schema_version": 1,
        "replay_id": evidence_record.get("replay_id"),
        "generated_at_utc": evidence_record.get("generated_at_utc"),
        "source": {
            "logical_name": source.name,
            "sha256": source_hash,
            "size_bytes": source_size,
        },
        "atomic_source": {
            "coordinator_id": state_before.coordinator_id,
            "state_fingerprint": state_before.state_fingerprint,
            "transaction_sequence": state_before.transaction_sequence,
            "file_manifest_fingerprint": atomic_manifest_before,
        },
        "artifacts": {
            "replay": {
                "logical_name": replay_output.name,
                "sha256": replay_hash,
                "size_bytes": replay_size,
            },
            "input_manifest": {
                "logical_name": replay_manifest.name,
                "sha256": input_manifest_hash,
                "size_bytes": len(input_manifest_bytes),
            },
            "evidence": {
                "logical_name": replay_evidence.name,
                "sha256": evidence_hash,
                "size_bytes": evidence_size,
            },
        },
        "result": {
            "step_count": validation.get("step_count"),
            "requested_step_count": validation.get("requested_step_count"),
            "committed_step_count": validation.get("committed_step_count"),
            "noop_step_count": validation.get("noop_step_count"),
            "rejected_step_count": validation.get("rejected_step_count"),
            "autonomous_exit_step_count": validation.get(
                "autonomous_exit_step_count"
            ),
            "autonomous_exit_committed_count": validation.get(
                "autonomous_exit_committed_count"
            ),
            "restart_enabled": validation.get("restart_enabled"),
            "restart_after_step": validation.get("restart_after_step"),
            "restart_count": validation.get("restart_count"),
            "restart_position": validation.get("restart_position"),
            "restart_state_fingerprint": validation.get(
                "restart_state_fingerprint"
            ),
            "restart_transaction_sequence": validation.get(
                "restart_transaction_sequence"
            ),
            "restart_state_restored": validation.get("restart_state_restored"),
            "restart_fault_injection": validation.get(
                "restart_fault_injection"
            ),
            "restart_fault_detected": validation.get("restart_fault_detected"),
            "restart_fault_reason_codes": validation.get(
                "restart_fault_reason_codes"
            ),
            "restart_fault_snapshot_sha256_before": validation.get(
                "restart_fault_snapshot_sha256_before"
            ),
            "restart_fault_snapshot_sha256_after": validation.get(
                "restart_fault_snapshot_sha256_after"
            ),
            "continuation_blocked": validation.get("continuation_blocked"),
            "simulated_transaction_count": validation.get("simulated_transaction_count"),
            "sandbox_final_state_fingerprint": validation.get(
                "sandbox_final_state_fingerprint"
            ),
        },
        "chain_checks": chain_checks,
        "iu4_enforced_enabled": False,
        "exchange_enabled": False,
        "live_enabled": False,
    }
    receipt_record = {
        **receipt_base,
        "receipt_fingerprint": _sha256(_canonical_json(receipt_base)),
    }
    receipt_payload = _canonical_json(receipt_record) + b"\n"
    receipt_new, receipt_existing = publish_immutable_bytes(
        output_path=pipeline_receipt,
        payload=receipt_payload,
    )
    return IU4ReplayPipelineSmokeV1(
        source_log_path=source,
        input_build=input_build,
        evidence_export=evidence_export,
        receipt_path=pipeline_receipt,
        receipt_sha256=_sha256(receipt_payload),
        receipt_newly_written=receipt_new,
        receipt_already_exists=receipt_existing,
    )


__all__ = [
    "IU4ReplayPipelineError",
    "IU4ReplayPipelineReasonCode",
    "IU4ReplayPipelineSmokeV1",
    "run_iu4_replay_pipeline_smoke",
]
