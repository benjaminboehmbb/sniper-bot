#!/usr/bin/env python3
"""Versioned, checksummed, atomic persistence for the legacy loss-cluster gate."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping


LOSS_CLUSTER_SCHEMA_VERSION = 2
LOSS_CLUSTER_LOOKBACK = 10


class LossClusterReasonCode:
    JSON_INVALID = "LOSS_CLUSTER_JSON_INVALID"
    SCHEMA_INVALID = "LOSS_CLUSTER_SCHEMA_INVALID"
    STATE_INVALID = "LOSS_CLUSTER_STATE_INVALID"
    CHECKSUM_MISMATCH = "LOSS_CLUSTER_CHECKSUM_MISMATCH"
    IO_FAILURE = "LOSS_CLUSTER_IO_FAILURE"


class LossClusterStateError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


class SimulatedLossClusterInterruption(RuntimeError):
    """Test-only interruption after durable temp write and before replace."""


def _integer(value: object, field_name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise LossClusterStateError(
            LossClusterReasonCode.STATE_INVALID,
            f"{field_name} must be an integer >= {minimum}",
        )
    return value


def _decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise LossClusterStateError(
            LossClusterReasonCode.STATE_INVALID,
            f"{field_name} must be finite numeric data",
        )
    try:
        if isinstance(value, Decimal):
            result = value
        elif isinstance(value, (int, float, str)):
            result = Decimal(str(value).strip())
        else:
            raise InvalidOperation
    except (InvalidOperation, ValueError) as exc:
        raise LossClusterStateError(
            LossClusterReasonCode.STATE_INVALID,
            f"{field_name} must be finite numeric data",
        ) from exc
    if not result.is_finite():
        raise LossClusterStateError(
            LossClusterReasonCode.STATE_INVALID,
            f"{field_name} must be finite numeric data",
        )
    return Decimal(0) if result == 0 else result


def _canonical_decimal(value: Decimal) -> str:
    if value == 0:
        return "0"
    result = format(value, "f")
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    return result


def _canonical_utc_seconds(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LossClusterStateError(
            LossClusterReasonCode.STATE_INVALID,
            f"{field_name} must be a timestamp string",
        )
    text = value.strip()
    try:
        parsed = datetime.fromisoformat(
            text[:-1] + "+00:00" if text.endswith("Z") else text
        )
    except ValueError as exc:
        raise LossClusterStateError(
            LossClusterReasonCode.STATE_INVALID,
            f"{field_name} must be an ISO-8601 timestamp",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LossClusterStateError(
            LossClusterReasonCode.STATE_INVALID,
            f"{field_name} must be timezone-aware",
        )
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def _sha256_payload(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_text(value: object) -> str:
    if not isinstance(value, str):
        raise LossClusterStateError(
            LossClusterReasonCode.CHECKSUM_MISMATCH,
            "state_fingerprint must be a string",
        )
    result = value.strip().lower()
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise LossClusterStateError(
            LossClusterReasonCode.CHECKSUM_MISMATCH,
            "state_fingerprint must be a lowercase SHA-256 digest",
        )
    return result


@dataclass(frozen=True)
class LossClusterStateV2:
    schema_version: int
    revision: int
    recent_closed_trade_pnls: tuple[Decimal, ...]
    pause_entries_remaining: int
    updated_utc: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != LOSS_CLUSTER_SCHEMA_VERSION
        ):
            raise LossClusterStateError(
                LossClusterReasonCode.SCHEMA_INVALID,
                "LossClusterStateV2 requires integer schema_version 2",
            )
        object.__setattr__(self, "revision", _integer(self.revision, "revision"))
        object.__setattr__(
            self,
            "pause_entries_remaining",
            _integer(self.pause_entries_remaining, "pause_entries_remaining"),
        )
        if not isinstance(self.recent_closed_trade_pnls, (list, tuple)):
            raise LossClusterStateError(
                LossClusterReasonCode.STATE_INVALID,
                "recent_closed_trade_pnls must be a list or tuple",
            )
        pnls = tuple(
            _decimal(value, f"recent_closed_trade_pnls[{index}]")
            for index, value in enumerate(self.recent_closed_trade_pnls)
        )
        if len(pnls) > LOSS_CLUSTER_LOOKBACK:
            raise LossClusterStateError(
                LossClusterReasonCode.STATE_INVALID,
                f"recent_closed_trade_pnls exceeds lookback {LOSS_CLUSTER_LOOKBACK}",
            )
        object.__setattr__(self, "recent_closed_trade_pnls", pnls)
        object.__setattr__(
            self,
            "updated_utc",
            _canonical_utc_seconds(self.updated_utc, "updated_utc"),
        )

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "version": self.schema_version,
            "revision": self.revision,
            "recent_closed_trade_pnls": [
                _canonical_decimal(value) for value in self.recent_closed_trade_pnls
            ],
            "pause_entries_remaining": self.pause_entries_remaining,
            "updated_utc": self.updated_utc,
        }

    @property
    def state_fingerprint(self) -> str:
        return _sha256_payload(self.canonical_payload())

    def to_record(self) -> dict[str, Any]:
        result = self.canonical_payload()
        result["state_fingerprint"] = self.state_fingerprint
        return result

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "LossClusterStateV2":
        expected_fields = {
            "schema_version",
            "version",
            "revision",
            "recent_closed_trade_pnls",
            "pause_entries_remaining",
            "updated_utc",
            "state_fingerprint",
        }
        if set(record) != expected_fields:
            raise LossClusterStateError(
                LossClusterReasonCode.SCHEMA_INVALID,
                "loss-cluster V2 fields are incomplete or unknown",
            )
        if record.get("version") != LOSS_CLUSTER_SCHEMA_VERSION:
            raise LossClusterStateError(
                LossClusterReasonCode.SCHEMA_INVALID,
                "loss-cluster version marker must equal 2",
            )
        state = cls(
            schema_version=record.get("schema_version"),
            revision=record.get("revision"),
            recent_closed_trade_pnls=record.get("recent_closed_trade_pnls"),
            pause_entries_remaining=record.get("pause_entries_remaining"),
            updated_utc=record.get("updated_utc"),
        )
        if _sha256_text(record.get("state_fingerprint")) != state.state_fingerprint:
            raise LossClusterStateError(
                LossClusterReasonCode.CHECKSUM_MISMATCH,
                "loss-cluster state fingerprint does not match its payload",
            )
        return state

    @classmethod
    def from_legacy_v1(cls, record: Mapping[str, Any]) -> "LossClusterStateV2":
        expected_fields = {
            "schema_version",
            "version",
            "recent_closed_trade_pnls",
            "pause_entries_remaining",
            "updated_utc",
        }
        if set(record) != expected_fields:
            raise LossClusterStateError(
                LossClusterReasonCode.SCHEMA_INVALID,
                "legacy loss-cluster fields are incomplete or unknown",
            )
        if record.get("schema_version") != 1 or record.get("version") != 1:
            raise LossClusterStateError(
                LossClusterReasonCode.SCHEMA_INVALID,
                "legacy loss-cluster version markers must equal 1",
            )
        raw_pnls = record.get("recent_closed_trade_pnls")
        if not isinstance(raw_pnls, list) or any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in raw_pnls
        ):
            raise LossClusterStateError(
                LossClusterReasonCode.STATE_INVALID,
                "legacy recent_closed_trade_pnls must contain only JSON numbers",
            )
        return cls(
            schema_version=LOSS_CLUSTER_SCHEMA_VERSION,
            revision=0,
            recent_closed_trade_pnls=tuple(raw_pnls),
            pause_entries_remaining=record.get("pause_entries_remaining"),
            updated_utc=record.get("updated_utc"),
        )


@dataclass(frozen=True)
class LossClusterLoadResult:
    state: LossClusterStateV2 | None
    existed: bool
    migrated_legacy_v1: bool


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(str(directory), flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class LossClusterStateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> LossClusterLoadResult:
        if not self.path.exists():
            return LossClusterLoadResult(
                state=None,
                existed=False,
                migrated_legacy_v1=False,
            )
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                record = json.load(handle)
        except json.JSONDecodeError as exc:
            raise LossClusterStateError(
                LossClusterReasonCode.JSON_INVALID,
                "loss-cluster state is not valid JSON",
            ) from exc
        except OSError as exc:
            raise LossClusterStateError(
                LossClusterReasonCode.IO_FAILURE,
                "loss-cluster state cannot be read",
            ) from exc
        if not isinstance(record, dict):
            raise LossClusterStateError(
                LossClusterReasonCode.JSON_INVALID,
                "loss-cluster JSON root must be an object",
            )
        raw_version = record.get("schema_version")
        if isinstance(raw_version, bool) or not isinstance(raw_version, int):
            raise LossClusterStateError(
                LossClusterReasonCode.SCHEMA_INVALID,
                "loss-cluster schema_version must be an integer",
            )
        if raw_version == LOSS_CLUSTER_SCHEMA_VERSION:
            state = LossClusterStateV2.from_record(record)
            migrated = False
        elif raw_version == 1:
            state = LossClusterStateV2.from_legacy_v1(record)
            migrated = True
        else:
            raise LossClusterStateError(
                LossClusterReasonCode.SCHEMA_INVALID,
                f"unsupported loss-cluster schema_version {raw_version}",
            )
        return LossClusterLoadResult(
            state=state,
            existed=True,
            migrated_legacy_v1=migrated,
        )

    def save(
        self,
        state: LossClusterStateV2,
        *,
        simulate_interruption_before_replace: bool = False,
    ) -> None:
        if not isinstance(state, LossClusterStateV2):
            raise LossClusterStateError(
                LossClusterReasonCode.STATE_INVALID,
                "save requires LossClusterStateV2",
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(
            state.to_record(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ) + "\n"
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                dir=str(self.path.parent),
                prefix=f".{self.path.name}.",
                suffix=".tmp",
            )
        except OSError as exc:
            raise LossClusterStateError(
                LossClusterReasonCode.IO_FAILURE,
                "loss-cluster temporary file cannot be created",
            ) from exc
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            if simulate_interruption_before_replace:
                raise SimulatedLossClusterInterruption(
                    "simulated interruption before atomic loss-cluster replace"
                )
            os.replace(temporary_path, self.path)
            _fsync_directory(self.path.parent)
        except SimulatedLossClusterInterruption:
            temporary_path.unlink(missing_ok=True)
            raise
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise LossClusterStateError(
                LossClusterReasonCode.IO_FAILURE,
                "loss-cluster state cannot be atomically replaced",
            ) from exc


__all__ = [
    "LOSS_CLUSTER_LOOKBACK",
    "LOSS_CLUSTER_SCHEMA_VERSION",
    "LossClusterLoadResult",
    "LossClusterReasonCode",
    "LossClusterStateError",
    "LossClusterStateStore",
    "LossClusterStateV2",
    "SimulatedLossClusterInterruption",
]
