#!/usr/bin/env python3
"""Run a bounded X1-only IU-4 SHADOW replay dataset with full evidence."""

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
) -> PaperAtomicCoordinator:
    identity = _sha256_bytes(source_id.encode("utf-8"))[:16]
    coordinator = PaperAtomicCoordinator(
        root,
        config,
        policy,
        coordinator_id=f"IU4-X1-REPLAY-BTCUSDT-{identity}",
        symbol="BTCUSDT",
    )
    coordinator.initialize(
        position=PositionStateS2FlatV2(
            schema_version=2,
            system_state_id=f"IU4-X1-INITIAL-{identity}",
            symbol="BTCUSDT",
            position="FLAT",
            side="",
            last_closed_trade_id="",
            economics_profile_id=config.economics_profile_id,
            economics_model_version=config.economics_model_version,
            config_fingerprint=config.config_fingerprint,
        ),
        account=PaperAccountState.initial(
            account_id=f"PAPER-IU4-X1-{identity}",
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
    restart_after_steps: int | None = None,
    restart_fault_injection: str | None = None,
) -> IU4X1DatasetRunV1:
    output_directory = output_directory.resolve()
    if output_directory.exists():
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.OUTPUT_INVALID,
            "output directory already exists",
        )
    if max_ticks < 1 or valid_row_offset < 0:
        raise IU4X1DatasetError(
            IU4X1DatasetReasonCode.INPUT_INVALID,
            "max_ticks must be positive and valid_row_offset non-negative",
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
    output_directory.mkdir(parents=True)
    iu3_directory = output_directory / "iu3_source"
    iu3_manifest = run_validation(
        source_csv=source_csv.resolve(),
        expected_source_sha256=expected_source_sha256,
        profile_json=economics_profile_json.resolve(),
        seed_csv=seed_csv.resolve(),
        output_directory=iu3_directory,
        max_ticks=max_ticks,
        valid_row_offset=valid_row_offset,
        source_id=source_id,
    )
    first_timestamp = str(
        iu3_manifest["normalized_market_slice"]["first_timestamp_utc"]
    )
    first_utc_day = first_timestamp[:10]
    atomic_directory = output_directory / "atomic_source"
    coordinator = _initial_atomic_coordinator(
        root=atomic_directory,
        source_id=source_id,
        first_utc_day=first_utc_day,
        config=config,
        policy=policy,
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
    iu4_directory.mkdir()
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
    )
    receipt_path = pipeline.receipt_path
    manifest_base = {
        "artifact_type": "PEE_IU4_X1_REPLAY_DATASET_RUN",
        "schema_version": 1,
        "git_commit": git_commit,
        "source_id": source_id,
        "replay_id": replay_id,
        "generated_at_utc": generated_at_utc,
        "x1_only": True,
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
    parser.add_argument("--restart-after-steps", type=int)
    parser.add_argument(
        "--restart-fault-injection",
        choices=(RESTART_FAULT_SNAPSHOT_TRUNCATED,),
    )
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
        restart_after_steps=args.restart_after_steps,
        restart_fault_injection=args.restart_fault_injection,
    )
    evidence = result.pipeline.evidence_export.evidence
    validation = evidence["validation"]
    print("IU4 X1 REPLAY DATASET: PASS")
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
    "run_x1_replay_dataset",
]
