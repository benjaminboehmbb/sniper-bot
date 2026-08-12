#!/usr/bin/env python3
"""Fail-closed active-startup bridge for IU-4 OFF or read-only SHADOW mode."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from live_l1.core.paper_economics_shadow import load_shadow_settings
from live_l1.core.paper_entry_throttle_profile import (
    ApprovedPaperEntryThrottleProfileV1,
    load_approved_paper_entry_throttle_profile,
)
from live_l1.core.paper_iu4_startup_gate import (
    IU4StartupGateDecisionV1,
    IU4StartupModeRequestV1,
    MODE_OFF,
    MODE_SHADOW,
    evaluate_iu4_startup_gate,
)
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator


ENV_MODE = "L1_IU4_MODE"
ENV_ATOMIC_STATE_DIRECTORY = "L1_IU4_ATOMIC_STATE_DIRECTORY"
ENV_APPROVED_THROTTLE_PROFILE = "L1_IU4_APPROVED_THROTTLE_PROFILE"
ENV_COORDINATOR_ID = "L1_IU4_COORDINATOR_ID"
ENV_SYMBOL = "L1_IU4_SYMBOL"
ENV_REPOSITORY_COMMIT = "L1_IU4_REPOSITORY_COMMIT"
DEFAULT_APPROVED_THROTTLE_PROFILE = (
    "config/pee/PEE_RATE_OBSERVED_BOUNDARY_001.json"
)
APPROVED_THROTTLE_APPROVAL_ID = (
    "IU4-THROTTLE-PROFIL-OBSERVED-BOUNDARY-2026-08-11"
)
APPROVED_THROTTLE_PROFILE_SHA256 = (
    "b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7"
)
APPROVED_THROTTLE_POLICY_PROFILE_ID = "PEE_RATE_OBSERVED_BOUNDARY_001"
APPROVED_THROTTLE_POLICY_FINGERPRINT = (
    "ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada"
)
APPROVED_ECONOMICS_PROFILE_ID = "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001"
APPROVED_ECONOMICS_MODEL_VERSION = "PEE_V1"
APPROVED_ECONOMICS_CONFIG_FINGERPRINT = (
    "ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1"
)


class IU4ShadowRuntimeGateReasonCode:
    READY = "PEE_IU4_SHADOW_RUNTIME_READY"
    MODE_INVALID = "PEE_IU4_SHADOW_RUNTIME_MODE_INVALID"
    PROFILE_REQUIRED = "PEE_IU4_SHADOW_RUNTIME_PROFILE_REQUIRED"
    ECONOMICS_INVALID = "PEE_IU4_SHADOW_RUNTIME_ECONOMICS_INVALID"
    COMMIT_INVALID = "PEE_IU4_SHADOW_RUNTIME_COMMIT_INVALID"
    COORDINATOR_INVALID = "PEE_IU4_SHADOW_RUNTIME_COORDINATOR_INVALID"
    GATE_DENIED = "PEE_IU4_SHADOW_RUNTIME_GATE_DENIED"


class IU4ShadowRuntimeGateError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


@dataclass(frozen=True)
class IU4ShadowRuntimeGateV1:
    mode: str
    decision: IU4StartupGateDecisionV1
    running_repository_commit_sha: str
    approved_profile: ApprovedPaperEntryThrottleProfileV1 | None
    coordinator: PaperAtomicCoordinator | None

    @property
    def shadow_enabled(self) -> bool:
        return self.mode == MODE_SHADOW and self.decision.shadow_observation_enabled

    def startup_log_fields(self) -> dict[str, object]:
        policy = None if self.approved_profile is None else self.approved_profile.policy
        return {
            "iu4_mode": self.mode,
            "iu4_startup_passed": int(self.decision.passed),
            "iu4_shadow_enabled": int(self.shadow_enabled),
            "iu4_adapter_execution_enabled": int(
                self.decision.adapter_execution_enabled
            ),
            "iu4_state_mutation_allowed": int(self.decision.state_mutation_allowed),
            "iu4_exchange_enabled": 0,
            "iu4_live_enabled": 0,
            "iu4_reason_codes": ",".join(self.decision.reason_codes),
            "iu4_atomic_state_fingerprint": self.decision.atomic_state_fingerprint,
            "iu4_atomic_transaction_sequence": self.decision.atomic_transaction_sequence,
            "iu4_repository_commit_sha": self.running_repository_commit_sha,
            "iu4_throttle_approval_id": (
                "" if self.approved_profile is None else self.approved_profile.approval_id
            ),
            "iu4_throttle_profile_sha256": (
                "" if self.approved_profile is None else self.approved_profile.file_sha256
            ),
            "iu4_throttle_policy_profile_id": (
                "" if policy is None else policy.policy_profile_id
            ),
            "iu4_throttle_policy_fingerprint": (
                "" if policy is None else policy.policy_fingerprint
            ),
        }

    def assert_current_binding(self) -> None:
        """Re-read the source state immediately before active-loop startup."""

        if self.mode == MODE_OFF:
            return
        if (
            not self.shadow_enabled
            or self.decision.adapter_execution_enabled
            or self.decision.state_mutation_allowed
            or self.coordinator is None
        ):
            raise IU4ShadowRuntimeGateError(
                IU4ShadowRuntimeGateReasonCode.GATE_DENIED,
                "IU4 SHADOW runtime decision is not read-only",
            )
        try:
            report = self.coordinator.reconciliation_report()
            state = self.coordinator.load_state()
        except Exception as exc:
            raise IU4ShadowRuntimeGateError(
                IU4ShadowRuntimeGateReasonCode.COORDINATOR_INVALID,
                str(exc),
            ) from exc
        if (
            not report.consistent
            or state.state_fingerprint != self.decision.atomic_state_fingerprint
            or state.transaction_sequence != self.decision.atomic_transaction_sequence
        ):
            raise IU4ShadowRuntimeGateError(
                IU4ShadowRuntimeGateReasonCode.GATE_DENIED,
                "IU4 SHADOW atomic source changed after startup decision",
            )


def _text(environment: Mapping[str, str], name: str) -> str:
    return str(environment.get(name, "")).strip()


def _full_commit(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != 40 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COMMIT_INVALID,
            "IU4 SHADOW requires one full lowercase repository commit SHA",
        )
    return normalized


def _git_head(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COMMIT_INVALID,
            "running repository commit cannot be resolved",
        ) from exc
    commit = _full_commit(result.stdout)
    try:
        status = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "status",
                "--porcelain",
                "--untracked-files=no",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COMMIT_INVALID,
            "running repository tracked-state cannot be resolved",
        ) from exc
    if status.stdout.strip():
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COMMIT_INVALID,
            "running repository contains tracked changes outside its commit",
        )
    return commit


def _off(startup_timestamp_utc: str) -> IU4ShadowRuntimeGateV1:
    decision = evaluate_iu4_startup_gate(
        IU4StartupModeRequestV1.off(
            startup_timestamp_utc=startup_timestamp_utc,
        ),
        None,
    )
    return IU4ShadowRuntimeGateV1(
        mode=MODE_OFF,
        decision=decision,
        running_repository_commit_sha="",
        approved_profile=None,
        coordinator=None,
    )


def evaluate_iu4_shadow_runtime_gate(
    *,
    repo_root: str | Path,
    environment: Mapping[str, str],
    operational_profile: str,
    startup_recovery_enabled: bool,
    reconciliation_gate_enabled: bool,
    startup_timestamp_utc: str | None = None,
) -> IU4ShadowRuntimeGateV1:
    """Evaluate active startup without executing the adapter or mutating state."""

    timestamp = startup_timestamp_utc or datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    mode = _text(environment, ENV_MODE).upper() or MODE_OFF
    if mode == MODE_OFF:
        return _off(timestamp)
    if mode != MODE_SHADOW:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.MODE_INVALID,
            "active runtime bridge permits only IU4 OFF or SHADOW",
        )
    if str(operational_profile).strip().upper() != "PAPER":
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.MODE_INVALID,
            "IU4 SHADOW runtime gate requires the PAPER operational profile",
        )

    root = Path(repo_root).resolve()
    profile_value = _text(environment, ENV_APPROVED_THROTTLE_PROFILE)
    profile_path = Path(profile_value or DEFAULT_APPROVED_THROTTLE_PROFILE)
    if not profile_path.is_absolute():
        profile_path = root / profile_path
    try:
        approved = load_approved_paper_entry_throttle_profile(profile_path)
    except Exception as exc:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.PROFILE_REQUIRED,
            str(exc),
        ) from exc
    if (
        approved.approval_id != APPROVED_THROTTLE_APPROVAL_ID
        or approved.file_sha256 != APPROVED_THROTTLE_PROFILE_SHA256
        or approved.policy.policy_profile_id
        != APPROVED_THROTTLE_POLICY_PROFILE_ID
        or approved.policy.policy_fingerprint
        != APPROVED_THROTTLE_POLICY_FINGERPRINT
    ):
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.PROFILE_REQUIRED,
            "IU4 SHADOW requires the exact approved throttle artifact identity",
        )

    economics = load_shadow_settings(environment)
    if not economics.ready or economics.config is None:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.ECONOMICS_INVALID,
            f"{economics.reason_code}: {economics.detail}",
        )
    if (
        economics.config.economics_profile_id != APPROVED_ECONOMICS_PROFILE_ID
        or economics.config.economics_model_version
        != APPROVED_ECONOMICS_MODEL_VERSION
        or economics.config.config_fingerprint
        != APPROVED_ECONOMICS_CONFIG_FINGERPRINT
    ):
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.ECONOMICS_INVALID,
            "IU4 SHADOW requires the exact approved economics configuration",
        )

    running_commit = _git_head(root)
    expected_commit = _full_commit(_text(environment, ENV_REPOSITORY_COMMIT))
    if expected_commit != running_commit:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COMMIT_INVALID,
            "authorized and running repository commits differ",
        )

    state_directory_value = _text(environment, ENV_ATOMIC_STATE_DIRECTORY)
    coordinator_id = _text(environment, ENV_COORDINATOR_ID)
    symbol = _text(environment, ENV_SYMBOL).upper()
    if not state_directory_value or not coordinator_id or not symbol:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COORDINATOR_INVALID,
            "IU4 SHADOW atomic directory, coordinator ID, and symbol are required",
        )
    state_directory = Path(state_directory_value)
    if not state_directory.is_absolute():
        state_directory = root / state_directory
    state_directory_absolute = state_directory.absolute()
    try:
        state_directory_resolved = state_directory.resolve(strict=True)
    except OSError as exc:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COORDINATOR_INVALID,
            "IU4 SHADOW atomic source cannot be resolved",
        ) from exc
    if (
        state_directory_resolved != state_directory_absolute
        or not state_directory.is_dir()
        or state_directory.is_symlink()
        or not (state_directory / "paper_atomic_state.json").is_file()
        or (state_directory / "paper_atomic_state.json").is_symlink()
        or (
            (state_directory / "paper_atomic_transactions").exists()
            and (
                not (state_directory / "paper_atomic_transactions").is_dir()
                or (state_directory / "paper_atomic_transactions").is_symlink()
            )
        )
    ):
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COORDINATOR_INVALID,
            "IU4 SHADOW atomic source must be an existing non-symlink state tree",
        )
    coordinator = PaperAtomicCoordinator(
        state_directory,
        economics.config,
        approved.policy,
        coordinator_id=coordinator_id,
        symbol=symbol,
    )
    request = IU4StartupModeRequestV1(
        schema_version=1,
        mode=MODE_SHADOW,
        startup_timestamp_utc=timestamp,
        operational_profile="PAPER",
        startup_recovery_enabled=bool(startup_recovery_enabled),
        reconciliation_gate_enabled=bool(reconciliation_gate_enabled),
        repository_commit_sha=expected_commit,
        expected_coordinator_id=coordinator.coordinator_id,
        expected_symbol=coordinator.symbol,
        expected_economics_profile_id=economics.config.economics_profile_id,
        expected_economics_model_version=economics.config.economics_model_version,
        expected_economics_config_fingerprint=economics.config.config_fingerprint,
        expected_throttle_policy_profile_id=approved.policy.policy_profile_id,
        expected_throttle_policy_model_version=approved.policy.policy_model_version,
        expected_throttle_policy_fingerprint=approved.policy.policy_fingerprint,
        authorization=None,
    )
    try:
        decision = evaluate_iu4_startup_gate(
            request,
            coordinator,
            running_repository_commit_sha=running_commit,
        )
    except Exception as exc:
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.COORDINATOR_INVALID,
            str(exc),
        ) from exc
    if (
        not decision.passed
        or not decision.shadow_observation_enabled
        or decision.adapter_execution_enabled
        or decision.state_mutation_allowed
        or decision.entry_allowed
    ):
        raise IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.GATE_DENIED,
            ",".join(decision.reason_codes),
        )
    return IU4ShadowRuntimeGateV1(
        mode=MODE_SHADOW,
        decision=decision,
        running_repository_commit_sha=running_commit,
        approved_profile=approved,
        coordinator=coordinator,
    )


__all__ = [
    "DEFAULT_APPROVED_THROTTLE_PROFILE",
    "ENV_APPROVED_THROTTLE_PROFILE",
    "ENV_ATOMIC_STATE_DIRECTORY",
    "ENV_COORDINATOR_ID",
    "ENV_MODE",
    "ENV_REPOSITORY_COMMIT",
    "ENV_SYMBOL",
    "IU4ShadowRuntimeGateError",
    "IU4ShadowRuntimeGateReasonCode",
    "IU4ShadowRuntimeGateV1",
    "evaluate_iu4_shadow_runtime_gate",
]
