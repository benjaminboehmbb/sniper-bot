#!/usr/bin/env python3
"""Run a bounded IU-4 SHADOW replay dataset with host-bound evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from live_l1.core.paper_economics import PaperEconomicsConfig
from live_l1.core.paper_entry_throttle import (
    PaperEntryThrottlePolicy,
    PaperEntryThrottleState,
)
from live_l1.core.paper_iu4_startup_gate import (
    IU4StartupModeRequestV1,
    MODE_SHADOW,
    evaluate_iu4_startup_gate,
)
from live_l1.core.paper_iu4_shadow_harness import (
    RESTART_FAULT_SNAPSHOT_TRUNCATED,
)
from live_l1.state.paper_artifacts import PaperAccountState, PositionStateS2FlatV2
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator
from live_l1.tools.paper_economics_shadow_sidecar import load_settings_json
from live_l1.tools.paper_iu4_replay_evidence import publish_immutable_bytes
from live_l1.tools.paper_iu4_replay_pipeline import (
    IU4ReplayPipelineSmokeV1,
    run_iu4_replay_pipeline_smoke,
)
from live_l1.tools.run_pee_shadow_validation import run_validation


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXECUTION_HOST_X1 = "X1"
EXECUTION_HOST_WORKSTATION = "WORKSTATION"
EXECUTION_HOSTS = (EXECUTION_HOST_X1, EXECUTION_HOST_WORKSTATION)


class IU4X1DatasetReasonCode:
    INPUT_INVALID = "PEE_IU4_X1_DATASET_INPUT_INVALID"
    POLICY_INVALID = "PEE_IU4_X1_DATASET_POLICY_INVALID"
    OUTPUT_INVALID = "PEE_IU4_X1_DATASET_OUTPUT_INVALID"


class IU4X1DatasetError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


@dataclass(frozen=True)
class IU4X1DatasetRunV1:
    output_directory: Path
    iu3_manifest: Mapping[str, Any]
    pipeline: IU4ReplayPipelineSmokeV1
    run_manifest_path: Path
    run_manifest_sha256: str


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            f"invalid JSON object: {path}",
        ) from exc
    if not isinstance(value, dict):
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            f"JSON root must be an object: {path}",
        )
    return value


def _git_head() -> str:
    result = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _load_calibration_policy(path: Path) -> PaperEntryThrottlePolicy:
    record = _json_object(path)
    expected = {
        "artifact_type",
        "schema_version",
        "calibration_only",
        "operationally_approved",
        "policy",
    }
    if set(record) != expected:
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.POLICY_INVALID,
            "calibration policy fields are missing or unknown",
        )
    policy_record = record.get("policy")
    if (
        record.get("artifact_type") != "pee_rate_calibration_policy"
        or record.get("schema_version") != 1
        or record.get("calibration_only") is not True
        or record.get("operationally_approved") is not False
        or not isinstance(policy_record, Mapping)
    ):
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.POLICY_INVALID,
            "policy must be calibration-only and operationally unapproved",
        )
    expected_policy_fields = set(PaperEntryThrottlePolicy.__dataclass_fields__)
    if set(policy_record) != expected_policy_fields:
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.POLICY_INVALID,
            "throttle policy fields are missing or unknown",
        )
    return PaperEntryThrottlePolicy.from_record(policy_record)


def _initial_atomic_coordinator(
    *,
    root: Path,
    source_id: str,
    first_utc_day: str,
    config: PaperEconomicsConfig,
    policy: PaperEntryThrottlePolicy,
    execution_host: str,
) -> PaperAtomicCoordinator:
    identity = _sha256_bytes(source_id.encode("utf-8"))[:16]
    coordinator = PaperAtomicCoordinator(
        root,
        config,
        policy,
        coordinator_id=f"IU4-{execution_host}-REPLAY-BTCUSDT-{identity}",
        symbol="BTCUSDT",
    )
    coordinator.initialize(
        position=PositionStateS2FlatV2(
            schema_version=2,
            system_state_id=f"IU4-{execution_host}-INITIAL-{identity}",
            symbol="BTCUSDT",
            position="FLAT",
            side="",
            last_closed_trade_id="",
            economics_profile_id=config.economics_profile_id,
            economics_model_version=config.economics_model_version,
            config_fingerprint=config.config_fingerprint,
        ),
        account=PaperAccountState.initial(
            account_id=f"PAPER-IU4-{execution_host}-{identity}",
            quote_currency=config.quote_currency,
            starting_equity_quote=config.starting_equity_quote,
            utc_day=first_utc_day,
            economics_profile_id=config.economics_profile_id,
            economics_model_version=config.economics_model_version,
            config_fingerprint=config.config_fingerprint,
        ),
        throttle=PaperEntryThrottleState.initial(policy, utc_day=first_utc_day),
    )
    return coordinator


def _resume_atomic_coordinator(
    *,
    root: Path,
    source_id: str,
    config: PaperEconomicsConfig,
    policy: PaperEntryThrottlePolicy,
    execution_host: str,
) -> PaperAtomicCoordinator:
    identity = _sha256_bytes(source_id.encode("utf-8"))[:16]
    coordinator = PaperAtomicCoordinator(
        root,
        config,
        policy,
        coordinator_id=f"IU4-{execution_host}-REPLAY-BTCUSDT-{identity}",
        symbol="BTCUSDT",
    )
    report = coordinator.reconciliation_report()
    state = coordinator.load_state()
    if not report.consistent or state.transaction_sequence != 0:
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "resume atomic source must be reconciled at transaction sequence zero",
        )
    return coordinator


def _load_resume_iu3_manifest(
    *,
    iu3_directory: Path,
    source_csv: Path,
    expected_source_sha256: str,
    economics_profile_json: Path,
    seed_csv: Path,
    max_ticks: int,
    valid_row_offset: int,
    source_id: str,
    git_commit: str,
) -> dict[str, Any]:
    manifest_path = iu3_directory / "run_manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "resume requires the existing IU3 manifest",
        )
    manifest = _json_object(manifest_path)
    source_record = manifest.get("source_csv")
    slice_record = manifest.get("normalized_market_slice")
    profile_record = manifest.get("profile")
    seed_record = manifest.get("seed_csv")
    runtime_record = manifest.get("runtime")
    sidecar_record = manifest.get("sidecar")
    output_hashes = manifest.get("output_hashes")
    if not all(
        isinstance(value, Mapping)
        for value in (
            source_record,
            slice_record,
            profile_record,
            seed_record,
            runtime_record,
            sidecar_record,
            output_hashes,
        )
    ):
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "resume IU3 manifest misses required objects",
        )
    checks = (
        manifest.get("artifact_type") == "pee_iu3_shadow_validation_manifest",
        manifest.get("source_id") == source_id,
        manifest.get("git_commit") == git_commit,
        source_record.get("sha256") == expected_source_sha256.lower(),
        _sha256_file(source_csv) == expected_source_sha256.lower(),
        profile_record.get("file_sha256") == _sha256_file(economics_profile_json),
        seed_record.get("sha256") == _sha256_file(seed_csv),
        runtime_record.get("return_code") == 0,
        runtime_record.get("max_ticks") == max_ticks,
        slice_record.get("valid_row_offset") == valid_row_offset,
        slice_record.get("rows_written") == max_ticks,
        sidecar_record.get("issues") == 0,
    )
    if not all(checks):
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "resume parameters do not match the completed IU3 evidence",
        )
    for relative_name, expected_hash in output_hashes.items():
        if not isinstance(relative_name, str) or not isinstance(expected_hash, str):
            raise IU4X1DatasetError(
                IU4X1DatasetReasonCode.OUTPUT_INVALID,
                "resume IU3 output hash manifest is invalid",
            )
        path = (iu3_directory / relative_name).resolve()
        iu3_root = iu3_directory.resolve()
        if iu3_root not in path.parents:
            raise IU4X1DatasetError(
                IU4X1DatasetReasonCode.OUTPUT_INVALID,
                "resume IU3 output path escapes its run directory",
            )
        if not path.is_file() or path.is_symlink() or _sha256_file(path) != expected_hash:
            raise IU4X1DatasetError(
                IU4X1DatasetReasonCode.OUTPUT_INVALID,
                f"resume IU3 artifact hash mismatch: {relative_name}",
            )
    return manifest


def _progress_callback(path: Path):
    if path.is_symlink():
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "progress path must not be a symlink",
        )

    def publish(completed: int, total: int) -> None:
        percentage = 100.0 if total == 0 else round(completed * 100 / total, 2)
        record = {
            "artifact_type": "PEE_IU4_REPLAY_OPERATIONAL_PROGRESS",
            "schema_version": 1,
            "completed_steps": completed,
            "total_steps": total,
            "percentage": percentage,
            "status": "COMPLETE" if completed == total else "RUNNING",
        }
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_bytes(_canonical_json(record) + b"\n")
        temporary.replace(path)

    return publish


def run_x1_replay_dataset(
    *,
    source_csv: Path,
    expected_source_sha256: str,
    economics_profile_json: Path,
    throttle_observation_policy_json: Path,
    seed_csv: Path,
    output_directory: Path,
    max_ticks: int,
    valid_row_offset: int,
    source_id: str,
    replay_id: str,
    generated_at_utc: str,
    execution_host: str = EXECUTION_HOST_X1,
    restart_after_steps: int | None = None,
    restart_fault_injection: str | None = None,
    resume_existing_output: bool = False,
    expected_iu3_git_commit: str | None = None,
    progress_interval_steps: int = 10_000,
) -> IU4X1DatasetRunV1:
    output_candidate = output_directory
    if resume_existing_output and output_candidate.is_symlink():
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "resume output must not be a symlink",
        )
    output_directory = output_candidate.resolve()
    if output_directory.exists() and not resume_existing_output:
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "output directory already exists",
        )
    if resume_existing_output and (
        not output_directory.is_dir() or output_directory.is_symlink()
    ):
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "resume output must be an existing non-symlink directory",
        )
    if max_ticks < 1 or valid_row_offset < 0:
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            "max_ticks must be positive and valid_row_offset non-negative",
        )
    if (
        isinstance(progress_interval_steps, bool)
        or not isinstance(progress_interval_steps, int)
        or progress_interval_steps < 1
    ):
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            "progress_interval_steps must be a positive integer",
        )
    if execution_host not in EXECUTION_HOSTS:
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            f"execution_host must be one of {EXECUTION_HOSTS}",
        )
    if resume_existing_output:
        if expected_iu3_git_commit is None:
            expected_iu3_git_commit = _git_head()
        if (
            len(expected_iu3_git_commit) != 40
            or any(
                character not in "0123456789abcdef"
                for character in expected_iu3_git_commit
            )
        ):
            raise IU4X1DatasetError(
                IU4X1DatasetReasonCode.INPUT_INVALID,
                "resume requires a lowercase 40-character expected IU3 git commit",
            )
    if restart_after_steps is not None and (
        isinstance(restart_after_steps, bool)
        or not isinstance(restart_after_steps, int)
        or restart_after_steps < 1
        or restart_after_steps >= max_ticks
    ):
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            "restart_after_steps must split the bounded replay into two non-empty segments",
        )
    if restart_fault_injection is not None and (
        restart_fault_injection != RESTART_FAULT_SNAPSHOT_TRUNCATED
        or restart_after_steps is None
    ):
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            "restart fault injection requires SNAPSHOT_TRUNCATED and a valid boundary",
        )
    for path in (
        source_csv,
        economics_profile_json,
        throttle_observation_policy_json,
        seed_csv,
    ):
        if not path.is_file() or path.is_symlink():
            raise IU4X1DatasetError(
                IU4X1DatasetReasonCode.INPUT_INVALID,
                f"input must be a regular, non-symlink file: {path}",
            )
    policy = _load_calibration_policy(throttle_observation_policy_json)
    settings = load_settings_json(economics_profile_json)
    if not settings.ready or settings.config is None or settings.reference_stop_rate is None:
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            "economics profile must be ready for SHADOW",
        )
    config = settings.config
    git_commit = _git_head()
    if not resume_existing_output:
        output_directory.mkdir(parents=True)
    iu3_directory = output_directory / "iu3_source"
    iu3_manifest = (
        _load_resume_iu3_manifest(
            iu3_directory=iu3_directory,
            source_csv=source_csv,
            expected_source_sha256=expected_source_sha256,
            economics_profile_json=economics_profile_json,
            seed_csv=seed_csv,
            max_ticks=max_ticks,
            valid_row_offset=valid_row_offset,
            source_id=source_id,
            git_commit=expected_iu3_git_commit,
        )
        if resume_existing_output
        else run_validation(
            source_csv=source_csv.resolve(),
            expected_source_sha256=expected_source_sha256,
            profile_json=economics_profile_json.resolve(),
            seed_csv=seed_csv.resolve(),
            output_directory=iu3_directory,
            max_ticks=max_ticks,
            valid_row_offset=valid_row_offset,
            source_id=source_id,
        )
    )
    first_timestamp = str(
        iu3_manifest["normalized_market_slice"]["first_timestamp_utc"]
    )
    first_utc_day = first_timestamp[:10]
    atomic_directory = output_directory / "atomic_source"
    coordinator = (
        _resume_atomic_coordinator(
            root=atomic_directory,
            source_id=source_id,
            config=config,
            policy=policy,
            execution_host=execution_host,
        )
        if resume_existing_output
        else _initial_atomic_coordinator(
            root=atomic_directory,
            source_id=source_id,
            first_utc_day=first_utc_day,
            config=config,
            policy=policy,
            execution_host=execution_host,
        )
    )
    state = coordinator.load_state()
    gate_request = IU4StartupModeRequestV1(
        schema_version=1,
        mode=MODE_SHADOW,
        startup_timestamp_utc=generated_at_utc,
        operational_profile="PAPER",
        startup_recovery_enabled=False,
        reconciliation_gate_enabled=True,
        repository_commit_sha=git_commit,
        expected_coordinator_id=coordinator.coordinator_id,
        expected_symbol=coordinator.symbol,
        expected_economics_profile_id=config.economics_profile_id,
        expected_economics_model_version=config.economics_model_version,
        expected_economics_config_fingerprint=config.config_fingerprint,
        expected_throttle_policy_profile_id=policy.policy_profile_id,
        expected_throttle_policy_model_version=policy.policy_model_version,
        expected_throttle_policy_fingerprint=policy.policy_fingerprint,
        authorization=None,
    )
    gate = evaluate_iu4_startup_gate(
        gate_request,
        coordinator,
        running_repository_commit_sha=git_commit,
    )
    iu4_directory = output_directory / "iu4_replay"
    if resume_existing_output:
        for completed_path in (
            iu4_directory / "replay_evidence.json",
            iu4_directory / "pipeline_receipt.json",
            output_directory / "run_manifest.json",
        ):
            if completed_path.exists() or completed_path.is_symlink():
                raise IU4X1DatasetError(
                    IU4X1DatasetReasonCode.OUTPUT_INVALID,
                    "resume refuses a run with completed or conflicting outputs",
                )
    else:
        iu4_directory.mkdir()
    progress_path = iu4_directory / "phase2_progress.json"
    pipeline = run_iu4_replay_pipeline_smoke(
        source_log_path=iu3_directory / "live_logs" / "l1.log",
        replay_output_path=iu4_directory / "replay.jsonl",
        replay_manifest_path=iu4_directory / "replay_input_manifest.json",
        replay_evidence_path=iu4_directory / "replay_evidence.json",
        pipeline_receipt_path=iu4_directory / "pipeline_receipt.json",
        source_coordinator=coordinator,
        shadow_gate_decision=gate,
        reference_stop_rate=str(settings.reference_stop_rate),
        replay_id=replay_id,
        generated_at_utc=generated_at_utc,
        restart_after_steps=restart_after_steps,
        restart_fault_injection=restart_fault_injection,
        reuse_existing_replay_input=resume_existing_output,
        progress_callback=_progress_callback(progress_path),
        progress_interval_steps=progress_interval_steps,
        stream_evidence_output=resume_existing_output,
    )
    receipt_path = pipeline.receipt_path
    manifest_base = {
        "artifact_type": f"PEE_IU4_{execution_host}_REPLAY_DATASET_RUN",
        "schema_version": 1,
        "git_commit": git_commit,
        "source_id": source_id,
        "replay_id": replay_id,
        "generated_at_utc": generated_at_utc,
        "execution_host": execution_host,
        "x1_only": execution_host == EXECUTION_HOST_X1,
        "workstation_only": execution_host == EXECUTION_HOST_WORKSTATION,
        "max_ticks": max_ticks,
        "valid_row_offset": valid_row_offset,
        "restart_after_steps": restart_after_steps,
        "restart_fault_injection": restart_fault_injection,
        "source_csv": {
            "logical_name": source_csv.name,
            "sha256": expected_source_sha256.lower(),
        },
        "economics_profile": {
            "logical_name": economics_profile_json.name,
            "file_sha256": _sha256_file(economics_profile_json),
            "profile_id": config.economics_profile_id,
            "config_fingerprint": config.config_fingerprint,
        },
        "throttle_observation_policy": {
            "logical_name": throttle_observation_policy_json.name,
            "file_sha256": _sha256_file(throttle_observation_policy_json),
            "profile_id": policy.policy_profile_id,
            "policy_fingerprint": policy.policy_fingerprint,
            "calibration_only": True,
            "operationally_approved": False,
        },
        "iu3_manifest": {
            "relative_path": "iu3_source/run_manifest.json",
            "sha256": _sha256_file(iu3_directory / "run_manifest.json"),
            "source_git_commit": iu3_manifest["git_commit"],
            "issues": iu3_manifest["sidecar"]["issues"],
        },
        "atomic_source": {
            "state_fingerprint": state.state_fingerprint,
            "transaction_sequence": state.transaction_sequence,
        },
        "iu4_pipeline_receipt": {
            "relative_path": "iu4_replay/pipeline_receipt.json",
            "sha256": pipeline.receipt_sha256,
        },
        "iu4_enforced_enabled": False,
        "exchange_enabled": False,
        "live_enabled": False,
    }
    run_manifest = {
        **manifest_base,
        "manifest_fingerprint": _sha256_bytes(_canonical_json(manifest_base)),
    }
    run_manifest_payload = _canonical_json(run_manifest) + b"\n"
    run_manifest_path = output_directory / "run_manifest.json"
    publish_immutable_bytes(
        output_path=run_manifest_path,
        payload=run_manifest_payload,
    )
    return IU4X1DatasetRunV1(
        output_directory=output_directory,
        iu3_manifest=iu3_manifest,
        pipeline=pipeline,
        run_manifest_path=run_manifest_path,
        run_manifest_sha256=_sha256_bytes(run_manifest_payload),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--economics-profile-json", required=True)
    parser.add_argument("--throttle-observation-policy-json", required=True)
    parser.add_argument("--seed-csv", required=True)
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--max-ticks", type=int, required=True)
    parser.add_argument("--valid-row-offset", type=int, default=0)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--replay-id", required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument(
        "--execution-host",
        choices=EXECUTION_HOSTS,
        default=EXECUTION_HOST_X1,
    )
    parser.add_argument("--restart-after-steps", type=int)
    parser.add_argument(
        "--restart-fault-injection",
        choices=(RESTART_FAULT_SNAPSHOT_TRUNCATED,),
    )
    parser.add_argument("--resume-existing-output", action="store_true")
    parser.add_argument("--expected-iu3-git-commit")
    parser.add_argument("--progress-interval-steps", type=int, default=10_000)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    result = run_x1_replay_dataset(
        source_csv=Path(args.source_csv),
        expected_source_sha256=args.expected_source_sha256,
        economics_profile_json=Path(args.economics_profile_json),
        throttle_observation_policy_json=Path(
            args.throttle_observation_policy_json
        ),
        seed_csv=Path(args.seed_csv),
        output_directory=Path(args.output_directory),
        max_ticks=args.max_ticks,
        valid_row_offset=args.valid_row_offset,
        source_id=args.source_id,
        replay_id=args.replay_id,
        generated_at_utc=args.generated_at_utc,
        execution_host=args.execution_host,
        restart_after_steps=args.restart_after_steps,
        restart_fault_injection=args.restart_fault_injection,
        resume_existing_output=args.resume_existing_output,
        expected_iu3_git_commit=args.expected_iu3_git_commit,
        progress_interval_steps=args.progress_interval_steps,
    )
    evidence = result.pipeline.evidence_export.evidence
    validation = evidence["validation"]
    print(f"IU4 {args.execution_host} REPLAY DATASET: PASS")
    print("max_ticks:", result.iu3_manifest["runtime"]["max_ticks"])
    print("committed:", validation["committed_step_count"])
    print("noop:", validation["noop_step_count"])
    print("rejected:", validation["rejected_step_count"])
    print("continuation_blocked:", validation["continuation_blocked"])
    print("run_manifest:", result.run_manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "IU4X1DatasetError",
    "IU4X1DatasetReasonCode",
    "IU4X1DatasetRunV1",
    "EXECUTION_HOST_WORKSTATION",
    "EXECUTION_HOST_X1",
    "run_x1_replay_dataset",
]
