#!/usr/bin/env python3
"""Strict loader for the approved, non-activated paper-entry throttle profile."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from live_l1.core.paper_entry_throttle import PaperEntryThrottlePolicy


class ApprovedThrottleProfileReasonCode:
    INPUT_INVALID = "PEE_RATE_APPROVED_PROFILE_INPUT_INVALID"
    SCHEMA_INVALID = "PEE_RATE_APPROVED_PROFILE_SCHEMA_INVALID"
    AUTHORITY_INVALID = "PEE_RATE_APPROVED_PROFILE_AUTHORITY_INVALID"
    BINDING_INVALID = "PEE_RATE_APPROVED_PROFILE_BINDING_INVALID"
    POLICY_INVALID = "PEE_RATE_APPROVED_PROFILE_POLICY_INVALID"


class ApprovedThrottleProfileError(ValueError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


@dataclass(frozen=True)
class ApprovedPaperEntryThrottleProfileV1:
    path: Path
    file_sha256: str
    approval_id: str
    calibration_binding: Mapping[str, Any]
    policy: PaperEntryThrottlePolicy


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _is_lower_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _json_object(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.INPUT_INVALID,
            "approved throttle profile must be a regular non-symlink file",
        )
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.INPUT_INVALID,
            "approved throttle profile must contain one valid JSON object",
        ) from exc
    if not isinstance(value, dict):
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.INPUT_INVALID,
            "approved throttle profile root must be an object",
        )
    return value


def load_approved_paper_entry_throttle_profile(
    path: str | Path,
) -> ApprovedPaperEntryThrottleProfileV1:
    candidate = Path(path)
    record = _json_object(candidate)
    expected_fields = {
        "artifact_type",
        "schema_version",
        "approval_id",
        "profile_approved",
        "runtime_activated",
        "iu4_enforced_authorized",
        "exchange_authorized",
        "live_authorized",
        "calibration_binding",
        "policy",
        "policy_fingerprint",
    }
    if set(record) != expected_fields:
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.SCHEMA_INVALID,
            "approved throttle profile fields are missing or unknown",
        )

    approval_id = record.get("approval_id")
    if (
        record.get("artifact_type") != "pee_rate_approved_policy_profile"
        or record.get("schema_version") != 1
        or not isinstance(approval_id, str)
        or not approval_id.strip()
        or record.get("profile_approved") is not True
    ):
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.SCHEMA_INVALID,
            "approved throttle profile identity or approval is invalid",
        )
    if any(
        record.get(field) is not False
        for field in (
            "runtime_activated",
            "iu4_enforced_authorized",
            "exchange_authorized",
            "live_authorized",
        )
    ):
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.AUTHORITY_INVALID,
            "approved throttle profile must remain non-activated and offline-only",
        )

    binding = record.get("calibration_binding")
    expected_binding_fields = {
        "report_sha256",
        "report_fingerprint",
        "candidate_policy_profile_id",
        "candidate_policy_fingerprint",
        "decision_replay_sha256",
    }
    if (
        not isinstance(binding, Mapping)
        or set(binding) != expected_binding_fields
        or not isinstance(binding.get("candidate_policy_profile_id"), str)
        or not str(binding.get("candidate_policy_profile_id")).strip()
        or not all(
            _is_lower_sha256(binding.get(field))
            for field in (
                "report_sha256",
                "report_fingerprint",
                "candidate_policy_fingerprint",
                "decision_replay_sha256",
            )
        )
    ):
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.BINDING_INVALID,
            "approved throttle calibration binding is invalid",
        )

    policy_record = record.get("policy")
    if (
        not isinstance(policy_record, Mapping)
        or set(policy_record) != set(PaperEntryThrottlePolicy.__dataclass_fields__)
    ):
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.POLICY_INVALID,
            "approved throttle policy fields are missing or unknown",
        )
    try:
        policy = PaperEntryThrottlePolicy.from_record(policy_record)
    except Exception as exc:
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.POLICY_INVALID,
            "approved throttle policy record is invalid",
        ) from exc
    if (
        policy.policy_model_version != "PEE_RATE_V1"
        or not _is_lower_sha256(record.get("policy_fingerprint"))
        or record.get("policy_fingerprint") != policy.policy_fingerprint
    ):
        raise ApprovedThrottleProfileError(
            ApprovedThrottleProfileReasonCode.POLICY_INVALID,
            "approved throttle policy identity or fingerprint mismatch",
        )

    return ApprovedPaperEntryThrottleProfileV1(
        path=candidate,
        file_sha256=_sha256_file(candidate),
        approval_id=approval_id.strip(),
        calibration_binding=dict(binding),
        policy=policy,
    )


__all__ = [
    "ApprovedPaperEntryThrottleProfileV1",
    "ApprovedThrottleProfileError",
    "ApprovedThrottleProfileReasonCode",
    "load_approved_paper_entry_throttle_profile",
]
