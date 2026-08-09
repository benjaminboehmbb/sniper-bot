#!/usr/bin/env python3
"""End-to-end local smoke pipeline for isolated IU-4 SHADOW replay."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from live_l1.core.paper_entry_throttle import canonical_utc_timestamp
from live_l1.core.paper_iu4_shadow_harness import PaperIU4ShadowDryRunHarness
from live_l1.core.paper_iu4_startup_gate import IU4StartupGateDecisionV1
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator
from live_l1.tools.paper_iu4_replay_evidence import (
    IU4ReplayEvidenceExportV1,
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
    source_bytes = source.read_bytes()
    source_hash = _sha256(source_bytes)
    atomic_before, atomic_manifest_before = _coordinator_manifest(source_coordinator)
    state_before = source_coordinator.load_state()

    input_build = build_iu4_replay_input_from_l1_log(
        source_path=source,
        output_path=replay_output,
        manifest_path=replay_manifest,
        reference_stop_rate=reference_stop_rate,
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
    )

    input_manifest_record = _json_object(replay_manifest)
    evidence_record = _json_object(replay_evidence)
    if not _verify_record_fingerprint(
        input_manifest_record,
        field_name="manifest_fingerprint",
    ):
        raise IU4ReplayPipelineError(
            IU4ReplayPipelineReasonCode.CHAIN_INVALID,
            "replay input manifest fingerprint is invalid",
        )
    if not _verify_record_fingerprint(
        evidence_record,
        field_name="evidence_fingerprint",
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
    replay_bytes = replay_output.read_bytes()
    replay_hash = _sha256(replay_bytes)
    input_manifest_bytes = replay_manifest.read_bytes()
    input_manifest_hash = _sha256(input_manifest_bytes)
    evidence_bytes = replay_evidence.read_bytes()
    evidence_hash = _sha256(evidence_bytes)
    chain_checks = {
        "source_log_unchanged": source.read_bytes() == source_bytes,
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
        "sandbox_consistent": validation.get("sandbox_consistent") is True,
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
            "size_bytes": len(source_bytes),
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
                "size_bytes": len(replay_bytes),
            },
            "input_manifest": {
                "logical_name": replay_manifest.name,
                "sha256": input_manifest_hash,
                "size_bytes": len(input_manifest_bytes),
            },
            "evidence": {
                "logical_name": replay_evidence.name,
                "sha256": evidence_hash,
                "size_bytes": len(evidence_bytes),
            },
        },
        "result": {
            "step_count": validation.get("step_count"),
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
