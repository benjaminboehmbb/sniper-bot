#!/usr/bin/env python3
"""Offline IU4 I6 recovery, monitoring and compatibility projection boundary.

The module is intentionally dormant: it has no caller in the live loop, the
adapter, execution or any launcher.  Every mutating API requires an explicit
caller-owned absolute root and operates only below that root.
"""

from __future__ import annotations

import fcntl
import errno
import hashlib
import json
import os
import re
import stat
import sys
import unicodedata
from dataclasses import dataclass, fields, replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, ClassVar, Mapping

from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    PaperEntryThrottleError,
)
from live_l1.state.models import LegacyRiskStateS4ProjectionV1
from live_l1.state.state_store import (
    read_legacy_safety_projection,
    write_legacy_safety_projection,
)
from live_l1.state.iu4_lifecycle_ledger import (
    AUTHORITY_PAIRS,
    IU4LifecycleLedgerError,
    IU4LifecycleRecordV1,
    IU4LifecycleLedgerV1,
    authority_generation_id,
    canonical_json as lifecycle_canonical_json,
    fingerprint as lifecycle_fingerprint,
)


NONE = "NONE"
EMPTY = "EMPTY"


class IU4RecoveryProjectionError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def _raise_lifecycle_publication_error(
    exc: BaseException, conflict_code: str, message: str
) -> None:
    code = "PEE_IU4_RESOURCE_EXHAUSTED" if _has_resource_cause(exc) else conflict_code
    raise IU4RecoveryProjectionError(code, message) from exc


def _has_resource_cause(exc: BaseException) -> bool:
    pending: list[BaseException] = [exc]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        if isinstance(current, (OSError, MemoryError)):
            return True
        seen.add(id(current))
        for linked in (current.__cause__, current.__context__):
            if linked is not None:
                pending.append(linked)
    return False


def _raise_cleanup_error_if_primary_absent(
    cleanup_error: BaseException | None,
    *,
    primary_active: bool,
    message: str,
) -> None:
    """Classify cleanup resource failures without replacing a primary result."""

    if cleanup_error is None or primary_active:
        return
    if _has_resource_cause(cleanup_error):
        raise IU4RecoveryProjectionError(
            "PEE_IU4_RESOURCE_EXHAUSTED", message
        ) from cleanup_error
    raise cleanup_error


def _cleanup_descriptors_preserving_primary(
    descriptors: tuple[int, ...],
    *,
    primary_active: bool,
    message: str,
    unlock_descriptor: int = -1,
) -> None:
    """Attempt every cleanup and preserve an already selected primary result."""

    cleanup_error: BaseException | None = None
    if unlock_descriptor >= 0:
        try:
            fcntl.flock(unlock_descriptor, fcntl.LOCK_UN)
        except BaseException as exc:
            cleanup_error = exc
    for descriptor in descriptors:
        if descriptor < 0:
            continue
        try:
            os.close(descriptor)
        except BaseException as exc:
            if cleanup_error is None:
                cleanup_error = exc
    _raise_cleanup_error_if_primary_absent(
        cleanup_error,
        primary_active=primary_active,
        message=message,
    )


def canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            "value is not canonical JSON",
        ) from exc


def _hash(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _sha(value: Any, name: str, *, allow_none: bool = False) -> str:
    if allow_none and value == NONE:
        return value
    if type(value) is not str or len(value) != 64 or any(
        char not in "0123456789abcdef" for char in value
    ):
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"{name} is not lowercase hex64"
        )
    return value


def _text(value: Any, name: str, *, allow_none: bool = False) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"invalid {name}"
        )
    if not allow_none and value == NONE:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"{name} may not be NONE"
        )
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"{name} is not canonical ASCII"
        ) from exc
    return value


def _integer(value: Any, name: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"invalid {name}"
        )
    return value


def _boolean(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"invalid {name}"
        )
    return value


def _utc(value: Any, name: str) -> str:
    _text(value, name)
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError as exc:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"invalid {name}"
        ) from exc
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"noncanonical {name}"
        )
    return value


def _utc_or_none(value: Any, name: str) -> str:
    if value == NONE:
        return value
    return _utc(value, name)


def _decimal(value: Any, name: str) -> str:
    if type(value) is not str or not value:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"invalid {name}"
        )
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"invalid {name}"
        ) from exc
    if not number.is_finite():
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"nonfinite {name}"
        )
    canonical = format(number, "f")
    if "." in canonical:
        canonical = canonical.rstrip("0").rstrip(".")
    if canonical in {"", "-0"}:
        canonical = "0"
    if canonical != value:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"noncanonical {name}"
        )
    return value


def _validate_json_tree(value: Any, name: str) -> None:
    if value is None or type(value) in (str, int, bool):
        return
    if type(value) is list:
        for item in value:
            _validate_json_tree(item, name)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"non-string {name} key"
                )
            _validate_json_tree(item, name)
        return
    raise IU4RecoveryProjectionError(
        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"invalid primitive in {name}"
    )


def _hex40(value: Any, name: str) -> str:
    if type(value) is not str or len(value) != 40 or any(
        char not in "0123456789abcdef" for char in value
    ):
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"{name} is not lowercase hex40"
        )
    return value


def _exact_record(value: Any, names: set[str], name: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != names:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            f"{name} fields are missing or unknown",
        )
    return value


def _path(value: Any, name: str) -> str:
    text = _text(value, name)
    if not text.startswith("/") or text == "/" or text.endswith("/") or "\x00" in text:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"invalid absolute {name}"
        )
    if text != os.path.abspath(text) or unicodedata.normalize("NFC", text) != text:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"noncanonical {name}"
        )
    return text


def _validate_identifier_tree(value: Any, name: str) -> None:
    """Apply the Section-7.7 primitive rules to a nested exact-shape record."""

    if type(value) is dict:
        for key, item in value.items():
            _validate_identifier_tree(item, f"{name}.{key}")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _validate_identifier_tree(item, f"{name}[{index}]")
        return
    leaf = name.rsplit(".", 1)[-1]
    if leaf == "direct_continuation_nonce_hash" and value == NONE:
        return
    if leaf.endswith(("_fingerprint", "_sha256", "_hash")):
        _sha(value, name)
    elif leaf.endswith("_id") and value != NONE:
        _text(value, name)
    elif leaf.endswith(("_pid", "_tid", "_start_time_ns")):
        _integer(value, name, minimum=1)
    elif leaf.endswith(("_count", "_sequence", "_ms", "_bytes")):
        _integer(value, name)


_LEGACY_POSITION_FIELDS = {
    "schema_version", "system_state_id", "symbol", "position", "side",
    "size", "entry_price", "entry_timestamp_utc", "position_size",
    "last_intent_id", "snapshot_id",
}
_LEGACY_LOSS_FIELDS = {
    "schema_version", "pause_entries_remaining", "recent_closed_trade_pnls",
    "revision", "updated_utc", "version", "state_fingerprint",
}
_LEGACY_THROTTLE_FIELDS = {
    "schema_version", "entries_today", "last_entry_event_id",
    "last_entry_timestamp_utc", "last_update_event_id", "policy_fingerprint",
    "policy_model_version", "policy_profile_id", "recent_entry_events",
    "total_accepted_entry_count", "utc_day", "state_fingerprint",
}
_THROTTLE_EVENT_FIELDS = {
    "schema_version", "entry_sequence", "entry_event_id",
    "previous_entry_event_id", "entry_timestamp_utc",
    "policy_model_version", "policy_profile_id", "policy_fingerprint",
}
_LEGACY_CURSOR_FIELDS = {
    "schema_version", "tick_id", "snapshot_id", "intent_id",
    "timestamp_utc", "cursor_fingerprint",
}
_GENESIS_PROFILE_FIELDS = {
    "runtime_control_profile_id", "runtime_control_fingerprint",
    "loss_cluster_policy_id", "loss_cluster_policy_fingerprint",
    "economics_profile_id", "economics_config_fingerprint",
    "throttle_policy_profile_id", "throttle_policy_fingerprint",
}
_GENESIS_COMPONENT_FIELDS = {
    "position", "account", "throttle", "loss_cluster", "progress_cursor",
    "risk", "entry_quote", "state", "business", "core",
}
_HANDOFF_MAPPING_FIELDS = {
    "direction", "source_snapshot_id", "source_snapshot_fingerprint",
    "position_fingerprint", "risk_fingerprint", "loss_cluster_fingerprint",
    "throttle_fingerprint", "progress_cursor_fingerprint",
    "target_business_fingerprint", "target_core_fingerprint",
}


class _ContentAddressedArtifact:
    SCHEMA_VERSION: ClassVar[int] = 1
    ARTIFACT_TYPE: ClassVar[str]
    ID_FIELD: ClassVar[str]
    FINGERPRINT_FIELD: ClassVar[str]
    ID_PREFIX: ClassVar[str]
    TUPLE_FIELDS: ClassVar[frozenset[str]] = frozenset()

    def _validate_specific(self) -> None:
        return None

    def __post_init__(self) -> None:
        if type(getattr(self, "schema_version")) is not int or getattr(
            self, "schema_version"
        ) != self.SCHEMA_VERSION:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "unsupported artifact schema"
            )
        if type(getattr(self, "artifact_type")) is not str or getattr(
            self, "artifact_type"
        ) != self.ARTIFACT_TYPE:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "wrong artifact type"
            )
        for field in fields(self):
            field_value = self._serialize_value(getattr(self, field.name))
            _validate_json_tree(field_value, field.name)
            if type(field_value) is str:
                if field.name.endswith(("_fingerprint", "_sha256")):
                    _sha(field_value, field.name, allow_none=True)
                elif field.name.endswith("_id"):
                    _text(field_value, field.name, allow_none=True)
        self._validate_specific()
        material = self.to_record()
        supplied_id = material.pop(self.ID_FIELD)
        supplied_fingerprint = material.pop(self.FINGERPRINT_FIELD)
        expected_id = self.ID_PREFIX + _hash(material)
        if supplied_id != expected_id:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "artifact ID mismatch"
            )
        material[self.ID_FIELD] = supplied_id
        expected_fingerprint = _hash(material)
        if supplied_fingerprint != expected_fingerprint:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "artifact fingerprint mismatch"
            )

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, _ContentAddressedArtifact):
            return value.to_record()
        if type(value) is tuple:
            return [_ContentAddressedArtifact._serialize_value(item) for item in value]
        if type(value) is list:
            return [_ContentAddressedArtifact._serialize_value(item) for item in value]
        if type(value) is dict:
            return {
                key: _ContentAddressedArtifact._serialize_value(item)
                for key, item in value.items()
            }
        return value

    def to_record(self) -> dict[str, Any]:
        return {
            field.name: self._serialize_value(getattr(self, field.name))
            for field in fields(self)
        }

    @classmethod
    def build(cls, **values: Any):
        names = {field.name for field in fields(cls)}
        values = dict(values)
        values["schema_version"] = cls.SCHEMA_VERSION
        values["artifact_type"] = cls.ARTIFACT_TYPE
        material = {
            name: cls._serialize_value(values[name])
            for name in names
            if name not in {cls.ID_FIELD, cls.FINGERPRINT_FIELD}
        }
        artifact_id = cls.ID_PREFIX + _hash(material)
        values[cls.ID_FIELD] = artifact_id
        material[cls.ID_FIELD] = artifact_id
        values[cls.FINGERPRINT_FIELD] = _hash(material)
        return cls(**values)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        if type(record) is not dict or set(record) != {field.name for field in fields(cls)}:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                f"{cls.ARTIFACT_TYPE} fields are missing or unknown",
            )
        values = dict(record)
        for name in cls.TUPLE_FIELDS:
            if type(values[name]) is not list:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", f"{name} is not a canonical array"
                )
            values[name] = tuple(values[name])
        value = cls(**values)
        if value.to_record() != record:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "artifact record is not canonical"
            )
        return value


@dataclass(frozen=True)
class IU4LegacySafetySnapshotV1(_ContentAddressedArtifact):
    schema_version: int
    artifact_type: str
    legacy_safety_snapshot_id: str
    system_state_id: str
    symbol: str
    source_path: str
    source_bytes_sha256: str
    owner_epoch: str
    authority_generation_id: str
    position_record: dict[str, Any]
    risk_record: dict[str, Any]
    loss_cluster_record: dict[str, Any]
    loss_cluster_fingerprint: str
    throttle_record: dict[str, Any]
    throttle_fingerprint: str
    progress_cursor_record: dict[str, Any]
    progress_cursor_fingerprint: str
    position_fingerprint: str
    risk_fingerprint: str
    snapshot_fingerprint: str

    ARTIFACT_TYPE = "iu4_legacy_safety_snapshot_v1"
    ID_FIELD = "legacy_safety_snapshot_id"
    FINGERPRINT_FIELD = "snapshot_fingerprint"
    ID_PREFIX = "IU4-LEGACY-SAFETY-SNAPSHOT-V1-"

    def _validate_specific(self) -> None:
        for name in ("system_state_id", "symbol", "authority_generation_id"):
            _text(getattr(self, name), name)
        _path(self.source_path, "source_path")
        if self.owner_epoch not in {"LEGACY", "PEE"}:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID", "invalid snapshot Owner"
            )
        for name in (
            "source_bytes_sha256", "loss_cluster_fingerprint", "throttle_fingerprint",
            "progress_cursor_fingerprint", "position_fingerprint", "risk_fingerprint",
        ):
            _sha(getattr(self, name), name)
        position = _exact_record(
            self.position_record, _LEGACY_POSITION_FIELDS, "position_record"
        )
        if position["schema_version"] != 1 or position["system_state_id"] != self.system_state_id:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy S2 identity differs"
            )
        if position["symbol"] != self.symbol or position["position"] not in {"FLAT", "LONG", "SHORT"}:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy S2 symbol/position differs"
            )
        for name in ("size", "position_size"):
            _decimal(position[name], f"position_record.{name}")
        if position["entry_price"] != NONE:
            _decimal(position["entry_price"], "position_record.entry_price")
        _utc_or_none(
            position["entry_timestamp_utc"],
            "position_record.entry_timestamp_utc",
        )
        for name in ("last_intent_id", "snapshot_id"):
            _text(position[name], f"position_record.{name}", allow_none=True)
        if position["side"] not in {NONE, "LONG", "SHORT"}:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy S2 side is invalid"
            )
        if position["position"] == "FLAT" and (
            position["side"] != NONE
            or position["size"] != "0"
            or position["position_size"] != "0"
            or position["entry_price"] != NONE
            or position["entry_timestamp_utc"] != NONE
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy FLAT S2 is inconsistent"
            )
        if position["position"] in {"LONG", "SHORT"} and (
            position["side"] != position["position"]
            or Decimal(position["size"]) <= 0
            or position["position_size"] != position["size"]
            or position["entry_price"] == NONE
            or Decimal(position["entry_price"]) <= 0
            or position["entry_timestamp_utc"] == NONE
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                "Legacy OPEN S2 is inconsistent",
            )
        try:
            risk = LegacyRiskStateS4ProjectionV1.from_record(self.risk_record)
        except ValueError as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy S4 record is invalid"
            ) from exc
        loss = _exact_record(
            self.loss_cluster_record, _LEGACY_LOSS_FIELDS, "loss_cluster_record"
        )
        throttle = _exact_record(
            self.throttle_record, _LEGACY_THROTTLE_FIELDS, "throttle_record"
        )
        cursor = _exact_record(
            self.progress_cursor_record, _LEGACY_CURSOR_FIELDS,
            "progress_cursor_record",
        )
        if (
            loss["schema_version"] != 2
            or loss["version"] != 2
            or type(loss["recent_closed_trade_pnls"]) is not list
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy Loss record is invalid"
            )
        for name in ("pause_entries_remaining", "revision"):
            _integer(loss[name], f"loss_cluster_record.{name}")
        for index, value in enumerate(loss["recent_closed_trade_pnls"]):
            _decimal(value, f"loss_cluster_record.recent_closed_trade_pnls[{index}]")
        _utc_or_none(loss["updated_utc"], "loss_cluster_record.updated_utc")
        if throttle["schema_version"] != 1 or type(throttle["recent_entry_events"]) is not list:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy Throttle record is invalid"
            )
        for name in ("entries_today", "total_accepted_entry_count"):
            _integer(throttle[name], f"throttle_record.{name}")
        for name in ("last_entry_event_id", "last_update_event_id"):
            _text(throttle[name], f"throttle_record.{name}", allow_none=True)
        _utc_or_none(
            throttle["last_entry_timestamp_utc"],
            "throttle_record.last_entry_timestamp_utc",
        )
        _sha(throttle["policy_fingerprint"], "throttle_record.policy_fingerprint")
        _text(throttle["policy_model_version"], "throttle_record.policy_model_version")
        _text(throttle["policy_profile_id"], "throttle_record.policy_profile_id")
        try:
            parsed_day = datetime.strptime(throttle["utc_day"], "%Y-%m-%d")
        except (TypeError, ValueError) as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy Throttle day is invalid"
            ) from exc
        if parsed_day.strftime("%Y-%m-%d") != throttle["utc_day"]:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                "Legacy Throttle day is not canonical",
            )
        if throttle["entries_today"] > throttle["total_accepted_entry_count"]:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                "Legacy Throttle counts are inconsistent",
            )
        parsed_events: list[AcceptedEntryEventV1] = []
        for index, raw_event in enumerate(throttle["recent_entry_events"]):
            if type(raw_event) is not dict or set(raw_event) != _THROTTLE_EVENT_FIELDS:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    f"Legacy Throttle event {index} has an invalid shape",
                )
            try:
                parsed_event = AcceptedEntryEventV1.from_record(raw_event)
            except (PaperEntryThrottleError, TypeError) as exc:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    f"Legacy Throttle event {index} is invalid",
                ) from exc
            if parsed_event.to_record() != raw_event:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    f"Legacy Throttle event {index} is not canonical",
                )
            if (
                parsed_event.policy_model_version
                != throttle["policy_model_version"]
                or parsed_event.policy_profile_id != throttle["policy_profile_id"]
                or parsed_event.policy_fingerprint != throttle["policy_fingerprint"]
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    "Legacy Throttle event policy binding differs",
                )
            if parsed_events and (
                parsed_event.entry_sequence
                != parsed_events[-1].entry_sequence + 1
                or parsed_event.previous_entry_event_id
                != parsed_events[-1].entry_event_id
                or parsed_event.entry_timestamp_utc
                < parsed_events[-1].entry_timestamp_utc
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    "Legacy Throttle event chain is inconsistent",
                )
            parsed_events.append(parsed_event)
        if len({event.entry_event_id for event in parsed_events}) != len(parsed_events):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                "Legacy Throttle event identifiers are not unique",
            )
        total = throttle["total_accepted_entry_count"]
        if total == 0:
            if (
                throttle["entries_today"] != 0
                or parsed_events
                or throttle["last_entry_event_id"] != NONE
                or throttle["last_update_event_id"] != NONE
                or throttle["last_entry_timestamp_utc"] != NONE
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    "Empty Legacy Throttle state is inconsistent",
                )
        else:
            if not parsed_events:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    "Non-empty Legacy Throttle state has no retained events",
                )
            latest = parsed_events[-1]
            if (
                latest.entry_sequence != total
                or throttle["last_entry_event_id"] != latest.entry_event_id
                or throttle["last_update_event_id"] != latest.entry_event_id
                or throttle["last_entry_timestamp_utc"]
                != latest.entry_timestamp_utc
                or throttle["utc_day"] != latest.entry_timestamp_utc[:10]
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    "Legacy Throttle head binding differs",
                )
            visible_today = sum(
                event.entry_timestamp_utc[:10] == throttle["utc_day"]
                for event in parsed_events
            )
            if visible_today > throttle["entries_today"]:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    "Legacy Throttle daily count is inconsistent",
                )
        if cursor["schema_version"] != 1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy Cursor schema is invalid"
            )
        _integer(cursor["tick_id"], "progress_cursor_record.tick_id")
        for name in ("snapshot_id", "intent_id"):
            _text(cursor[name], f"progress_cursor_record.{name}", allow_none=True)
        _utc_or_none(cursor["timestamp_utc"], "progress_cursor_record.timestamp_utc")
        for name, record, fingerprint_field, supplied in (
            ("position", position, None, self.position_fingerprint),
            ("risk", risk.to_record(), None, self.risk_fingerprint),
            ("loss_cluster", loss, "state_fingerprint", self.loss_cluster_fingerprint),
            ("throttle", throttle, "state_fingerprint", self.throttle_fingerprint),
            ("progress_cursor", cursor, "cursor_fingerprint", self.progress_cursor_fingerprint),
        ):
            if fingerprint_field is None:
                expected = _hash(record)
            else:
                expected = _sha(record[fingerprint_field], f"{name}.{fingerprint_field}")
                payload = dict(record)
                payload.pop(fingerprint_field)
                if expected != _hash(payload):
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                        f"{name} embedded fingerprint differs",
                    )
            if supplied != expected:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                    f"{name} cross-fingerprint differs",
                )


@dataclass(frozen=True)
class IU4StateHandoffManifestV1(_ContentAddressedArtifact):
    schema_version: int
    artifact_type: str
    handoff_manifest_id: str
    direction: str
    repository_commit: str
    symbol: str
    coordinator_id: str
    system_state_id: str
    source_state_path: str
    source_state_schema: int
    source_state_bytes_sha256: str
    source_state_fingerprint: str
    competing_state_path: str
    competing_state_schema: int
    competing_state_bytes_sha256: str
    competing_state_fingerprint: str
    source_safety_snapshot: dict[str, Any]
    target_business_fingerprint: str
    target_core_fingerprint: str
    previous_owner_epoch: int
    new_owner_epoch: int
    source_authority_generation_id: str
    source_authority_commit_anchor: str
    planned_authority_generation_id: str
    mapping_record: dict[str, Any]
    operator: str
    operation_timestamp_utc: str
    approval_reference: str
    approval_fingerprint: str
    operation_attempt_id: str
    manifest_fingerprint: str

    ARTIFACT_TYPE = "iu4_state_handoff_manifest_v1"
    ID_FIELD = "handoff_manifest_id"
    FINGERPRINT_FIELD = "manifest_fingerprint"
    ID_PREFIX = "IU4-STATE-HANDOFF-MANIFEST-V1-"

    def _validate_specific(self) -> None:
        if self.direction not in {"LEGACY_TO_PEE", "PEE_TO_LEGACY"}:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID", "invalid handoff direction"
            )
        _hex40(self.repository_commit, "repository_commit")
        for name in (
            "symbol", "coordinator_id", "system_state_id",
            "source_authority_generation_id", "planned_authority_generation_id",
            "operator", "approval_reference", "operation_attempt_id",
        ):
            _text(getattr(self, name), name)
        _path(self.source_state_path, "source_state_path")
        _path(self.competing_state_path, "competing_state_path")
        for name in ("source_state_schema", "competing_state_schema"):
            _integer(getattr(self, name), name, minimum=1)
        _integer(self.previous_owner_epoch, "previous_owner_epoch")
        if _integer(self.new_owner_epoch, "new_owner_epoch", minimum=1) != self.previous_owner_epoch + 1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID", "handoff Owner is not monotone"
            )
        for name in (
            "source_state_bytes_sha256", "source_state_fingerprint",
            "competing_state_bytes_sha256", "competing_state_fingerprint",
            "target_business_fingerprint", "target_core_fingerprint",
            "source_authority_commit_anchor", "approval_fingerprint",
        ):
            _sha(getattr(self, name), name)
        _utc(self.operation_timestamp_utc, "operation_timestamp_utc")
        snapshot = IU4LegacySafetySnapshotV1.from_record(self.source_safety_snapshot)
        if snapshot.system_state_id != self.system_state_id or snapshot.symbol != self.symbol:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Handoff source Snapshot identity differs"
            )
        mapping = _exact_record(
            self.mapping_record, _HANDOFF_MAPPING_FIELDS, "mapping_record"
        )
        expected_mapping = handoff_mapping_record(
            direction=self.direction,
            source_snapshot=snapshot,
            target_business_fingerprint=self.target_business_fingerprint,
            target_core_fingerprint=self.target_core_fingerprint,
        )
        if mapping != expected_mapping:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Handoff mapping differs"
            )
        expected_owner = "LEGACY" if self.direction == "LEGACY_TO_PEE" else "PEE"
        expected_schemas = (1, 2) if self.direction == "LEGACY_TO_PEE" else (2, 1)
        if (
            snapshot.owner_epoch != expected_owner
            or snapshot.source_path != self.source_state_path
            or snapshot.source_bytes_sha256 != self.source_state_bytes_sha256
            or snapshot.authority_generation_id
            != self.source_authority_generation_id
            or (self.source_state_schema, self.competing_state_schema)
            != expected_schemas
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                "Handoff source or schema binding differs",
            )
        _text(self.approval_reference, "approval_reference")


@dataclass(frozen=True)
class IU4CleanGenesisManifestV1(_ContentAddressedArtifact):
    schema_version: int
    artifact_type: str
    clean_genesis_manifest_id: str
    symbol: str
    starting_equity: str
    profile_bindings: dict[str, Any]
    coordinator_id: str
    system_state_id: str
    state_owner_epoch: str
    initial_state_record: dict[str, Any]
    empty_journal_inventory_fingerprint: str
    component_fingerprints: dict[str, Any]
    state_path: str
    journal_path: str
    legacy_absence_proof_sha256: str
    atomic_absence_proof_sha256: str
    operator: str
    operation_timestamp_utc: str
    approval_reference: str
    approval_fingerprint: str
    process_instance_id: str
    operation_attempt_id: str
    manifest_fingerprint: str

    ARTIFACT_TYPE = "iu4_clean_genesis_manifest_v1"
    ID_FIELD = "clean_genesis_manifest_id"
    FINGERPRINT_FIELD = "manifest_fingerprint"
    ID_PREFIX = "IU4-CLEAN-GENESIS-MANIFEST-V1-"

    def _validate_specific(self) -> None:
        _decimal(self.starting_equity, "starting_equity")
        if Decimal(self.starting_equity) <= 0 or self.state_owner_epoch != "PEE":
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "invalid Genesis State"
            )
        from live_l1.state.paper_atomic_coordinator import (
            AtomicPaperStateV2,
            PaperAtomicCoordinatorError,
        )

        if type(self.profile_bindings) is not dict or set(self.profile_bindings) != _GENESIS_PROFILE_FIELDS:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "Genesis profiles are incomplete"
            )
        for name, value in self.profile_bindings.items():
            (_sha if name.endswith("fingerprint") else _text)(value, f"profile_bindings.{name}")
        if type(self.initial_state_record) is not dict:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "Genesis initial State is incomplete"
            )
        try:
            initial = AtomicPaperStateV2.from_record(self.initial_state_record)
        except Exception as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "Genesis initial State is invalid"
            ) from exc
        if initial.transaction_sequence != 0 or initial.journal_head != EMPTY:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "Genesis must start at EMPTY sequence zero"
            )
        if (
            initial.coordinator_id != self.coordinator_id
            or initial.system_state_id != self.system_state_id
            or initial.position.symbol != self.symbol
            or initial.state_owner_epoch != self.state_owner_epoch
            or str(initial.account.starting_equity_quote) != self.starting_equity
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "Genesis initial State identity differs"
            )
        if type(self.component_fingerprints) is not dict or set(self.component_fingerprints) != _GENESIS_COMPONENT_FIELDS:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "Genesis component map is incomplete"
            )
        for name, value in self.component_fingerprints.items():
            if name == "entry_quote" and value == NONE:
                continue
            _sha(value, f"component_fingerprints.{name}")
        _path(self.state_path, "state_path")
        _path(self.journal_path, "journal_path")
        for name in (
            "symbol", "coordinator_id", "system_state_id", "operator",
            "approval_reference", "process_instance_id", "operation_attempt_id",
        ):
            _text(getattr(self, name), name)
        for name in (
            "empty_journal_inventory_fingerprint", "legacy_absence_proof_sha256",
            "atomic_absence_proof_sha256", "approval_fingerprint",
        ):
            _sha(getattr(self, name), name)
        _utc(self.operation_timestamp_utc, "operation_timestamp_utc")
        if self.profile_bindings != _atomic_profile_bindings(initial):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID",
                "Genesis profile cross-bindings differ",
            )
        if self.component_fingerprints != _atomic_component_fingerprints(initial):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID",
                "Genesis component cross-bindings differ",
            )
        if (
            self.empty_journal_inventory_fingerprint
            != _empty_journal_inventory_fingerprint(self.journal_path)
            or self.atomic_absence_proof_sha256
            != _absence_proof_sha256("ATOMIC_STATE", self.state_path)
            or self.legacy_absence_proof_sha256
            != _absence_proof_sha256("LEGACY_STATE", self.state_path + ".legacy")
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID",
                "Genesis absence or inventory proof differs",
            )


@dataclass(frozen=True)
class IU4CompatibilityProjectionV1(_ContentAddressedArtifact):
    schema_version: int
    artifact_type: str
    projection_id: str
    non_authoritative_projection: bool
    projection_id_material: str
    atomic_transaction_event_id: str
    atomic_transaction_fingerprint: str
    atomic_transaction_sequence: int
    atomic_journal_head: str
    atomic_state_fingerprint: str
    authority_generation_id: str
    authority_prepare_record_fingerprint: str
    projected_legacy_safety: dict[str, Any]
    source_path: str
    target_path: str
    source_bytes_sha256: str
    target_bytes_sha256: str
    projected_at_utc: str
    projection_fingerprint: str

    ARTIFACT_TYPE = "iu4_compatibility_projection_v1"
    ID_FIELD = "projection_id"
    FINGERPRINT_FIELD = "projection_fingerprint"
    ID_PREFIX = "IU4-COMPATIBILITY-PROJECTION-V1-"

    @classmethod
    def build(cls, **values: Any):
        values.setdefault("non_authoritative_projection", True)
        return super().build(**values)

    def _validate_specific(self) -> None:
        if self.non_authoritative_projection is not True:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_AUTHORITY_ROOT_MISMATCH", "projection may not claim authority"
            )
        _integer(self.atomic_transaction_sequence, "atomic_transaction_sequence", minimum=1)
        for name in (
            "projection_id_material", "atomic_transaction_event_id",
            "authority_generation_id",
        ):
            _text(getattr(self, name), name)
        _path(self.source_path, "source_path")
        _path(self.target_path, "target_path")
        for name in (
            "atomic_transaction_fingerprint", "atomic_journal_head", "atomic_state_fingerprint",
            "authority_prepare_record_fingerprint", "source_bytes_sha256", "target_bytes_sha256",
        ):
            _sha(getattr(self, name), name)
        projected = IU4LegacySafetySnapshotV1.from_record(
            self.projected_legacy_safety
        )
        if (
            projected.source_path != self.source_path
            or projected.source_bytes_sha256 != self.source_bytes_sha256
            or projected.authority_generation_id != self.authority_generation_id
            or self.target_bytes_sha256
            != hashlib.sha256(
                canonical_json_bytes(projected.to_record())
            ).hexdigest()
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_AUTHORITY_ROOT_MISMATCH",
                "projection source or target binding differs",
            )
        _utc(self.projected_at_utc, "projected_at_utc")


@dataclass(frozen=True)
class IU4PersistenceWorkerDeathTrustAnchorV1(_ContentAddressedArtifact):
    schema_version: int
    artifact_type: str
    trust_anchor_id: str
    allowed_attestor_type: str
    trusted_attestor_id: str
    trusted_attestor_executable_sha256: str
    trusted_collector_id: str
    trusted_source_evidence_sha256: str
    expected_boot_id: str
    expected_runtime_session_id: str
    approval_reference: str
    approval_fingerprint: str
    trusted_anchor_registry_id: str
    trusted_anchor_registry_fingerprint: str
    valid_from_utc: str
    valid_until_utc: str
    trust_anchor_fingerprint: str

    ARTIFACT_TYPE = "iu4_persistence_worker_death_trust_anchor_v1"
    ID_FIELD = "trust_anchor_id"
    FINGERPRINT_FIELD = "trust_anchor_fingerprint"
    ID_PREFIX = "IU4-PERSISTENCE-WORKER-DEATH-TRUST-ANCHOR-V1-"

    def _validate_specific(self) -> None:
        if self.allowed_attestor_type not in {
            "TERMINAL_PARENT_GUARDIAN_V13", "NATIVE_TRIP_BROKER_V10"
        }:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "untrusted attestor type"
            )
        for name in (
            "trusted_attestor_executable_sha256", "trusted_source_evidence_sha256",
            "approval_fingerprint", "trusted_anchor_registry_fingerprint",
        ):
            _sha(getattr(self, name), name)
        _text(self.approval_reference, "approval_reference")
        if _as_datetime(_utc(self.valid_until_utc, "valid_until_utc")) <= _as_datetime(
            _utc(self.valid_from_utc, "valid_from_utc")
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "trust window is not increasing"
            )


def _as_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class IU4PersistenceWorkerExclusionProofV1(_ContentAddressedArtifact):
    schema_version: int
    artifact_type: str
    worker_exclusion_proof_id: str
    proof_mode: str
    runtime_session_id: str
    runtime_session_open_event_id: str
    runtime_session_open_record_fingerprint: str
    authority_generation_id: str
    authority_commit_anchor: str
    coordinator_id: str
    journal_root_fingerprint: str
    old_worker_id: str
    old_worker_boot_id: str
    old_worker_pid: int
    old_worker_start_time_ns: int
    old_broker_generation_id: int
    old_worker_generation_id: int
    attestor_type: str
    attestor_id: str
    attestor_executable_sha256: str
    collector_id: str
    source_evidence_id: str
    source_evidence_sha256: str
    observed_at_utc: str
    death_evidence_kind: str
    observed_pidfd_id: str
    pidfd_exit_observed: bool
    waitid_reaped: bool
    death_exit_status_class: str
    reap_evidence_fingerprint: str
    death_observation_sequence: int
    worker_append_handle_closed: bool
    surviving_writer_holder_count: int
    append_handle_inventory_fingerprint: str
    proof_fingerprint: str

    ARTIFACT_TYPE = "iu4_persistence_worker_exclusion_proof_v1"
    ID_FIELD = "worker_exclusion_proof_id"
    FINGERPRINT_FIELD = "proof_fingerprint"
    ID_PREFIX = "IU4-PERSISTENCE-WORKER-EXCLUSION-PROOF-V1-"

    def _validate_specific(self) -> None:
        if self.proof_mode != "PROCESS_DEATH" or self.death_evidence_kind != "PIDFD_EXIT_AND_REAP_ATTESTATION":
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "unsupported Worker exclusion mode"
            )
        if self.death_exit_status_class not in {"EXITED", "SIGNALED"}:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "invalid process death class"
            )
        for name in ("old_worker_pid", "old_worker_start_time_ns", "old_worker_generation_id", "death_observation_sequence"):
            _integer(getattr(self, name), name, minimum=1)
        _integer(self.old_broker_generation_id, "old_broker_generation_id")
        for name in ("pidfd_exit_observed", "waitid_reaped", "worker_append_handle_closed"):
            if _boolean(getattr(self, name), name) is not True:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_TERMINAL_GUARDIAN_INVALID", f"{name} must be true"
                )
        if _integer(self.surviving_writer_holder_count, "surviving_writer_holder_count") != 0:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "a Writer append holder survives"
            )
        for name in (
            "runtime_session_open_record_fingerprint", "authority_commit_anchor",
            "journal_root_fingerprint", "attestor_executable_sha256", "source_evidence_sha256",
            "reap_evidence_fingerprint", "append_handle_inventory_fingerprint",
        ):
            _sha(getattr(self, name), name)
        _utc(self.observed_at_utc, "observed_at_utc")


def validate_worker_exclusion(
    *,
    anchor: IU4PersistenceWorkerDeathTrustAnchorV1,
    proof: IU4PersistenceWorkerExclusionProofV1,
    expected_death_trust_anchor_id: str,
    expected_death_trust_anchor_fingerprint: str,
    expected_approval_fingerprint: str,
    expected_trusted_anchor_registry_fingerprint: str,
    runtime_session_id: str,
    runtime_session_open_event_id: str,
    runtime_session_open_record_fingerprint: str,
    authority_generation_id: str,
    authority_commit_anchor: str,
    coordinator_id: str,
    journal_root_fingerprint: str,
    old_worker_id: str,
    old_worker_boot_id: str,
) -> None:
    if type(anchor) is not IU4PersistenceWorkerDeathTrustAnchorV1 or type(proof) is not IU4PersistenceWorkerExclusionProofV1:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "Worker exclusion inputs require exact types"
        )
    expected = (
        anchor.trust_anchor_id,
        anchor.trust_anchor_fingerprint,
        anchor.approval_fingerprint,
        anchor.trusted_anchor_registry_fingerprint,
    )
    supplied = (
        expected_death_trust_anchor_id,
        expected_death_trust_anchor_fingerprint,
        expected_approval_fingerprint,
        expected_trusted_anchor_registry_fingerprint,
    )
    if expected != supplied:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "prebound Worker trust differs"
        )
    if not (_as_datetime(anchor.valid_from_utc) <= _as_datetime(proof.observed_at_utc) <= _as_datetime(anchor.valid_until_utc)):
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "Worker proof is outside its trust window"
        )
    bindings = (
        (proof.attestor_type, anchor.allowed_attestor_type),
        (proof.attestor_id, anchor.trusted_attestor_id),
        (proof.attestor_executable_sha256, anchor.trusted_attestor_executable_sha256),
        (proof.collector_id, anchor.trusted_collector_id),
        (proof.source_evidence_sha256, anchor.trusted_source_evidence_sha256),
        (proof.old_worker_boot_id, anchor.expected_boot_id),
        (proof.runtime_session_id, anchor.expected_runtime_session_id),
        (proof.runtime_session_id, runtime_session_id),
        (proof.runtime_session_open_event_id, runtime_session_open_event_id),
        (proof.runtime_session_open_record_fingerprint, runtime_session_open_record_fingerprint),
        (proof.authority_generation_id, authority_generation_id),
        (proof.authority_commit_anchor, authority_commit_anchor),
        (proof.coordinator_id, coordinator_id),
        (proof.journal_root_fingerprint, journal_root_fingerprint),
        (proof.old_worker_id, old_worker_id),
        (proof.old_worker_boot_id, old_worker_boot_id),
    )
    if any(actual != wanted for actual, wanted in bindings):
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "Worker exclusion binding differs"
        )


@dataclass(frozen=True)
class IU4ProjectionCursorV1(_ContentAddressedArtifact):
    schema_version: int
    artifact_type: str
    projection_cursor_id: str
    authority_generation_id: str
    authority_prepare_record_fingerprint: str
    projection_base_sequence: int
    projection_base_journal_head: str
    projection_base_state_fingerprint: str
    previous_atomic_transaction_sequence: int
    previous_atomic_journal_head: str
    previous_atomic_state_fingerprint: str
    atomic_transaction_event_id: str
    atomic_transaction_fingerprint: str
    atomic_transaction_sequence: int
    atomic_journal_head: str
    atomic_state_fingerprint: str
    projection_id: str
    projection_fingerprint: str
    projection_output_bytes_sha256: str
    previous_projection_cursor_id: str
    previous_projection_cursor_fingerprint: str
    published_at_utc: str
    projection_root_inventory_fingerprint: str
    projection_cursor_fingerprint: str

    ARTIFACT_TYPE = "iu4_projection_cursor_v1"
    ID_FIELD = "projection_cursor_id"
    FINGERPRINT_FIELD = "projection_cursor_fingerprint"
    ID_PREFIX = "IU4-PROJECTION-CURSOR-V1-"

    def _validate_specific(self) -> None:
        base = _integer(self.projection_base_sequence, "projection_base_sequence")
        previous = _integer(self.previous_atomic_transaction_sequence, "previous_atomic_transaction_sequence")
        current = _integer(self.atomic_transaction_sequence, "atomic_transaction_sequence", minimum=1)
        if base != 0 or self.projection_base_journal_head != EMPTY:
            raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "invalid Projection base")
        if current != previous + 1:
            raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "Projection cursor skipped history")
        if current == 1:
            if previous != 0 or self.previous_atomic_journal_head != EMPTY or self.previous_projection_cursor_id != NONE or self.previous_projection_cursor_fingerprint != NONE:
                raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "invalid first Projection link")
        else:
            if self.previous_projection_cursor_id == NONE or self.previous_projection_cursor_fingerprint == NONE:
                raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "missing previous Projection cursor")
            _sha(self.previous_atomic_journal_head, "previous_atomic_journal_head")
            _sha(self.previous_projection_cursor_fingerprint, "previous_projection_cursor_fingerprint")
        for name in (
            "authority_prepare_record_fingerprint", "projection_base_state_fingerprint",
            "previous_atomic_state_fingerprint", "atomic_transaction_fingerprint",
            "atomic_journal_head", "atomic_state_fingerprint", "projection_fingerprint",
            "projection_output_bytes_sha256", "projection_root_inventory_fingerprint",
        ):
            _sha(getattr(self, name), name)
        _utc(self.published_at_utc, "published_at_utc")


def projection_root_realpath_sha256(projection_root_path: str) -> str:
    if type(projection_root_path) is not str:
        raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "projection root must be an exact string")
    return hashlib.sha256(
        b"IU4_PROJECTION_ROOT_V1\x00" + projection_root_path.encode("utf-8", "strict")
    ).hexdigest()


def _minimal_observation_groups() -> dict[str, dict[str, Any]]:
    h = "a" * 64
    role = {
        "parent_guardian_ready": True, "parent_guardian_id": "GUARDIAN-1", "parent_guardian_pid": 11,
        "parent_guardian_start_time_ns": 1, "native_trip_broker_ready": True,
        "native_trip_broker_id": "BROKER-1", "native_trip_broker_pid": 12,
        "native_trip_broker_start_time_ns": 2, "persistence_worker_ready": True,
        "persistence_worker_id": "WORKER-1", "persistence_worker_pid": 13,
        "persistence_worker_start_time_ns": 3, "listener_owner_role": "NATIVE_TRIP_BROKER_V10",
        "worker_ack_receiver_role": "TERMINAL_PERSISTENCE_WORKER_V8",
        "renewal_sender_role": "TRADING_CHILD", "close_approval_sender_role": "PARENT_GUARDIAN_V13",
        "worker_request_sender_role": "TRADING_CHILD",
    }
    lease = {
        "os_lease_type": "PIDFD_KERNEL_SELF_DEATH", "os_lease_identifier": "LEASE-1",
        "credentials_capability_fingerprint": h, "lease_nonce_sha256": h,
        "self_death_timer_armed": True, "self_death_timer_id": "TIMER-1",
        "self_death_timer_clock": "CLOCK_BOOTTIME", "self_death_timer_signal": "SIGKILL",
        "self_death_timer_expiry_monotonic_ns": 1, "native_shim_fingerprint": h,
    }
    pidfd = {
        name: {
            "pidfd_id": f"PIDFD-{name}", "target_pid": pid,
            "target_start_time_ns": start, "sigkill_probe_result": "PASS",
        }
        for name, pid, start in (
            ("trading_self", 10, 10), ("guardian", 11, 1),
            ("broker", 12, 2),
        )
    }
    control = {
        "control_word_schema": 3, "control_word_state": "RUNNING", "trip_sequence": 0,
        "renewal_sequence": 0, "broker_cas_sequence": 0, "memfd_create_flags": ["MFD_CLOEXEC"],
        "initial_seals": ["F_SEAL_SHRINK"], "intermediate_seals": ["F_SEAL_GROW"],
        "final_seals": ["F_SEAL_SEAL"], "trading_mapping_rights": "READ_WRITE",
        "guardian_mapping_rights": "READ_ONLY", "broker_mapping_rights": "READ_WRITE",
        "worker_mapping_rights": "READ_ONLY",
    }
    signal = {
        "signal_envelope_id": "SIGNAL-1", "signal_envelope_fingerprint": h,
        "signal_mask_fingerprint": h, "signal_disposition_fingerprint": h,
        "wait_killable_recv": True, "later_signal_change_locked": True,
    }
    channel = {
        "channel_id": "CHANNEL-1", "direction": "A_TO_B", "sender_role": "TRADING_CHILD",
        "receiver_role": "NATIVE_TRIP_BROKER_V10", "so_peercred": {"pid": 10, "uid": 0, "gid": 0},
        "peer_binding_fingerprint": h, "so_passcred": 0, "so_passrights": 0,
        "receiver_tid": 12, "receiver_files_table_fingerprint": h,
        "receiver_tsync_filter_fingerprint": h, "final_role_filter_fingerprint": h,
        "scm_fds": 0, "control_buffer_bytes": 0, "queue_inventory_fingerprint": h,
        "fd_inventory_fingerprint": h, "fdinfo_inventory_fingerprint": h,
        "ofd_inventory_fingerprint": h, "lock_inventory_fingerprint": h,
        "rights_reject_result": "EPERM",
    }
    channels = {"channel_records": [{**channel, "channel_id": f"CHANNEL-{index}"} for index in range(1, 7)], "guardian_notification_eventfd_id": "EVENTFD-G", "broker_notification_eventfd_id": "EVENTFD-B"}
    seccomp = {
        "seccomp_listener_id": "LISTENER-1", "seccomp_notification_id": "NOTIFY-1",
        "seccomp_listener_owner": "NATIVE_TRIP_BROKER_V10", "seccomp_listener_receive_error_status": "NONE",
        "seccomp_filter_hash": h, "btf_id": "BTF-1", "program_ids": ["P-1"], "map_ids": ["M-1"],
        "link_ids": ["L-1"], "pin_paths": ["/synthetic/pin"], "cgroup_ids": ["C-1"],
        "lsm_hook_coverage": ["file_open", "file_permission", "socket_connect", "socket_sendmsg", "task_kill", "bprm_check_security"],
        "socket_cookie_tag_inventory_fingerprint": h, "phase_map_frozen": True, "config_map_frozen": True,
        "bpf_cmpxchg_proof_fingerprint": h, "scalar_seccomp_userspace_authority_matrix": [],
        "scalar_seccomp_userspace_authority_matrix_fingerprint": h, "capability_envelope_fingerprint": h,
    }
    close = {
        "channel_phase": "OPEN_DURABLE_GRANTED", "close_fsm_phase": "OPEN",
        "close_prepare_event_id": NONE, "broker_closed_evidence_id": NONE, "close_commit_event_id": NONE,
        "close_peer_status": "NONE", "close_hup_status": "NONE", "close_timeout_status": "NONE",
        "request_owner_role": "TRADING_CHILD", "ack_owner_role": "TERMINAL_PERSISTENCE_WORKER_V8",
    }
    heartbeat = {
        "heartbeat_interval_ms": 10, "heartbeat_last_sequence": 1, "heartbeat_age_ms": 0,
        "capability_probe_age_ms": 0, "capability_probe_expiry_ms": 25, "clock_source": "CLOCK_BOOTTIME",
        "terminal_guardian_lease_max_ms": 25, "terminal_broker_trip_cas_max_ms": 5,
        "terminal_guardian_trip_dispatch_max_ms": 5, "terminal_kernel_signal_generation_budget_ms": 25,
        "terminal_failstop_max_ms": 100, "termination_latch_deadline_ms": 1,
    }
    failstop = {
        "failstop_asserted": False, "pending_signal_status": "NONE", "reap_status": "NONE",
        "runtime_session_unclean": False, "terminal_gap_status": "NONE",
        "liveness_pipe_read_endpoint_id": "PIPE-R", "liveness_pipe_write_endpoint_id": "PIPE-W",
        "liveness_pipe_inode": 1, "liveness_pipe_capacity_bytes": 4096,
        "liveness_pipe_exclusive_owner_role": "PARENT_GUARDIAN_V13", "liveness_pipe_write_forbidden": True,
        "liveness_pipe_payload_bytes": 0, "liveness_pipe_empty": True,
        "liveness_pipe_hup_status": "NOT_OBSERVED", "liveness_pipe_fallback_status": "NOT_REQUIRED",
    }
    completion = {
        "completion_provenance": "DIRECT", "completion_authorization_id": NONE,
        "completion_consumption_event_id": NONE, "completion_startup_attempt_id": NONE,
        "direct_process_instance_id": "PROCESS-1", "genesis_operation_attempt_id": "GENESIS-1",
        "direct_continuation_nonce_hash": h, "direct_continuation_nonce_preimage_match": True,
        "prior_runtime_session_count": 0, "direct_first_start_eligible": True,
    }
    safety = {
        "kill_level": "NONE", "entry_allowed": True, "exit_evaluation_allowed": True,
        "runtime_directive": "CONTINUE", "reason_codes": [], "activation_authorization_valid": True,
        "restart_authorization_status": "NOT_REQUIRED", "profile_binding_status": "MATCH",
        "resource_reserve_status": "PASS", "io_status": "PASS", "atomic_schema_version": 2,
        "lifecycle_schema_version": 1, "projection_schema_version": 1,
        "legacy_exit_only_status": "NOT_APPLICABLE",
    }
    return {
        "role_readiness": role, "lease_and_self_death": lease, "pidfd_targets": pidfd,
        "control_word_and_memfd": control, "signal_envelope": signal, "runtime_channels": channels,
        "seccomp_lsm_capability": seccomp, "runtime_close_fsm": close,
        "heartbeat_and_budgets": heartbeat, "failstop_and_terminal_gap": failstop,
        "completion_provenance": completion, "safety_resource_schema": safety,
    }


def _validate_exact_shape(value: Any, template: Any, name: str) -> None:
    if type(template) is dict:
        if type(value) is not dict or set(value) != set(template):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", f"invalid nested fields in {name}"
            )
        for key in template:
            _validate_exact_shape(value[key], template[key], f"{name}.{key}")
        return
    if type(template) is list:
        if type(value) is not list or len(value) != len(template):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", f"invalid array in {name}"
            )
        if template:
            for item in value:
                _validate_exact_shape(item, template[0], f"{name}[]")
        return
    if type(value) is not type(template):
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_GUARDIAN_INVALID", f"invalid primitive type in {name}"
        )


OBSERVATION_GROUPS = tuple(_minimal_observation_groups())


@dataclass(frozen=True)
class IU4TerminalMonitoringObservationV1(_ContentAddressedArtifact):
    schema_version: int
    artifact_type: str
    terminal_monitoring_observation_id: str
    runtime_session_id: str
    runtime_session_open_record_fingerprint: str
    authority_generation_id: str
    authority_commit_anchor: str
    atomic_root_fingerprint: str
    source_collector_id: str
    source_evidence_id: str
    source_evidence_sha256: str
    observation_sequence: int
    observed_at_utc: str
    role_readiness: dict[str, Any]
    lease_and_self_death: dict[str, Any]
    pidfd_targets: dict[str, Any]
    control_word_and_memfd: dict[str, Any]
    signal_envelope: dict[str, Any]
    runtime_channels: dict[str, Any]
    seccomp_lsm_capability: dict[str, Any]
    runtime_close_fsm: dict[str, Any]
    heartbeat_and_budgets: dict[str, Any]
    failstop_and_terminal_gap: dict[str, Any]
    completion_provenance: dict[str, Any]
    safety_resource_schema: dict[str, Any]
    observation_fingerprint: str

    ARTIFACT_TYPE = "iu4_terminal_monitoring_observation_v1"
    ID_FIELD = "terminal_monitoring_observation_id"
    FINGERPRINT_FIELD = "observation_fingerprint"
    ID_PREFIX = "IU4-TERMINAL-MONITORING-OBSERVATION-V1-"

    @classmethod
    def build_minimal_pass(cls, **values: Any):
        values.update(_minimal_observation_groups())
        return cls.build(**values)

    def _validate_specific(self) -> None:
        if self.runtime_session_id == NONE:
            if self.runtime_session_open_record_fingerprint != NONE:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RUNTIME_SESSION_UNCLEAN", "mixed absent Observation Session pair"
                )
        else:
            _text(self.runtime_session_id, "runtime_session_id")
            _sha(self.runtime_session_open_record_fingerprint, "runtime_session_open_record_fingerprint")
        _sha(self.authority_commit_anchor, "authority_commit_anchor")
        _sha(self.atomic_root_fingerprint, "atomic_root_fingerprint")
        _sha(self.source_evidence_sha256, "source_evidence_sha256")
        for name in (
            "authority_generation_id", "source_collector_id", "source_evidence_id"
        ):
            _text(getattr(self, name), name)
        _integer(self.observation_sequence, "observation_sequence")
        _utc(self.observed_at_utc, "observed_at_utc")
        expected = _minimal_observation_groups()
        for name in OBSERVATION_GROUPS:
            value = getattr(self, name)
            if type(value) is not dict or set(value) != set(expected[name]):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_TERMINAL_GUARDIAN_INVALID", f"invalid terminal group {name}"
                )
            _validate_exact_shape(value, expected[name], name)
            _validate_identifier_tree(value, name)
        _validate_observation_groups(self)


_CLOSE_FIELDS = frozenset(_minimal_observation_groups()["runtime_close_fsm"])


def _classify_runtime_close_fsm(
    close: dict[str, Any], runtime_session_status: str | None,
) -> tuple[str, str]:
    if type(close) is not dict or set(close) != _CLOSE_FIELDS:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "invalid Runtime Close record"
        )

    def enum(value: Any, allowed: set[str], name: str) -> str:
        if type(value) is not str or value not in allowed:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", f"unknown {name} enum"
            )
        return value

    enum(close["channel_phase"], {
        "LISTENER_HANDOFF", "LISTENER_RECEIVED", "HANDOFF_REVOKED_GRANTED",
        "BOOTSTRAP", "OPEN_DURABLE_GRANTED", "RELEASED",
    }, "channel_phase")
    phase = enum(close["close_fsm_phase"], {
        "OPEN", "CLOSING", "PREPARE", "BROKER_CLOSED", "COMMIT",
        "COMMITTED", "FAILED",
    }, "close_fsm_phase")
    for name in ("close_peer_status", "close_hup_status", "close_timeout_status"):
        enum(close[name], {"NONE", "OK", "HUP", "TIMEOUT", "ERROR"}, name)
    identifiers = tuple(close[name] for name in (
        "close_prepare_event_id", "broker_closed_evidence_id",
        "close_commit_event_id",
    ))
    statuses = tuple(close[name] for name in (
        "close_peer_status", "close_hup_status", "close_timeout_status",
    ))
    identifier_presence = tuple(value != NONE for value in identifiers)
    expected_identifiers = {
        "OPEN": (False, False, False),
        "CLOSING": (False, False, False),
        "PREPARE": (True, False, False),
        "BROKER_CLOSED": (True, True, False),
        "COMMIT": (True, True, True),
        "COMMITTED": (True, True, True),
    }
    success_statuses = {
        "OPEN": (NONE, NONE, NONE),
        "CLOSING": (NONE, NONE, NONE),
        "PREPARE": (NONE, NONE, NONE),
        "BROKER_CLOSED": ("OK", "HUP", NONE),
        "COMMIT": ("OK", "HUP", NONE),
        "COMMITTED": ("OK", "HUP", NONE),
    }
    owners_ok = (
        close["request_owner_role"] == "TRADING_CHILD"
        and close["ack_owner_role"] == "TERMINAL_PERSISTENCE_WORKER_V8"
    )
    if phase != "FAILED":
        identifiers_ok = identifier_presence == expected_identifiers[phase]
        status_ok = statuses == success_statuses[phase]
        expected_channel = "RELEASED" if phase == "COMMITTED" else "OPEN_DURABLE_GRANTED"
        expected_session = "CLOSED_CLEAN" if phase == "COMMITTED" else "OPEN_CLEAN"
        session_ok = runtime_session_status in {None, expected_session}
        valid = (
            identifiers_ok and status_ok and owners_ok
            and close["channel_phase"] == expected_channel and session_ok
        )
        if valid:
            return "PASS", NONE
        reason = (
            "PEE_IU4_RUNTIME_SESSION_CLOSE_INCOMPLETE"
            if not identifiers_ok
            else "PEE_IU4_RUNTIME_SESSION_CLOSE_PROTOCOL_INVALID"
        )
        return "FAIL", reason

    allowed_failure_statuses = {
        (False, False, False): {
            ("ERROR", NONE, NONE), (NONE, NONE, "TIMEOUT"),
        },
        (True, False, False): {
            ("ERROR", NONE, NONE), ("OK", "ERROR", NONE),
            (NONE, NONE, "TIMEOUT"), ("OK", NONE, "TIMEOUT"),
        },
        (True, True, False): {
            ("ERROR", NONE, NONE), ("OK", "ERROR", NONE),
            (NONE, NONE, "TIMEOUT"), ("OK", NONE, "TIMEOUT"),
        },
        (True, True, True): {
            ("ERROR", NONE, NONE), ("OK", "ERROR", NONE),
            (NONE, NONE, "TIMEOUT"), ("OK", NONE, "TIMEOUT"),
        },
    }
    status_ok = statuses in allowed_failure_statuses.get(identifier_presence, set())
    allowed_session_channels = {
        (False, False, False): {("OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN")},
        (True, False, False): {("OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN")},
        (True, True, False): {("RELEASED", "CLOSED_UNCLEAN")},
        (True, True, True): {
            ("OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN"),
            ("RELEASED", "CLOSED_UNCLEAN"),
        },
    }
    if runtime_session_status is None:
        session_channel_ok = any(
            channel == close["channel_phase"]
            for channel, _session in allowed_session_channels.get(
                identifier_presence, set()
            )
        )
    else:
        session_channel_ok = (
            close["channel_phase"], runtime_session_status
        ) in allowed_session_channels.get(identifier_presence, set())
    valid = status_ok and session_channel_ok and owners_ok
    if valid:
        reason = (
            "PEE_IU4_RUNTIME_SESSION_CLOSE_TIMEOUT"
            if statuses[2] == "TIMEOUT"
            else "PEE_IU4_RUNTIME_SESSION_CLOSE_TRANSPORT_FAILED"
        )
        return "PASS", reason
    if identifier_presence not in allowed_failure_statuses:
        return "FAIL", "PEE_IU4_RUNTIME_SESSION_CLOSE_INCOMPLETE"
    return "FAIL", "PEE_IU4_RUNTIME_SESSION_CLOSE_PROTOCOL_INVALID"


def _validate_observation_groups(
    observation: IU4TerminalMonitoringObservationV1,
    *,
    runtime_session_status: str | None = None,
) -> tuple[str, ...]:
    def enum(value: Any, allowed: set[str], name: str) -> str:
        if type(value) is not str or value not in allowed:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_GUARDIAN_INVALID", f"unknown {name} enum"
            )
        return value

    results: list[str] = []
    role = observation.role_readiness
    roles = {"PARENT_GUARDIAN_V13", "NATIVE_TRIP_BROKER_V10", "TERMINAL_PERSISTENCE_WORKER_V8", "TRADING_CHILD"}
    for name in ("listener_owner_role", "worker_ack_receiver_role", "renewal_sender_role", "close_approval_sender_role", "worker_request_sender_role"):
        enum(role[name], roles, name)
    for prefix in ("parent_guardian", "native_trip_broker", "persistence_worker"):
        _integer(role[f"{prefix}_pid"], f"{prefix}_pid", minimum=1)
        _integer(role[f"{prefix}_start_time_ns"], f"{prefix}_start_time_ns", minimum=1)
    role_owners_ok = (
        role["listener_owner_role"] == "NATIVE_TRIP_BROKER_V10"
        and role["worker_ack_receiver_role"] == "TERMINAL_PERSISTENCE_WORKER_V8"
        and role["renewal_sender_role"] == "TRADING_CHILD"
        and role["close_approval_sender_role"] == "PARENT_GUARDIAN_V13"
        and role["worker_request_sender_role"] == "TRADING_CHILD"
    )
    results.append("PASS" if role_owners_ok and all(role[name] is True for name in ("parent_guardian_ready", "native_trip_broker_ready", "persistence_worker_ready")) else "FAIL")
    lease = observation.lease_and_self_death
    enum(lease["os_lease_type"], {"PIDFD_KERNEL_SELF_DEATH"}, "os_lease_type")
    enum(lease["self_death_timer_clock"], {"CLOCK_BOOTTIME"}, "self_death_timer_clock")
    enum(lease["self_death_timer_signal"], {"SIGKILL"}, "self_death_timer_signal")
    _integer(lease["self_death_timer_expiry_monotonic_ns"], "self_death_timer_expiry_monotonic_ns", minimum=1)
    results.append("PASS" if lease["os_lease_type"] == "PIDFD_KERNEL_SELF_DEATH" and lease["self_death_timer_armed"] is True and lease["self_death_timer_clock"] == "CLOCK_BOOTTIME" and lease["self_death_timer_signal"] == "SIGKILL" else "FAIL")
    pidfd = observation.pidfd_targets
    for name in ("trading_self", "guardian", "broker"):
        _integer(pidfd[name]["target_pid"], f"{name}.target_pid", minimum=1)
        _integer(pidfd[name]["target_start_time_ns"], f"{name}.target_start_time_ns", minimum=1)
        enum(pidfd[name]["sigkill_probe_result"], {"PASS", "FAIL"}, f"{name}.sigkill_probe_result")
    pidfd_bindings_ok = (
        pidfd["guardian"]["target_pid"] == role["parent_guardian_pid"]
        and pidfd["guardian"]["target_start_time_ns"]
        == role["parent_guardian_start_time_ns"]
        and pidfd["broker"]["target_pid"] == role["native_trip_broker_pid"]
        and pidfd["broker"]["target_start_time_ns"]
        == role["native_trip_broker_start_time_ns"]
    )
    results.append("PASS" if pidfd_bindings_ok and all(type(pidfd[name]) is dict and pidfd[name]["sigkill_probe_result"] == "PASS" for name in ("trading_self", "guardian", "broker")) else "FAIL")
    control = observation.control_word_and_memfd
    enum(control["control_word_state"], {"RUNNING", "CLOSING", "TERMINATING", "CLOSED"}, "control_word_state")
    for name in ("trading_mapping_rights", "guardian_mapping_rights", "broker_mapping_rights", "worker_mapping_rights"):
        enum(control[name], {"NONE", "READ_ONLY", "READ_WRITE"}, name)
    for name in ("trip_sequence", "renewal_sequence", "broker_cas_sequence"):
        _integer(control[name], name)
    control_static_ok = (
        control["memfd_create_flags"] == ["MFD_CLOEXEC"]
        and control["initial_seals"] == ["F_SEAL_SHRINK"]
        and control["intermediate_seals"] == ["F_SEAL_GROW"]
        and control["final_seals"] == ["F_SEAL_SEAL"]
        and control["trading_mapping_rights"] == "READ_WRITE"
        and control["guardian_mapping_rights"] == "READ_ONLY"
        and control["broker_mapping_rights"] == "READ_WRITE"
        and control["worker_mapping_rights"] == "READ_ONLY"
    )
    results.append("PASS" if type(control["control_word_schema"]) is int and control["control_word_schema"] == 3 and control["control_word_state"] in {"RUNNING", "CLOSING", "TERMINATING", "CLOSED"} and control["broker_cas_sequence"] <= control["trip_sequence"] and control_static_ok else "FAIL")
    signal = observation.signal_envelope
    results.append("PASS" if signal["wait_killable_recv"] is True and signal["later_signal_change_locked"] is True else "FAIL")
    channels = observation.runtime_channels
    for index, record in enumerate(channels["channel_records"]):
        enum(record["direction"], {"A_TO_B", "B_TO_A"}, f"channel[{index}].direction")
        enum(record["sender_role"], roles, f"channel[{index}].sender_role")
        enum(record["receiver_role"], roles, f"channel[{index}].receiver_role")
        enum(record["rights_reject_result"], {"EPERM"}, f"channel[{index}].rights_reject_result")
        for name in ("pid",):
            _integer(record["so_peercred"][name], f"channel[{index}].so_peercred.{name}", minimum=1)
        for name in ("uid", "gid"):
            _integer(record["so_peercred"][name], f"channel[{index}].so_peercred.{name}")
    channel_ok = type(channels["channel_records"]) is list and len(channels["channel_records"]) == 6 and all(record["so_passcred"] == record["so_passrights"] == record["scm_fds"] == record["control_buffer_bytes"] == 0 and record["rights_reject_result"] == "EPERM" for record in channels["channel_records"])
    results.append("PASS" if channel_ok else "FAIL")
    seccomp = observation.seccomp_lsm_capability
    enum(seccomp["seccomp_listener_owner"], {"NATIVE_TRIP_BROKER_V10"}, "seccomp_listener_owner")
    enum(seccomp["seccomp_listener_receive_error_status"], {"NONE", "EINTR_RETRIED", "FATAL"}, "seccomp_listener_receive_error_status")
    expected_lsm_hooks = [
        "file_open", "file_permission", "socket_connect", "socket_sendmsg",
        "task_kill", "bprm_check_security",
    ]
    results.append("PASS" if seccomp["seccomp_listener_owner"] == "NATIVE_TRIP_BROKER_V10" and seccomp["seccomp_listener_receive_error_status"] == "NONE" and seccomp["phase_map_frozen"] is True and seccomp["config_map_frozen"] is True and seccomp["lsm_hook_coverage"] == expected_lsm_hooks else "FAIL")
    close_result, _close_reason = _classify_runtime_close_fsm(
        observation.runtime_close_fsm, runtime_session_status
    )
    results.append(close_result)
    budget = observation.heartbeat_and_budgets
    for name in ("heartbeat_interval_ms", "heartbeat_last_sequence", "heartbeat_age_ms", "capability_probe_age_ms", "capability_probe_expiry_ms", "terminal_guardian_lease_max_ms", "terminal_broker_trip_cas_max_ms", "terminal_guardian_trip_dispatch_max_ms", "terminal_kernel_signal_generation_budget_ms", "terminal_failstop_max_ms", "termination_latch_deadline_ms"):
        _integer(budget[name], name)
    enum(budget["clock_source"], {"CLOCK_BOOTTIME"}, "clock_source")
    budget_ok = budget == {**budget, "heartbeat_interval_ms": 10} and 0 <= budget["heartbeat_age_ms"] <= 25 and 0 <= budget["capability_probe_age_ms"] <= 25 and 0 <= budget["capability_probe_expiry_ms"] <= 25 and budget["terminal_guardian_lease_max_ms"] == 25 and budget["terminal_broker_trip_cas_max_ms"] == 5 and budget["terminal_guardian_trip_dispatch_max_ms"] == 5 and budget["terminal_kernel_signal_generation_budget_ms"] == 25 and budget["terminal_failstop_max_ms"] == 100 and 1 <= budget["termination_latch_deadline_ms"] <= 100
    results.append("PASS" if budget_ok else "FAIL")
    failstop = observation.failstop_and_terminal_gap
    for name in ("pending_signal_status", "reap_status", "terminal_gap_status"):
        enum(failstop[name], {"NONE", "PENDING", "COMPLETE", "FAILED"}, name)
    enum(failstop["liveness_pipe_hup_status"], {"OBSERVED", "NOT_OBSERVED"}, "liveness_pipe_hup_status")
    enum(failstop["liveness_pipe_fallback_status"], {"NOT_REQUIRED", "ARMED", "TRIPPED", "FAILED"}, "liveness_pipe_fallback_status")
    _integer(failstop["liveness_pipe_inode"], "liveness_pipe_inode", minimum=1)
    _integer(failstop["liveness_pipe_capacity_bytes"], "liveness_pipe_capacity_bytes", minimum=1)
    failstop_clean = (
        failstop["failstop_asserted"] is False
        and failstop["pending_signal_status"] == "NONE"
        and failstop["reap_status"] == "NONE"
        and failstop["terminal_gap_status"] == "NONE"
        and failstop["liveness_pipe_hup_status"] == "NOT_OBSERVED"
        and failstop["liveness_pipe_fallback_status"] == "NOT_REQUIRED"
    )
    results.append("PASS" if failstop_clean and failstop["liveness_pipe_write_forbidden"] is True and failstop["liveness_pipe_payload_bytes"] == 0 and failstop["liveness_pipe_empty"] is True and failstop["runtime_session_unclean"] is False else "FAIL")
    completion = observation.completion_provenance
    enum(completion["completion_provenance"], {"DIRECT", "RECOVERED_AFTER_PREPARE"}, "completion_provenance")
    _integer(completion["prior_runtime_session_count"], "prior_runtime_session_count")
    direct_ok = completion["completion_provenance"] == "DIRECT" and all(completion[name] == NONE for name in ("completion_authorization_id", "completion_consumption_event_id", "completion_startup_attempt_id")) and completion["direct_continuation_nonce_preimage_match"] is True and completion["prior_runtime_session_count"] == 0 and completion["direct_first_start_eligible"] is True
    recovered_ok = (
        completion["completion_provenance"] == "RECOVERED_AFTER_PREPARE"
        and all(completion[name] != NONE for name in (
            "completion_authorization_id", "completion_consumption_event_id",
            "completion_startup_attempt_id",
        ))
        and all(completion[name] == NONE for name in (
            "direct_process_instance_id", "genesis_operation_attempt_id",
            "direct_continuation_nonce_hash",
        ))
        and completion["direct_continuation_nonce_preimage_match"] is False
        and completion["direct_first_start_eligible"] is False
    )
    results.append("PASS" if direct_ok or recovered_ok else "FAIL")
    safety = observation.safety_resource_schema
    level = safety["kill_level"]
    enum(level, {"NONE", "SOFT", "HARD", "EMERGENCY"}, "kill_level")
    enum(safety["runtime_directive"], {"CONTINUE", "STOP_LOOP", "EXIT_PROCESS"}, "runtime_directive")
    enum(safety["restart_authorization_status"], {"NOT_REQUIRED", "VALID", "MISSING", "CONSUMED", "MISMATCH"}, "restart_authorization_status")
    enum(safety["profile_binding_status"], {"MATCH", "MISMATCH", "MISSING", "UNKNOWN_SCHEMA"}, "profile_binding_status")
    enum(safety["resource_reserve_status"], {"PASS", "EXHAUSTED", "BELOW_MINIMUM", "UNKNOWN"}, "resource_reserve_status")
    enum(safety["io_status"], {"PASS", "READ_ERROR", "WRITE_ERROR", "SYNC_ERROR", "PERMISSION_DENIED", "UNKNOWN"}, "io_status")
    enum(safety["legacy_exit_only_status"], {"NOT_APPLICABLE", "REQUIRED", "ACTIVE", "COMPLETE", "INVALID"}, "legacy_exit_only_status")
    expected_entry = level == "NONE"
    expected_exit = level in {"NONE", "SOFT"}
    expected_directive = {"NONE": "CONTINUE", "SOFT": "CONTINUE", "HARD": "STOP_LOOP", "EMERGENCY": "EXIT_PROCESS"}.get(level)
    safety_ok = expected_directive is not None and safety["entry_allowed"] is expected_entry and safety["exit_evaluation_allowed"] is expected_exit and safety["runtime_directive"] == expected_directive and safety["activation_authorization_valid"] is True and safety["restart_authorization_status"] in {"NOT_REQUIRED", "VALID"} and safety["profile_binding_status"] == "MATCH" and safety["resource_reserve_status"] == "PASS" and safety["io_status"] == "PASS" and (safety["atomic_schema_version"], safety["lifecycle_schema_version"], safety["projection_schema_version"]) == (2, 1, 1) and safety["legacy_exit_only_status"] in {"NOT_APPLICABLE", "COMPLETE", "REQUIRED", "ACTIVE"}
    results.append("WARN" if safety_ok and safety["legacy_exit_only_status"] in {"REQUIRED", "ACTIVE"} else "PASS" if safety_ok else "FAIL")
    return tuple(results)


def terminal_static_bindings_fingerprint(
    observation: IU4TerminalMonitoringObservationV1,
) -> str:
    """Fingerprint the OPEN/profile-owned, non-dynamic Observation fields."""

    if type(observation) is not IU4TerminalMonitoringObservationV1:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_GUARDIAN_INVALID",
            "terminal bindings require exact Observation",
        )
    groups = observation.to_record()
    role = {
        key: value for key, value in groups["role_readiness"].items()
        if not key.endswith("_ready")
    }
    lease = {
        key: value for key, value in groups["lease_and_self_death"].items()
        if key != "self_death_timer_armed"
    }
    pidfd = {
        name: {
            key: value for key, value in record.items()
            if key != "sigkill_probe_result"
        }
        for name, record in groups["pidfd_targets"].items()
    }
    control = {
        key: value for key, value in groups["control_word_and_memfd"].items()
        if key not in {
            "control_word_state", "trip_sequence", "renewal_sequence",
            "broker_cas_sequence",
        }
    }
    signal = {
        key: value for key, value in groups["signal_envelope"].items()
        if key not in {"wait_killable_recv", "later_signal_change_locked"}
    }
    channels = {
        "guardian_notification_eventfd_id": groups["runtime_channels"]["guardian_notification_eventfd_id"],
        "broker_notification_eventfd_id": groups["runtime_channels"]["broker_notification_eventfd_id"],
        "channel_records": [
            {
                key: value for key, value in record.items()
                if key not in {
                    "so_passcred", "so_passrights", "scm_fds",
                    "control_buffer_bytes", "rights_reject_result",
                }
            }
            for record in groups["runtime_channels"]["channel_records"]
        ],
    }
    seccomp = {
        key: value for key, value in groups["seccomp_lsm_capability"].items()
        if key not in {
            "seccomp_listener_receive_error_status", "phase_map_frozen",
            "config_map_frozen",
        }
    }
    close = {
        key: groups["runtime_close_fsm"][key]
        for key in ("request_owner_role", "ack_owner_role")
    }
    heartbeat = {
        key: value for key, value in groups["heartbeat_and_budgets"].items()
        if key not in {
            "heartbeat_last_sequence", "heartbeat_age_ms",
            "capability_probe_age_ms", "capability_probe_expiry_ms",
            "termination_latch_deadline_ms",
        }
    }
    liveness = {
        key: value for key, value in groups["failstop_and_terminal_gap"].items()
        if key in {
            "liveness_pipe_read_endpoint_id", "liveness_pipe_write_endpoint_id",
            "liveness_pipe_inode", "liveness_pipe_capacity_bytes",
            "liveness_pipe_exclusive_owner_role",
        }
    }
    return _hash({
        "schema_version": 1,
        "role_readiness": role,
        "lease_and_self_death": lease,
        "pidfd_targets": pidfd,
        "control_word_and_memfd": control,
        "signal_envelope": signal,
        "runtime_channels": channels,
        "seccomp_lsm_capability": seccomp,
        "runtime_close_fsm": close,
        "heartbeat_and_budgets": heartbeat,
        "failstop_and_terminal_gap": liveness,
        "completion_provenance": {
            key: groups["completion_provenance"][key]
            for key in (
                "completion_provenance", "completion_authorization_id",
                "completion_consumption_event_id",
                "completion_startup_attempt_id", "direct_process_instance_id",
                "genesis_operation_attempt_id",
                "direct_continuation_nonce_hash",
            )
        },
        "safety_schema_versions": {
            key: groups["safety_resource_schema"][key]
            for key in (
                "atomic_schema_version", "lifecycle_schema_version",
                "projection_schema_version",
            )
        },
    })


@dataclass(frozen=True)
class IU4TerminalRuntimeProfileAnchorV1(_ContentAddressedArtifact):
    """Content-addressed binding from a profile ID to accepted static bytes."""

    schema_version: int
    artifact_type: str
    profile_anchor_id: str
    runtime_profile_id: str
    terminal_static_bindings_fingerprint: str
    profile_anchor_fingerprint: str

    ARTIFACT_TYPE = "iu4_terminal_runtime_profile_anchor_v1"
    ID_FIELD = "profile_anchor_id"
    FINGERPRINT_FIELD = "profile_anchor_fingerprint"
    ID_PREFIX = "IU4-TERMINAL-RUNTIME-PROFILE-ANCHOR-V1-"

    def _validate_specific(self) -> None:
        _text(self.runtime_profile_id, "runtime_profile_id")
        _sha(
            self.terminal_static_bindings_fingerprint,
            "terminal_static_bindings_fingerprint",
        )


@dataclass(frozen=True)
class IU4TerminalRuntimeProfileRegistryV1(_ContentAddressedArtifact):
    """Immutable untrusted registry transport; it cannot authorize a PASS."""

    schema_version: int
    artifact_type: str
    profile_registry_id: str
    profile_anchors: tuple[IU4TerminalRuntimeProfileAnchorV1, ...]
    profile_registry_fingerprint: str

    ARTIFACT_TYPE = "iu4_terminal_runtime_profile_registry_v1"
    ID_FIELD = "profile_registry_id"
    FINGERPRINT_FIELD = "profile_registry_fingerprint"
    ID_PREFIX = "IU4-TERMINAL-RUNTIME-PROFILE-REGISTRY-V1-"
    @classmethod
    def from_anchors(
        cls, anchors: tuple[IU4TerminalRuntimeProfileAnchorV1, ...]
    ) -> "IU4TerminalRuntimeProfileRegistryV1":
        if type(anchors) is not tuple or not anchors or any(
            type(anchor) is not IU4TerminalRuntimeProfileAnchorV1
            for anchor in anchors
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry requires exact profile anchors",
            )
        for anchor in anchors:
            cls._revalidate_anchor(anchor)
        return cls.build(profile_anchors=anchors)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]):
        names = {field.name for field in fields(cls)}
        if type(record) is not dict or set(record) != names:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry fields are missing or unknown",
            )
        serialized = record.get("profile_anchors")
        if type(serialized) is not list:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile anchors are not a canonical array",
            )
        try:
            anchors = tuple(
                IU4TerminalRuntimeProfileAnchorV1.from_record(item)
                for item in serialized
            )
            value = cls(
                **{
                    **record,
                    "profile_anchors": anchors,
                }
            )
        except (TypeError, IU4RecoveryProjectionError) as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry contains an invalid anchor",
            ) from exc
        if value.to_record() != record:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry record is not canonical",
            )
        return value

    @staticmethod
    def _revalidate_anchor(
        anchor: IU4TerminalRuntimeProfileAnchorV1,
    ) -> bytes:
        if type(anchor) is not IU4TerminalRuntimeProfileAnchorV1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry contains a non-exact anchor",
            )
        try:
            anchor.__post_init__()
            canonical = canonical_json_bytes(anchor.to_record())
        except IU4RecoveryProjectionError as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry contains an invalid anchor",
            ) from exc
        if IU4TerminalRuntimeProfileAnchorV1.from_record(
            json.loads(canonical.decode("ascii"))
        ) != anchor:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile anchor canonical bytes differ",
            )
        return canonical

    def _validated_anchors(self) -> tuple[IU4TerminalRuntimeProfileAnchorV1, ...]:
        anchors: list[IU4TerminalRuntimeProfileAnchorV1] = []
        by_profile_id: dict[str, bytes] = {}
        for anchor in self.profile_anchors:
            canonical = self._revalidate_anchor(anchor)
            prior = by_profile_id.get(anchor.runtime_profile_id)
            if prior is not None and prior != canonical:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                    "same runtime profile ID has divergent anchored bytes",
                )
            if prior is not None:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                    "runtime profile ID is duplicated",
                )
            by_profile_id[anchor.runtime_profile_id] = canonical
            anchors.append(anchor)
        if not anchors:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry is empty",
            )
        return tuple(anchors)

    def _validate_specific(self) -> None:
        if type(self.profile_anchors) is not tuple or any(
            type(anchor) is not IU4TerminalRuntimeProfileAnchorV1
            for anchor in self.profile_anchors
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile anchors are not an exact deeply immutable tuple",
            )
        self._validated_anchors()

    def _revalidate_registry_binding(self) -> None:
        if type(self) is not IU4TerminalRuntimeProfileRegistryV1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry is not exact type",
            )
        try:
            self.__post_init__()
        except IU4RecoveryProjectionError as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "profile registry content-addressed binding differs",
            ) from exc

    def resolve(
        self, runtime_profile_id: str
    ) -> IU4TerminalRuntimeProfileAnchorV1:
        requested = _text(runtime_profile_id, "runtime_profile_id")
        self._revalidate_registry_binding()
        matches = tuple(
            anchor
            for anchor in self._validated_anchors()
            if anchor.runtime_profile_id == requested
        )
        if len(matches) != 1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "runtime profile has no unique trusted anchor",
            )
        return matches[0]


@dataclass(frozen=True)
class _IU4TerminalRuntimeProfileTrustRootV1(_ContentAddressedArtifact):
    """Private frozen provisioning root, independent of report-caller facts."""

    schema_version: int
    artifact_type: str
    trust_root_id: str
    provisioning_authority_id: str
    provisioning_authority_fingerprint: str
    profile_registry: IU4TerminalRuntimeProfileRegistryV1
    trust_root_fingerprint: str

    ARTIFACT_TYPE = "iu4_terminal_runtime_profile_trust_root_v1"
    ID_FIELD = "trust_root_id"
    FINGERPRINT_FIELD = "trust_root_fingerprint"
    ID_PREFIX = "IU4-TERMINAL-RUNTIME-PROFILE-TRUST-ROOT-V1-"

    def _validate_specific(self) -> None:
        _text(self.provisioning_authority_id, "provisioning_authority_id")
        _sha(
            self.provisioning_authority_fingerprint,
            "provisioning_authority_fingerprint",
        )
        if type(self.profile_registry) is not IU4TerminalRuntimeProfileRegistryV1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "provisioned profile registry is not exact type",
            )
        self.profile_registry._revalidate_registry_binding()

    def resolve(
        self, runtime_profile_id: str,
    ) -> tuple[
        IU4TerminalRuntimeProfileRegistryV1,
        IU4TerminalRuntimeProfileAnchorV1,
    ]:
        if type(self) is not _IU4TerminalRuntimeProfileTrustRootV1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "runtime profile trust root is not exact type",
            )
        try:
            self.__post_init__()
        except IU4RecoveryProjectionError as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "runtime profile trust root binding differs",
            ) from exc
        return self.profile_registry, self.profile_registry.resolve(
            runtime_profile_id
        )


REPORT_GROUP_RESULT_FIELDS = (
    "role_readiness_result", "lease_and_self_death_result", "pidfd_targets_result",
    "control_word_and_memfd_result", "signal_envelope_result", "runtime_channels_result",
    "seccomp_lsm_capability_result", "runtime_close_fsm_result",
    "heartbeat_and_budgets_result", "failstop_and_terminal_gap_result",
    "completion_provenance_result", "safety_resource_schema_result",
)
REPORT_GROUP_REASON_CODES = (
    "PEE_IU4_TERMINAL_GUARDIAN_INVALID",
    "PEE_IU4_TERMINAL_GUARDIAN_INVALID",
    "PEE_IU4_TERMINAL_GUARDIAN_INVALID",
    "PEE_IU4_TERMINAL_CONTROL_WORD_CONFLICT",
    "PEE_IU4_TERMINAL_SIGNAL_ENVELOPE_INVALID",
    "PEE_IU4_TERMINAL_TRIP_CHANNEL_INVALID",
    "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
    None,
    "PEE_IU4_TERMINAL_GUARDIAN_INVALID",
    "PEE_IU4_TERMINAL_FAILSTOP_REAP_PENDING",
    "PEE_IU4_GENESIS_PROVENANCE_INVALID",
    "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH",
)


def _derived_monitoring_reasons(
    *, group_results: tuple[str, ...], runtime_session_status: str,
    open_prepare_count: int, authority_root_ancestry_result: str,
    projection_lag_transactions: int, authorization_valid: bool,
    terminal_gap_status: str, runtime_close_fsm_reason_code: str,
) -> tuple[tuple[str, ...], bool]:
    reasons: list[str] = []

    def add(reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    hard_fail = False
    if runtime_session_status in {"OPEN_UNCLEAN", "CLOSED_UNCLEAN"}:
        add("PEE_IU4_RUNTIME_SESSION_UNCLEAN")
        hard_fail = True
    if open_prepare_count:
        add("PEE_IU4_AUTHORITY_PREPARE_COMPLETION_REQUIRED")
        hard_fail = True
    if authority_root_ancestry_result != "PASS":
        add("PEE_IU4_AUTHORITY_ROOT_MISMATCH")
        hard_fail = True
    for field_name, result, reason in zip(
        REPORT_GROUP_RESULT_FIELDS, group_results, REPORT_GROUP_REASON_CODES
    ):
        if field_name == "runtime_close_fsm_result":
            if runtime_close_fsm_reason_code != NONE:
                add(runtime_close_fsm_reason_code)
            if result == "FAIL":
                hard_fail = True
        elif result == "FAIL":
            if reason is None:
                raise AssertionError("missing monitoring group reason")
            add(reason)
            hard_fail = True
    if projection_lag_transactions:
        add("PEE_IU4_PROJECTION_LAG")
    if not authorization_valid:
        add("PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH")
        hard_fail = True
    if terminal_gap_status in {"PENDING", "FAILED"}:
        add("PEE_IU4_TERMINAL_GAP_RECONCILIATION_REQUIRED")
        hard_fail = True
    return tuple(reasons), hard_fail


def _immutable_monitoring_report_authority(subject, **constructor_values):
    """Code-literal I6 report authority; only error construction is global."""

    tuple_type = ().__class__
    dict_type = {}.__class__
    list_type = [].__class__
    text_type = "".__class__
    integer_type = (0).__class__
    boolean_type = True.__class__
    exact_type = tuple_type.__class__
    object_type = exact_type.__base__
    raw_getattribute = object_type.__getattribute__
    tuple_new = tuple_type.__new__
    tuple_count = tuple_type.__len__
    tuple_item = tuple_type.__getitem__

    report_fields = (
        "schema_version", "artifact_type", "monitoring_report_id",
        "runtime_session_id", "runtime_session_open_record_fingerprint",
        "authority_generation_id", "authority_commit_anchor", "owner_epoch",
        "report_operation", "atomic_root_fingerprint",
        "lifecycle_root_inventory_fingerprint",
        "atomic_root_inventory_fingerprint",
        "projection_root_inventory_fingerprint", "authorization_valid",
        "runtime_profile_id", "runtime_profile_fingerprint",
        "runtime_profile_anchor_record", "profile_registry_id",
        "profile_registry_fingerprint", "economics_profile_id",
        "economics_profile_fingerprint", "entry_throttle_profile_id",
        "entry_throttle_profile_fingerprint", "runtime_control_fingerprint",
        "lifecycle_ledger_tip_event_id", "lifecycle_ledger_tip_fingerprint",
        "open_prepare_count", "runtime_session_status",
        "handoff_or_genesis_manifest_id",
        "handoff_or_genesis_manifest_fingerprint", "atomic_journal_sequence",
        "atomic_journal_head", "atomic_snapshot_fingerprint",
        "authority_root_ancestry_result", "projection_cursor_id",
        "projection_cursor_fingerprint", "projection_cursor_sequence",
        "projection_cursor_journal_head", "projection_lag_transactions",
        "s2_fingerprint", "account_fingerprint", "throttle_fingerprint",
        "loss_cluster_fingerprint", "s4_fingerprint",
        "entry_quote_fingerprint", "progress_cursor_fingerprint",
        "terminal_gap_status", "terminal_monitoring_observation_id",
        "terminal_monitoring_observation_fingerprint",
        "terminal_monitoring_observation_record", "role_readiness_result",
        "lease_and_self_death_result", "pidfd_targets_result",
        "control_word_and_memfd_result", "signal_envelope_result",
        "runtime_channels_result", "seccomp_lsm_capability_result",
        "runtime_close_fsm_record", "runtime_close_fsm_result",
        "runtime_close_fsm_reason_code", "heartbeat_and_budgets_result",
        "failstop_and_terminal_gap_result", "completion_provenance_result",
        "safety_resource_schema_result", "entry_capability_result",
        "exit_capability_result", "overall_result", "reason_codes",
        "reported_at_utc", "report_fingerprint",
    )
    observation_fields = (
        "schema_version", "artifact_type",
        "terminal_monitoring_observation_id", "runtime_session_id",
        "runtime_session_open_record_fingerprint", "authority_generation_id",
        "authority_commit_anchor", "atomic_root_fingerprint",
        "source_collector_id", "source_evidence_id", "source_evidence_sha256",
        "observation_sequence", "observed_at_utc", "role_readiness",
        "lease_and_self_death", "pidfd_targets", "control_word_and_memfd",
        "signal_envelope", "runtime_channels", "seccomp_lsm_capability",
        "runtime_close_fsm", "heartbeat_and_budgets",
        "failstop_and_terminal_gap", "completion_provenance",
        "safety_resource_schema", "observation_fingerprint",
    )
    group_fields = (
        "role_readiness_result", "lease_and_self_death_result",
        "pidfd_targets_result", "control_word_and_memfd_result",
        "signal_envelope_result", "runtime_channels_result",
        "seccomp_lsm_capability_result", "runtime_close_fsm_result",
        "heartbeat_and_budgets_result", "failstop_and_terminal_gap_result",
        "completion_provenance_result", "safety_resource_schema_result",
    )
    nested_report_fields = (
        "runtime_profile_anchor_record",
        "terminal_monitoring_observation_record",
        "runtime_close_fsm_record",
    )

    def reject(code, message):
        raise IU4RecoveryProjectionError(code, message)

    def exact_keys(value, names):
        if exact_type(value) is not dict_type:
            return False
        actual_count = 0
        for key in value:
            if exact_type(key) is not text_type or key not in names:
                return False
            actual_count += 1
        expected_count = 0
        for _name in names:
            expected_count += 1
        return actual_count == expected_count

    def count(value):
        if exact_type(value) not in (tuple_type, list_type, text_type):
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring value is not a countable exact builtin",
            )
        result = 0
        for _item in value:
            result += 1
        return result

    def text_value(value, allow_none=False):
        if exact_type(value) is not text_type or not value:
            return False
        if value != value.strip() or (not allow_none and value == "NONE"):
            return False
        try:
            value.encode("ascii")
        except:
            return False
        return True

    def sha_value(value, allow_none=False):
        if exact_type(value) is not text_type:
            return False
        if allow_none and value == "NONE":
            return True
        if count(value) != 64:
            return False
        for char in value:
            if char not in "0123456789abcdef":
                return False
        return True

    def integer_value(value, minimum=0):
        return exact_type(value) is integer_type and value >= minimum

    def utc_value(value):
        if exact_type(value) is not text_type or count(value) != 20:
            return False
        if (
            value[4] != "-" or value[7] != "-" or value[10] != "T"
            or value[13] != ":" or value[16] != ":" or value[19] != "Z"
        ):
            return False
        for index in (0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15, 17, 18):
            if value[index] not in "0123456789":
                return False
        return True

    def normalize_public(value):
        value_type = exact_type(value)
        if value is None or value_type in (text_type, integer_type, boolean_type):
            return value
        if value_type is list_type:
            normalized = []
            for item in value:
                normalized.append(normalize_public(item))
            return normalized
        if value_type is dict_type:
            keys = []
            for key in value:
                if exact_type(key) is not text_type:
                    reject(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring public record contains a non-string key",
                    )
                keys.append(key)
            normalized = {}
            for key in keys:
                normalized[key] = normalize_public(value[key])
            return normalized
        reject(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            "monitoring public record contains a non-canonical value",
        )

    def freeze(value):
        value_type = exact_type(value)
        if value is None or value_type in (
            text_type, integer_type, boolean_type
        ):
            return value
        if value_type is list_type:
            items = []
            for item in value:
                items.append(freeze(item))
            return ("__LIST__", (*items,))
        if value_type is dict_type:
            keys = []
            for key in value:
                if exact_type(key) is not text_type:
                    reject(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring record contains a non-string key",
                    )
                keys.append(key)
            keys.sort()
            pairs = []
            for key in keys:
                pairs.append((key, freeze(value[key])))
            return ("__DICT__", (*pairs,))
        reject(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            "monitoring record contains a non-canonical value",
        )

    def thaw(value):
        value_type = exact_type(value)
        if value is None or value_type in (
            text_type, integer_type, boolean_type
        ):
            return value
        if value_type is not tuple_type or count(value) != 2:
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring immutable record tag is invalid",
            )
        tag = value[0]
        payload = value[1]
        if exact_type(tag) is not text_type or exact_type(payload) is not tuple_type:
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring immutable record payload is invalid",
            )
        if tag == "__LIST__":
            return [thaw(item) for item in payload]
        if tag == "__DICT__":
            result = {}
            prior = None
            for pair in payload:
                if exact_type(pair) is not tuple_type or count(pair) != 2:
                    reject(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring immutable mapping pair is invalid",
                    )
                key = pair[0]
                if exact_type(key) is not text_type or (
                    prior is not None and key <= prior
                ):
                    reject(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring immutable mapping order is invalid",
                    )
                prior = key
                result[key] = thaw(pair[1])
            return result
        reject(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            "monitoring immutable record tag is unknown",
        )

    def encode(value):
        value_type = exact_type(value)
        if value is None:
            return "null"
        if value_type is boolean_type:
            return "true" if value else "false"
        if value_type is integer_type:
            return f"{value}"
        if value_type is text_type:
            encoded = '"'
            for char in value:
                if char == '"':
                    encoded += '\\"'
                elif char == "\\":
                    encoded += "\\\\"
                elif char < " " or char > "~":
                    reject(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring string is not canonical printable ASCII",
                    )
                else:
                    encoded += char
            return encoded + '"'
        if value_type is list_type:
            parts = []
            for item in value:
                parts.append(encode(item))
            return "[" + ",".join(parts) + "]"
        if value_type is dict_type:
            keys = []
            for key in value:
                if exact_type(key) is not text_type:
                    reject(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring JSON key is not exact text",
                    )
                keys.append(key)
            keys.sort()
            parts = []
            for key in keys:
                parts.append(encode(key) + ":" + encode(value[key]))
            return "{" + ",".join(parts) + "}"
        reject(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            "monitoring value is not canonical JSON",
        )

    def sha256(value):
        data = encode(value).encode("ascii")
        message = []
        bit_length = 0
        for byte in data:
            message.append(byte)
            bit_length += 8
        message.append(128)
        while count(message) % 64 != 56:
            message.append(0)
        for shift in (56, 48, 40, 32, 24, 16, 8, 0):
            message.append((bit_length >> shift) & 255)
        state = [
            0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
            0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
        ]
        constants = (
            0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5,
            0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
            0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3,
            0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
            0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC,
            0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
            0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7,
            0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
            0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13,
            0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
            0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3,
            0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
            0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5,
            0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
            0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208,
            0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
        )

        def rotate(value, bits):
            return ((value >> bits) | (value << (32 - bits))) & 0xFFFFFFFF

        offset = 0
        while offset < count(message):
            words = []
            index = 0
            while index < 16:
                start = offset + index * 4
                words.append(
                    (message[start] << 24) | (message[start + 1] << 16)
                    | (message[start + 2] << 8) | message[start + 3]
                )
                index += 1
            while index < 64:
                s0 = (
                    rotate(words[index - 15], 7)
                    ^ rotate(words[index - 15], 18)
                    ^ (words[index - 15] >> 3)
                )
                s1 = (
                    rotate(words[index - 2], 17)
                    ^ rotate(words[index - 2], 19)
                    ^ (words[index - 2] >> 10)
                )
                words.append(
                    (words[index - 16] + s0 + words[index - 7] + s1)
                    & 0xFFFFFFFF
                )
                index += 1
            a, b, c, d, e, f, g, h = state
            index = 0
            while index < 64:
                sigma1 = rotate(e, 6) ^ rotate(e, 11) ^ rotate(e, 25)
                choice = (e & f) ^ ((~e) & g)
                temp1 = (
                    h + sigma1 + choice + constants[index] + words[index]
                ) & 0xFFFFFFFF
                sigma0 = rotate(a, 2) ^ rotate(a, 13) ^ rotate(a, 22)
                majority = (a & b) ^ (a & c) ^ (b & c)
                temp2 = (sigma0 + majority) & 0xFFFFFFFF
                h, g, f, e, d, c, b, a = (
                    g, f, e, (d + temp1) & 0xFFFFFFFF, c, b, a,
                    (temp1 + temp2) & 0xFFFFFFFF,
                )
                index += 1
            state = [
                (state[0] + a) & 0xFFFFFFFF,
                (state[1] + b) & 0xFFFFFFFF,
                (state[2] + c) & 0xFFFFFFFF,
                (state[3] + d) & 0xFFFFFFFF,
                (state[4] + e) & 0xFFFFFFFF,
                (state[5] + f) & 0xFFFFFFFF,
                (state[6] + g) & 0xFFFFFFFF,
                (state[7] + h) & 0xFFFFFFFF,
            ]
            offset += 64
        digits = "0123456789abcdef"
        result = ""
        for word in state:
            for shift in (28, 24, 20, 16, 12, 8, 4, 0):
                result += digits[(word >> shift) & 15]
        return result

    group_shapes = {
        "role_readiness": (
            ("parent_guardian_ready", "bool"), ("parent_guardian_id", "str"),
            ("parent_guardian_pid", "int"),
            ("parent_guardian_start_time_ns", "int"),
            ("native_trip_broker_ready", "bool"),
            ("native_trip_broker_id", "str"),
            ("native_trip_broker_pid", "int"),
            ("native_trip_broker_start_time_ns", "int"),
            ("persistence_worker_ready", "bool"),
            ("persistence_worker_id", "str"),
            ("persistence_worker_pid", "int"),
            ("persistence_worker_start_time_ns", "int"),
            ("listener_owner_role", "str"),
            ("worker_ack_receiver_role", "str"),
            ("renewal_sender_role", "str"),
            ("close_approval_sender_role", "str"),
            ("worker_request_sender_role", "str"),
        ),
        "lease_and_self_death": (
            ("os_lease_type", "str"), ("os_lease_identifier", "str"),
            ("credentials_capability_fingerprint", "str"),
            ("lease_nonce_sha256", "str"), ("self_death_timer_armed", "bool"),
            ("self_death_timer_id", "str"),
            ("self_death_timer_clock", "str"),
            ("self_death_timer_signal", "str"),
            ("self_death_timer_expiry_monotonic_ns", "int"),
            ("native_shim_fingerprint", "str"),
        ),
        "pidfd_targets": (
            ("trading_self", (("pidfd_id", "str"), ("target_pid", "int"), ("target_start_time_ns", "int"), ("sigkill_probe_result", "str"))),
            ("guardian", (("pidfd_id", "str"), ("target_pid", "int"), ("target_start_time_ns", "int"), ("sigkill_probe_result", "str"))),
            ("broker", (("pidfd_id", "str"), ("target_pid", "int"), ("target_start_time_ns", "int"), ("sigkill_probe_result", "str"))),
        ),
        "control_word_and_memfd": (
            ("control_word_schema", "int"), ("control_word_state", "str"),
            ("trip_sequence", "int"), ("renewal_sequence", "int"),
            ("broker_cas_sequence", "int"),
            ("memfd_create_flags", ("LIST", "str")),
            ("initial_seals", ("LIST", "str")),
            ("intermediate_seals", ("LIST", "str")),
            ("final_seals", ("LIST", "str")),
            ("trading_mapping_rights", "str"),
            ("guardian_mapping_rights", "str"),
            ("broker_mapping_rights", "str"),
            ("worker_mapping_rights", "str"),
        ),
        "signal_envelope": (
            ("signal_envelope_id", "str"),
            ("signal_envelope_fingerprint", "str"),
            ("signal_mask_fingerprint", "str"),
            ("signal_disposition_fingerprint", "str"),
            ("wait_killable_recv", "bool"),
            ("later_signal_change_locked", "bool"),
        ),
        "runtime_channels": (
            ("channel_records", ("LIST", (
                ("channel_id", "str"), ("direction", "str"),
                ("sender_role", "str"), ("receiver_role", "str"),
                ("so_peercred", (("pid", "int"), ("uid", "int"), ("gid", "int"))),
                ("peer_binding_fingerprint", "str"), ("so_passcred", "int"),
                ("so_passrights", "int"), ("receiver_tid", "int"),
                ("receiver_files_table_fingerprint", "str"),
                ("receiver_tsync_filter_fingerprint", "str"),
                ("final_role_filter_fingerprint", "str"), ("scm_fds", "int"),
                ("control_buffer_bytes", "int"),
                ("queue_inventory_fingerprint", "str"),
                ("fd_inventory_fingerprint", "str"),
                ("fdinfo_inventory_fingerprint", "str"),
                ("ofd_inventory_fingerprint", "str"),
                ("lock_inventory_fingerprint", "str"),
                ("rights_reject_result", "str"),
            ))),
            ("guardian_notification_eventfd_id", "str"),
            ("broker_notification_eventfd_id", "str"),
        ),
        "seccomp_lsm_capability": (
            ("seccomp_listener_id", "str"),
            ("seccomp_notification_id", "str"),
            ("seccomp_listener_owner", "str"),
            ("seccomp_listener_receive_error_status", "str"),
            ("seccomp_filter_hash", "str"), ("btf_id", "str"),
            ("program_ids", ("LIST", "str")), ("map_ids", ("LIST", "str")),
            ("link_ids", ("LIST", "str")), ("pin_paths", ("LIST", "str")),
            ("cgroup_ids", ("LIST", "str")),
            ("lsm_hook_coverage", ("LIST", "str")),
            ("socket_cookie_tag_inventory_fingerprint", "str"),
            ("phase_map_frozen", "bool"), ("config_map_frozen", "bool"),
            ("bpf_cmpxchg_proof_fingerprint", "str"),
            ("scalar_seccomp_userspace_authority_matrix", ("LIST", None)),
            ("scalar_seccomp_userspace_authority_matrix_fingerprint", "str"),
            ("capability_envelope_fingerprint", "str"),
        ),
        "runtime_close_fsm": (
            ("channel_phase", "str"), ("close_fsm_phase", "str"),
            ("close_prepare_event_id", "str"),
            ("broker_closed_evidence_id", "str"),
            ("close_commit_event_id", "str"), ("close_peer_status", "str"),
            ("close_hup_status", "str"), ("close_timeout_status", "str"),
            ("request_owner_role", "str"), ("ack_owner_role", "str"),
        ),
        "heartbeat_and_budgets": (
            ("heartbeat_interval_ms", "int"), ("heartbeat_last_sequence", "int"),
            ("heartbeat_age_ms", "int"), ("capability_probe_age_ms", "int"),
            ("capability_probe_expiry_ms", "int"), ("clock_source", "str"),
            ("terminal_guardian_lease_max_ms", "int"),
            ("terminal_broker_trip_cas_max_ms", "int"),
            ("terminal_guardian_trip_dispatch_max_ms", "int"),
            ("terminal_kernel_signal_generation_budget_ms", "int"),
            ("terminal_failstop_max_ms", "int"),
            ("termination_latch_deadline_ms", "int"),
        ),
        "failstop_and_terminal_gap": (
            ("failstop_asserted", "bool"), ("pending_signal_status", "str"),
            ("reap_status", "str"), ("runtime_session_unclean", "bool"),
            ("terminal_gap_status", "str"),
            ("liveness_pipe_read_endpoint_id", "str"),
            ("liveness_pipe_write_endpoint_id", "str"),
            ("liveness_pipe_inode", "int"),
            ("liveness_pipe_capacity_bytes", "int"),
            ("liveness_pipe_exclusive_owner_role", "str"),
            ("liveness_pipe_write_forbidden", "bool"),
            ("liveness_pipe_payload_bytes", "int"),
            ("liveness_pipe_empty", "bool"),
            ("liveness_pipe_hup_status", "str"),
            ("liveness_pipe_fallback_status", "str"),
        ),
        "completion_provenance": (
            ("completion_provenance", "str"),
            ("completion_authorization_id", "str"),
            ("completion_consumption_event_id", "str"),
            ("completion_startup_attempt_id", "str"),
            ("direct_process_instance_id", "str"),
            ("genesis_operation_attempt_id", "str"),
            ("direct_continuation_nonce_hash", "str"),
            ("direct_continuation_nonce_preimage_match", "bool"),
            ("prior_runtime_session_count", "int"),
            ("direct_first_start_eligible", "bool"),
        ),
        "safety_resource_schema": (
            ("kill_level", "str"), ("entry_allowed", "bool"),
            ("exit_evaluation_allowed", "bool"), ("runtime_directive", "str"),
            ("reason_codes", ("LIST", None)),
            ("activation_authorization_valid", "bool"),
            ("restart_authorization_status", "str"),
            ("profile_binding_status", "str"),
            ("resource_reserve_status", "str"), ("io_status", "str"),
            ("atomic_schema_version", "int"),
            ("lifecycle_schema_version", "int"),
            ("projection_schema_version", "int"),
            ("legacy_exit_only_status", "str"),
        ),
    }

    def shape_valid(value, shape):
        if shape == "str":
            return exact_type(value) is text_type
        if shape == "int":
            return exact_type(value) is integer_type
        if shape == "bool":
            return exact_type(value) is boolean_type
        if exact_type(shape) is tuple_type and count(shape) == 2 and shape[0] == "LIST":
            if exact_type(value) is not list_type:
                return False
            if shape[1] is None:
                return True
            for item in value:
                if not shape_valid(item, shape[1]):
                    return False
            return True
        names = tuple_name_list = []
        for pair in shape:
            tuple_name_list.append(pair[0])
        names = (*tuple_name_list,)
        if not exact_keys(value, names):
            return False
        for pair in shape:
            if not shape_valid(value[pair[0]], pair[1]):
                return False
        return True

    def identifier_tree_valid(value, path=""):
        value_type = exact_type(value)
        if value_type is dict_type:
            for key in value:
                if not identifier_tree_valid(value[key], key):
                    return False
            return True
        if value_type is list_type:
            for item in value:
                if not identifier_tree_valid(item, path):
                    return False
            return True
        if path == "direct_continuation_nonce_hash" and value == "NONE":
            return True
        if path.endswith(("_fingerprint", "_sha256", "_hash")):
            return sha_value(value)
        if path.endswith("_id") and value != "NONE":
            return text_value(value)
        if path.endswith(("_pid", "_tid", "_start_time_ns")):
            return integer_value(value, 1)
        if path.endswith(("_count", "_sequence", "_ms", "_bytes")):
            return integer_value(value)
        return True

    def enum(value, allowed):
        return exact_type(value) is text_type and value in allowed

    def close_projection(close, session_status):
        phase = close["close_fsm_phase"]
        if not enum(close["channel_phase"], {
            "LISTENER_HANDOFF", "LISTENER_RECEIVED", "HANDOFF_REVOKED_GRANTED",
            "BOOTSTRAP", "OPEN_DURABLE_GRANTED", "RELEASED",
        }) or not enum(phase, {
            "OPEN", "CLOSING", "PREPARE", "BROKER_CLOSED", "COMMIT",
            "COMMITTED", "FAILED",
        }):
            reject("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "unknown Close enum")
        for name in ("close_peer_status", "close_hup_status", "close_timeout_status"):
            if not enum(close[name], {"NONE", "OK", "HUP", "TIMEOUT", "ERROR"}):
                reject("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "unknown Close status")
        identifiers = (
            close["close_prepare_event_id"], close["broker_closed_evidence_id"],
            close["close_commit_event_id"],
        )
        statuses = (
            close["close_peer_status"], close["close_hup_status"],
            close["close_timeout_status"],
        )
        presence = (
            identifiers[0] != "NONE", identifiers[1] != "NONE",
            identifiers[2] != "NONE",
        )
        owners_ok = (
            close["request_owner_role"] == "TRADING_CHILD"
            and close["ack_owner_role"] == "TERMINAL_PERSISTENCE_WORKER_V8"
        )
        expected_ids = {
            "OPEN": (False, False, False), "CLOSING": (False, False, False),
            "PREPARE": (True, False, False),
            "BROKER_CLOSED": (True, True, False),
            "COMMIT": (True, True, True), "COMMITTED": (True, True, True),
        }
        expected_status = {
            "OPEN": ("NONE", "NONE", "NONE"),
            "CLOSING": ("NONE", "NONE", "NONE"),
            "PREPARE": ("NONE", "NONE", "NONE"),
            "BROKER_CLOSED": ("OK", "HUP", "NONE"),
            "COMMIT": ("OK", "HUP", "NONE"),
            "COMMITTED": ("OK", "HUP", "NONE"),
        }
        if phase != "FAILED":
            expected_channel = "RELEASED" if phase == "COMMITTED" else "OPEN_DURABLE_GRANTED"
            expected_session = "CLOSED_CLEAN" if phase == "COMMITTED" else "OPEN_CLEAN"
            if (
                presence == expected_ids[phase]
                and statuses == expected_status[phase] and owners_ok
                and close["channel_phase"] == expected_channel
                and session_status in (None, expected_session)
            ):
                return "PASS", "NONE"
            reason = (
                "PEE_IU4_RUNTIME_SESSION_CLOSE_INCOMPLETE"
                if presence != expected_ids[phase]
                else "PEE_IU4_RUNTIME_SESSION_CLOSE_PROTOCOL_INVALID"
            )
            return "FAIL", reason
        allowed_status = {
            (False, False, False): {
                ("ERROR", "NONE", "NONE"), ("NONE", "NONE", "TIMEOUT"),
            },
            (True, False, False): {
                ("ERROR", "NONE", "NONE"), ("OK", "ERROR", "NONE"),
                ("NONE", "NONE", "TIMEOUT"), ("OK", "NONE", "TIMEOUT"),
            },
            (True, True, False): {
                ("ERROR", "NONE", "NONE"), ("OK", "ERROR", "NONE"),
                ("NONE", "NONE", "TIMEOUT"), ("OK", "NONE", "TIMEOUT"),
            },
            (True, True, True): {
                ("ERROR", "NONE", "NONE"), ("OK", "ERROR", "NONE"),
                ("NONE", "NONE", "TIMEOUT"), ("OK", "NONE", "TIMEOUT"),
            },
        }
        allowed_channels = {
            (False, False, False): {("OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN")},
            (True, False, False): {("OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN")},
            (True, True, False): {("RELEASED", "CLOSED_UNCLEAN")},
            (True, True, True): {
                ("OPEN_DURABLE_GRANTED", "OPEN_UNCLEAN"),
                ("RELEASED", "CLOSED_UNCLEAN"),
            },
        }
        session_ok = False
        for channel, expected_session in allowed_channels.get(presence, ()):
            if close["channel_phase"] == channel and (
                session_status is None or session_status == expected_session
            ):
                session_ok = True
        if statuses in allowed_status.get(presence, ()) and session_ok and owners_ok:
            return (
                "PASS",
                "PEE_IU4_RUNTIME_SESSION_CLOSE_TIMEOUT"
                if statuses[2] == "TIMEOUT"
                else "PEE_IU4_RUNTIME_SESSION_CLOSE_TRANSPORT_FAILED",
            )
        if presence not in allowed_status:
            return "FAIL", "PEE_IU4_RUNTIME_SESSION_CLOSE_INCOMPLETE"
        return "FAIL", "PEE_IU4_RUNTIME_SESSION_CLOSE_PROTOCOL_INVALID"

    def derive_groups(observation, session_status):
        results = []
        role = observation["role_readiness"]
        roles = {"PARENT_GUARDIAN_V13", "NATIVE_TRIP_BROKER_V10", "TERMINAL_PERSISTENCE_WORKER_V8", "TRADING_CHILD"}
        for name in ("listener_owner_role", "worker_ack_receiver_role", "renewal_sender_role", "close_approval_sender_role", "worker_request_sender_role"):
            if not enum(role[name], roles):
                reject("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "unknown role enum")
        for prefix in ("parent_guardian", "native_trip_broker", "persistence_worker"):
            if not integer_value(role[prefix + "_pid"], 1) or not integer_value(role[prefix + "_start_time_ns"], 1):
                reject("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "invalid role identity")
        results.append("PASS" if (
            role["listener_owner_role"] == "NATIVE_TRIP_BROKER_V10"
            and role["worker_ack_receiver_role"] == "TERMINAL_PERSISTENCE_WORKER_V8"
            and role["renewal_sender_role"] == "TRADING_CHILD"
            and role["close_approval_sender_role"] == "PARENT_GUARDIAN_V13"
            and role["worker_request_sender_role"] == "TRADING_CHILD"
            and role["parent_guardian_ready"] is True
            and role["native_trip_broker_ready"] is True
            and role["persistence_worker_ready"] is True
        ) else "FAIL")
        lease = observation["lease_and_self_death"]
        results.append("PASS" if (
            lease["os_lease_type"] == "PIDFD_KERNEL_SELF_DEATH"
            and lease["self_death_timer_armed"] is True
            and lease["self_death_timer_clock"] == "CLOCK_BOOTTIME"
            and lease["self_death_timer_signal"] == "SIGKILL"
            and integer_value(lease["self_death_timer_expiry_monotonic_ns"], 1)
        ) else "FAIL")
        pidfd = observation["pidfd_targets"]
        pidfd_ok = True
        for name in ("trading_self", "guardian", "broker"):
            record = pidfd[name]
            if (
                not integer_value(record["target_pid"], 1)
                or not integer_value(record["target_start_time_ns"], 1)
                or not enum(record["sigkill_probe_result"], {"PASS", "FAIL"})
                or record["sigkill_probe_result"] != "PASS"
            ):
                pidfd_ok = False
        pidfd_ok = pidfd_ok and (
            pidfd["guardian"]["target_pid"] == role["parent_guardian_pid"]
            and pidfd["guardian"]["target_start_time_ns"] == role["parent_guardian_start_time_ns"]
            and pidfd["broker"]["target_pid"] == role["native_trip_broker_pid"]
            and pidfd["broker"]["target_start_time_ns"] == role["native_trip_broker_start_time_ns"]
        )
        results.append("PASS" if pidfd_ok else "FAIL")
        control = observation["control_word_and_memfd"]
        for name in ("trip_sequence", "renewal_sequence", "broker_cas_sequence"):
            if not integer_value(control[name]):
                reject("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "invalid control sequence")
        results.append("PASS" if (
            control["control_word_schema"] == 3
            and control["control_word_state"] in {"RUNNING", "CLOSING", "TERMINATING", "CLOSED"}
            and control["broker_cas_sequence"] <= control["trip_sequence"]
            and control["memfd_create_flags"] == ["MFD_CLOEXEC"]
            and control["initial_seals"] == ["F_SEAL_SHRINK"]
            and control["intermediate_seals"] == ["F_SEAL_GROW"]
            and control["final_seals"] == ["F_SEAL_SEAL"]
            and control["trading_mapping_rights"] == "READ_WRITE"
            and control["guardian_mapping_rights"] == "READ_ONLY"
            and control["broker_mapping_rights"] == "READ_WRITE"
            and control["worker_mapping_rights"] == "READ_ONLY"
        ) else "FAIL")
        signal = observation["signal_envelope"]
        results.append("PASS" if signal["wait_killable_recv"] is True and signal["later_signal_change_locked"] is True else "FAIL")
        channels = observation["runtime_channels"]
        channel_ok = count(channels["channel_records"]) == 6
        for record in channels["channel_records"]:
            if (
                record["direction"] not in {"A_TO_B", "B_TO_A"}
                or record["sender_role"] not in roles or record["receiver_role"] not in roles
                or not integer_value(record["so_peercred"]["pid"], 1)
                or not integer_value(record["so_peercred"]["uid"])
                or not integer_value(record["so_peercred"]["gid"])
                or (record["so_passcred"], record["so_passrights"], record["scm_fds"], record["control_buffer_bytes"], record["rights_reject_result"])
                != (0, 0, 0, 0, "EPERM")
            ):
                channel_ok = False
        results.append("PASS" if channel_ok else "FAIL")
        seccomp = observation["seccomp_lsm_capability"]
        expected_hooks = ["file_open", "file_permission", "socket_connect", "socket_sendmsg", "task_kill", "bprm_check_security"]
        results.append("PASS" if (
            seccomp["seccomp_listener_owner"] == "NATIVE_TRIP_BROKER_V10"
            and seccomp["seccomp_listener_receive_error_status"] == "NONE"
            and seccomp["phase_map_frozen"] is True
            and seccomp["config_map_frozen"] is True
            and seccomp["lsm_hook_coverage"] == expected_hooks
        ) else "FAIL")
        close_result, close_reason = close_projection(observation["runtime_close_fsm"], session_status)
        results.append(close_result)
        budget = observation["heartbeat_and_budgets"]
        for name in ("heartbeat_interval_ms", "heartbeat_last_sequence", "heartbeat_age_ms", "capability_probe_age_ms", "capability_probe_expiry_ms", "terminal_guardian_lease_max_ms", "terminal_broker_trip_cas_max_ms", "terminal_guardian_trip_dispatch_max_ms", "terminal_kernel_signal_generation_budget_ms", "terminal_failstop_max_ms", "termination_latch_deadline_ms"):
            if not integer_value(budget[name]):
                reject("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "invalid budget")
        results.append("PASS" if (
            budget["heartbeat_interval_ms"] == 10
            and budget["clock_source"] == "CLOCK_BOOTTIME"
            and 0 <= budget["heartbeat_age_ms"] <= 25
            and 0 <= budget["capability_probe_age_ms"] <= 25
            and 0 <= budget["capability_probe_expiry_ms"] <= 25
            and budget["terminal_guardian_lease_max_ms"] == 25
            and budget["terminal_broker_trip_cas_max_ms"] == 5
            and budget["terminal_guardian_trip_dispatch_max_ms"] == 5
            and budget["terminal_kernel_signal_generation_budget_ms"] == 25
            and budget["terminal_failstop_max_ms"] == 100
            and 1 <= budget["termination_latch_deadline_ms"] <= 100
        ) else "FAIL")
        failstop = observation["failstop_and_terminal_gap"]
        results.append("PASS" if (
            failstop["failstop_asserted"] is False
            and failstop["pending_signal_status"] == "NONE"
            and failstop["reap_status"] == "NONE"
            and failstop["terminal_gap_status"] == "NONE"
            and failstop["liveness_pipe_hup_status"] == "NOT_OBSERVED"
            and failstop["liveness_pipe_fallback_status"] == "NOT_REQUIRED"
            and failstop["liveness_pipe_write_forbidden"] is True
            and failstop["liveness_pipe_payload_bytes"] == 0
            and failstop["liveness_pipe_empty"] is True
            and failstop["runtime_session_unclean"] is False
        ) else "FAIL")
        completion = observation["completion_provenance"]
        direct_ok = (
            completion["completion_provenance"] == "DIRECT"
            and completion["completion_authorization_id"] == "NONE"
            and completion["completion_consumption_event_id"] == "NONE"
            and completion["completion_startup_attempt_id"] == "NONE"
            and completion["direct_continuation_nonce_preimage_match"] is True
            and completion["prior_runtime_session_count"] == 0
            and completion["direct_first_start_eligible"] is True
        )
        recovered_ok = (
            completion["completion_provenance"] == "RECOVERED_AFTER_PREPARE"
            and completion["completion_authorization_id"] != "NONE"
            and completion["completion_consumption_event_id"] != "NONE"
            and completion["completion_startup_attempt_id"] != "NONE"
            and completion["direct_process_instance_id"] == "NONE"
            and completion["genesis_operation_attempt_id"] == "NONE"
            and completion["direct_continuation_nonce_hash"] == "NONE"
            and completion["direct_continuation_nonce_preimage_match"] is False
            and completion["direct_first_start_eligible"] is False
        )
        results.append("PASS" if direct_ok or recovered_ok else "FAIL")
        safety = observation["safety_resource_schema"]
        level = safety["kill_level"]
        expected_entry = level == "NONE"
        expected_exit = level in {"NONE", "SOFT"}
        expected_directive = {"NONE": "CONTINUE", "SOFT": "CONTINUE", "HARD": "STOP_LOOP", "EMERGENCY": "EXIT_PROCESS"}.get(level)
        safety_ok = (
            expected_directive is not None
            and safety["entry_allowed"] is expected_entry
            and safety["exit_evaluation_allowed"] is expected_exit
            and safety["runtime_directive"] == expected_directive
            and safety["activation_authorization_valid"] is True
            and safety["restart_authorization_status"] in {"NOT_REQUIRED", "VALID"}
            and safety["profile_binding_status"] == "MATCH"
            and safety["resource_reserve_status"] == "PASS"
            and safety["io_status"] == "PASS"
            and (safety["atomic_schema_version"], safety["lifecycle_schema_version"], safety["projection_schema_version"]) == (2, 1, 1)
            and safety["legacy_exit_only_status"] in {"NOT_APPLICABLE", "COMPLETE", "REQUIRED", "ACTIVE"}
        )
        results.append("WARN" if safety_ok and safety["legacy_exit_only_status"] in {"REQUIRED", "ACTIVE"} else "PASS" if safety_ok else "FAIL")
        return (*results,), close_reason

    mode = "VALIDATE"
    instance = None
    subject_type = exact_type(subject)
    if constructor_values:
        report_type = subject
        if exact_type(report_type) is not exact_type:
            reject(
                "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
                "monitoring report type is not exact",
            )
        if not exact_keys(constructor_values, report_fields):
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring constructor fields differ",
            )
        raw = {}
        for name in report_fields:
            value = constructor_values[name]
            if name == "reason_codes":
                if exact_type(value) is not tuple_type:
                    reject(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring constructor reasons are not immutable",
                    )
                reasons = []
                for item in value:
                    if exact_type(item) is not text_type:
                        reject(
                            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                            "monitoring constructor reason is not exact text",
                        )
                    reasons.append(item)
                raw[name] = (*reasons,)
            else:
                raw[name] = normalize_public(value)
        mode = "CONSTRUCT"
    elif subject_type is tuple_type:
        if count(subject) != 2 or exact_type(subject[0]) is not text_type:
            reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "invalid monitoring authority invocation")
        if subject[0] not in {"DERIVE", "ADDRESS"} or exact_type(subject[1]) is not dict_type:
            reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "invalid monitoring authority invocation")
        mode = subject[0]
        raw = {}
        for name in subject[1]:
            if exact_type(name) is not text_type:
                reject(
                    "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                    "monitoring authority field name is not exact text",
                )
            value = subject[1][name]
            if name == "reason_codes":
                if exact_type(value) is not tuple_type:
                    reject(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring authority reasons are not immutable",
                    )
                reasons = []
                for item in value:
                    if exact_type(item) is not text_type:
                        reject(
                            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                            "monitoring authority reason is not exact text",
                        )
                    reasons.append(item)
                raw[name] = (*reasons,)
            else:
                raw[name] = normalize_public(value)
    else:
        instance = subject
        instance_dict = raw_getattribute(instance, "__dict__")
        if exact_type(instance_dict) is not dict_type:
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring instance dictionary is not exact",
            )
        for _name in instance_dict:
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring instance dictionary is nonempty",
            )
        try:
            storage_count = tuple_count(instance)
        except TypeError:
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring immutable authority storage is absent",
            )
        if storage_count != 70:
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring immutable authority storage differs",
            )
        raw = {}
        index = 0
        for name in report_fields:
            raw[name] = tuple_item(instance, index)
            index += 1

    if mode == "DERIVE":
        required = []
        for name in report_fields:
            if name not in {
                "schema_version", "artifact_type", "monitoring_report_id",
                "report_fingerprint", "runtime_profile_fingerprint",
                "runtime_profile_anchor_record", "profile_registry_id",
                "profile_registry_fingerprint", "projection_lag_transactions",
                "terminal_monitoring_observation_id",
                "terminal_monitoring_observation_fingerprint",
                "runtime_close_fsm_record", "runtime_close_fsm_result",
                "runtime_close_fsm_reason_code", "entry_capability_result",
                "exit_capability_result", "overall_result", "reason_codes",
            } and name not in group_fields:
                required.append(name)
        if not exact_keys(raw, (*required,)):
            reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring builder fields differ")
        raw["schema_version"] = 1
        raw["artifact_type"] = "iu4_recovery_monitoring_report_v1"
    elif mode == "ADDRESS":
        required = []
        for name in report_fields:
            if name not in {"schema_version", "artifact_type", "monitoring_report_id", "report_fingerprint"}:
                required.append(name)
        if not exact_keys(raw, (*required,)):
            reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring build fields differ")
        raw["schema_version"] = 1
        raw["artifact_type"] = "iu4_recovery_monitoring_report_v1"

    serialized = {}
    for name in report_fields:
        if name in raw:
            value = raw[name]
            if name in nested_report_fields:
                if mode == "VALIDATE":
                    value = thaw(value)
                elif exact_type(value) is not dict_type:
                    reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring nested record is not exact")
            elif name == "reason_codes":
                if exact_type(value) is not tuple_type:
                    reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring reasons are not immutable")
                reasons = []
                for item in value:
                    if exact_type(item) is not text_type:
                        reject(
                            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                            "monitoring reason is not exact text",
                        )
                    reasons.append(item)
                value = reasons
            serialized[name] = value
    raw = serialized

    integer_fields = (
        "open_prepare_count", "atomic_journal_sequence",
        "projection_cursor_sequence", "projection_lag_transactions",
    )
    for name in report_fields:
        if name not in raw:
            continue
        if name in nested_report_fields:
            if exact_type(raw[name]) is not dict_type:
                reject(
                    "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                    "monitoring nested record is not an exact mapping",
                )
        elif name == "reason_codes":
            if exact_type(raw[name]) is not list_type:
                reject(
                    "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                    "monitoring reasons are not a canonical array",
                )
        elif name == "authorization_valid":
            if exact_type(raw[name]) is not boolean_type:
                reject(
                    "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                    "monitoring authorization flag is not exact",
                )
        elif name in integer_fields or name == "schema_version":
            if exact_type(raw[name]) is not integer_type:
                reject(
                    "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                    "monitoring integer scalar is not exact",
                )
        elif exact_type(raw[name]) is not text_type:
            reject(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring text scalar is not exact",
            )

    observation = raw["terminal_monitoring_observation_record"]
    if not exact_keys(observation, observation_fields):
        reject("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "bound Observation fields differ")
    if observation["schema_version"] != 1 or observation["artifact_type"] != "iu4_terminal_monitoring_observation_v1":
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "bound Observation schema differs")
    for group_name in group_shapes:
        if not shape_valid(observation[group_name], group_shapes[group_name]) or not identifier_tree_valid(observation[group_name]):
            reject("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "bound Observation group is not canonical")
    if observation["runtime_session_id"] == "NONE":
        if observation["runtime_session_open_record_fingerprint"] != "NONE":
            reject("PEE_IU4_RUNTIME_SESSION_UNCLEAN", "bound Observation Session pair differs")
    elif not text_value(observation["runtime_session_id"]) or not sha_value(observation["runtime_session_open_record_fingerprint"]):
        reject("PEE_IU4_RUNTIME_SESSION_UNCLEAN", "bound Observation Session is invalid")
    for name in ("authority_generation_id", "source_collector_id", "source_evidence_id"):
        if not text_value(observation[name]):
            reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "bound Observation identifier is invalid")
    for name in ("authority_commit_anchor", "atomic_root_fingerprint", "source_evidence_sha256"):
        if not sha_value(observation[name]):
            reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "bound Observation fingerprint is invalid")
    if not integer_value(observation["observation_sequence"]) or not utc_value(observation["observed_at_utc"]):
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "bound Observation sequence/time is invalid")
    observation_material = {name: observation[name] for name in observation_fields if name not in {"terminal_monitoring_observation_id", "observation_fingerprint"}}
    expected_observation_id = "IU4-TERMINAL-MONITORING-OBSERVATION-V1-" + sha256(observation_material)
    if observation["terminal_monitoring_observation_id"] != expected_observation_id:
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "bound Observation ID differs")
    observation_material["terminal_monitoring_observation_id"] = expected_observation_id
    if observation["observation_fingerprint"] != sha256(observation_material):
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "bound Observation fingerprint differs")

    pinned_root = (
        1, "iu4_terminal_runtime_profile_trust_root_v1",
        "IU4-TERMINAL-RUNTIME-PROFILE-TRUST-ROOT-V1-946520547808afb5d297c6b3e55756d6e4a31f9f9e15226a7647bd45b9ef982c",
        "IU4-I6-REREVIEW-8-PINNED-TRUST-ROOT-AUTHORITY-V1",
        "7c3211a1b2b8899a0ace1cd3276be5bb88752c3cf08e5da2ad7abcfb5d7eca08",
        "iu4_terminal_runtime_profile_registry_v1",
        "IU4-TERMINAL-RUNTIME-PROFILE-REGISTRY-V1-ffa9fcc9e284efcdfe9ffcd78b24452909d5d5f80f8c64a8f7abb79ab7a74f2f",
        "177b99dff53d2f0c005b4a50a96508d04ac40c1f4aaf78250a420570be3d79ed",
        "95feb2817af0d3db81b820fd2a170d82bb13c7f7000e5aafaf77cea45b61cf5a",
        "iu4_terminal_runtime_profile_anchor_v1",
        (
            ("RP", "842946705cc9fca3cb2b83beddd819ff48ea95cec6fecef153eb052e6e69285c", "IU4-TERMINAL-RUNTIME-PROFILE-ANCHOR-V1-28ee6159e47a09955af77d0e07371af24134c29d68d928163d4ef2507ec7b5e7", "e3319fe1566efb48c8934d6cbd0e7d3d184ce7946a4c737d5c228dd2ac9c0ae5"),
            ("RP-RECOVERED-INVALID", "5f87a020ed7907df8a9511698d607e88b6bb804d684a9cc5930fa0ee0b73cfc7", "IU4-TERMINAL-RUNTIME-PROFILE-ANCHOR-V1-03b712e42f04c120c363826c2d7be648e251f0c01a1ee7024e875c704ef78420", "527f5855a325d61df4c4051351fbbaf3bcb4fbf73406f501ce47e067e16c198d"),
        ),
    )
    profile_id = raw["runtime_profile_id"]
    if exact_type(profile_id) is not text_type:
        reject("PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID", "runtime profile ID is not exact")
    if profile_id == pinned_root[10][0][0]:
        trusted = pinned_root[10][0]
    elif profile_id == pinned_root[10][1][0]:
        trusted = pinned_root[10][1]
    else:
        reject("PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID", "runtime profile is not code-pinned")
    trusted_anchor = {
        "schema_version": 1, "artifact_type": pinned_root[9],
        "profile_anchor_id": trusted[2], "runtime_profile_id": trusted[0],
        "terminal_static_bindings_fingerprint": trusted[1],
        "profile_anchor_fingerprint": trusted[3],
    }
    if mode == "DERIVE":
        raw["runtime_profile_fingerprint"] = trusted[1]
        raw["runtime_profile_anchor_record"] = trusted_anchor
        raw["profile_registry_id"] = pinned_root[6]
        raw["profile_registry_fingerprint"] = pinned_root[7]
    elif (
        raw["runtime_profile_fingerprint"] != trusted[1]
        or raw["runtime_profile_anchor_record"] != trusted_anchor
        or raw["profile_registry_id"] != pinned_root[6]
        or raw["profile_registry_fingerprint"] != pinned_root[7]
    ):
        reject("PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID", "monitoring profile root binding differs")

    role = observation["role_readiness"]
    lease = observation["lease_and_self_death"]
    pidfd = observation["pidfd_targets"]
    control = observation["control_word_and_memfd"]
    signal = observation["signal_envelope"]
    channels = observation["runtime_channels"]
    seccomp = observation["seccomp_lsm_capability"]
    close = observation["runtime_close_fsm"]
    heartbeat = observation["heartbeat_and_budgets"]
    liveness = observation["failstop_and_terminal_gap"]
    completion = observation["completion_provenance"]
    safety = observation["safety_resource_schema"]
    actual_static = (
        (role["parent_guardian_id"], role["parent_guardian_pid"], role["parent_guardian_start_time_ns"], role["native_trip_broker_id"], role["native_trip_broker_pid"], role["native_trip_broker_start_time_ns"], role["persistence_worker_id"], role["persistence_worker_pid"], role["persistence_worker_start_time_ns"], role["listener_owner_role"], role["worker_ack_receiver_role"], role["renewal_sender_role"], role["close_approval_sender_role"], role["worker_request_sender_role"]),
        (lease["os_lease_type"], lease["os_lease_identifier"], lease["credentials_capability_fingerprint"], lease["lease_nonce_sha256"], lease["self_death_timer_id"], lease["self_death_timer_clock"], lease["self_death_timer_signal"], lease["self_death_timer_expiry_monotonic_ns"], lease["native_shim_fingerprint"]),
        ((pidfd["trading_self"]["pidfd_id"], pidfd["trading_self"]["target_pid"], pidfd["trading_self"]["target_start_time_ns"]), (pidfd["guardian"]["pidfd_id"], pidfd["guardian"]["target_pid"], pidfd["guardian"]["target_start_time_ns"]), (pidfd["broker"]["pidfd_id"], pidfd["broker"]["target_pid"], pidfd["broker"]["target_start_time_ns"])),
        (control["control_word_schema"], (*control["memfd_create_flags"],), (*control["initial_seals"],), (*control["intermediate_seals"],), (*control["final_seals"],), control["trading_mapping_rights"], control["guardian_mapping_rights"], control["broker_mapping_rights"], control["worker_mapping_rights"]),
        (signal["signal_envelope_id"], signal["signal_envelope_fingerprint"], signal["signal_mask_fingerprint"], signal["signal_disposition_fingerprint"]),
        (channels["guardian_notification_eventfd_id"], channels["broker_notification_eventfd_id"], (*((record["channel_id"], record["direction"], record["sender_role"], record["receiver_role"], (record["so_peercred"]["pid"], record["so_peercred"]["uid"], record["so_peercred"]["gid"]), record["peer_binding_fingerprint"], record["receiver_tid"], record["receiver_files_table_fingerprint"], record["receiver_tsync_filter_fingerprint"], record["final_role_filter_fingerprint"], record["queue_inventory_fingerprint"], record["fd_inventory_fingerprint"], record["fdinfo_inventory_fingerprint"], record["ofd_inventory_fingerprint"], record["lock_inventory_fingerprint"]) for record in channels["channel_records"]),)),
        (seccomp["seccomp_listener_id"], seccomp["seccomp_notification_id"], seccomp["seccomp_listener_owner"], seccomp["seccomp_filter_hash"], seccomp["btf_id"], (*seccomp["program_ids"],), (*seccomp["map_ids"],), (*seccomp["link_ids"],), (*seccomp["pin_paths"],), (*seccomp["cgroup_ids"],), (*seccomp["lsm_hook_coverage"],), seccomp["socket_cookie_tag_inventory_fingerprint"], seccomp["bpf_cmpxchg_proof_fingerprint"], (*seccomp["scalar_seccomp_userspace_authority_matrix"],), seccomp["scalar_seccomp_userspace_authority_matrix_fingerprint"], seccomp["capability_envelope_fingerprint"]),
        (close["request_owner_role"], close["ack_owner_role"]),
        (heartbeat["heartbeat_interval_ms"], heartbeat["clock_source"], heartbeat["terminal_guardian_lease_max_ms"], heartbeat["terminal_broker_trip_cas_max_ms"], heartbeat["terminal_guardian_trip_dispatch_max_ms"], heartbeat["terminal_kernel_signal_generation_budget_ms"], heartbeat["terminal_failstop_max_ms"]),
        (liveness["liveness_pipe_read_endpoint_id"], liveness["liveness_pipe_write_endpoint_id"], liveness["liveness_pipe_inode"], liveness["liveness_pipe_capacity_bytes"], liveness["liveness_pipe_exclusive_owner_role"]),
        (completion["completion_provenance"], completion["completion_authorization_id"], completion["completion_consumption_event_id"], completion["completion_startup_attempt_id"], completion["direct_process_instance_id"], completion["genesis_operation_attempt_id"], completion["direct_continuation_nonce_hash"]),
        (safety["atomic_schema_version"], safety["lifecycle_schema_version"], safety["projection_schema_version"]),
    )
    h = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    common = (
        ("GUARDIAN-1", 11, 1, "BROKER-1", 12, 2, "WORKER-1", 13, 3, "NATIVE_TRIP_BROKER_V10", "TERMINAL_PERSISTENCE_WORKER_V8", "TRADING_CHILD", "PARENT_GUARDIAN_V13", "TRADING_CHILD"),
        ("PIDFD_KERNEL_SELF_DEATH", "LEASE-1", h, h, "TIMER-1", "CLOCK_BOOTTIME", "SIGKILL", 1, h),
        (("PIDFD-trading_self", 10, 10), ("PIDFD-guardian", 11, 1), ("PIDFD-broker", 12, 2)),
        (3, ("MFD_CLOEXEC",), ("F_SEAL_SHRINK",), ("F_SEAL_GROW",), ("F_SEAL_SEAL",), "READ_WRITE", "READ_ONLY", "READ_WRITE", "READ_ONLY"),
        ("SIGNAL-1", h, h, h),
        ("EVENTFD-G", "EVENTFD-B", (("CHANNEL-1", "A_TO_B", "TRADING_CHILD", "NATIVE_TRIP_BROKER_V10", (10, 0, 0), h, 12, h, h, h, h, h, h, h, h), ("CHANNEL-2", "A_TO_B", "TRADING_CHILD", "NATIVE_TRIP_BROKER_V10", (10, 0, 0), h, 12, h, h, h, h, h, h, h, h), ("CHANNEL-3", "A_TO_B", "TRADING_CHILD", "NATIVE_TRIP_BROKER_V10", (10, 0, 0), h, 12, h, h, h, h, h, h, h, h), ("CHANNEL-4", "A_TO_B", "TRADING_CHILD", "NATIVE_TRIP_BROKER_V10", (10, 0, 0), h, 12, h, h, h, h, h, h, h, h), ("CHANNEL-5", "A_TO_B", "TRADING_CHILD", "NATIVE_TRIP_BROKER_V10", (10, 0, 0), h, 12, h, h, h, h, h, h, h, h), ("CHANNEL-6", "A_TO_B", "TRADING_CHILD", "NATIVE_TRIP_BROKER_V10", (10, 0, 0), h, 12, h, h, h, h, h, h, h, h))),
        ("LISTENER-1", "NOTIFY-1", "NATIVE_TRIP_BROKER_V10", h, "BTF-1", ("P-1",), ("M-1",), ("L-1",), ("/synthetic/pin",), ("C-1",), ("file_open", "file_permission", "socket_connect", "socket_sendmsg", "task_kill", "bprm_check_security"), h, h, (), h, h),
        ("TRADING_CHILD", "TERMINAL_PERSISTENCE_WORKER_V8"),
        (10, "CLOCK_BOOTTIME", 25, 5, 5, 25, 100),
        ("PIPE-R", "PIPE-W", 1, 4096, "PARENT_GUARDIAN_V13"),
        (2, 1, 1),
    )
    expected_completion = ("DIRECT", "NONE", "NONE", "NONE", "PROCESS-1", "GENESIS-1", h) if trusted[0] == "RP" else ("RECOVERED_AFTER_PREPARE", "AUTH-1", "CONSUME-1", "START-1", "PROCESS-1", "GENESIS-1", h)
    expected_static = (*common[:10], expected_completion, common[10])
    if actual_static != expected_static:
        reject("PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID", "Monitoring static OPEN/profile binding differs")

    group_results, close_reason = derive_groups(observation, raw["runtime_session_status"])
    expected_restart = {"NOT_REQUIRED"} if raw["report_operation"] in {"MONITOR_ONLY", "ATOMIC_GENESIS", "LEGACY_TO_PEE", "PEE_TO_LEGACY"} else {"VALID"}
    owner_status_valid = safety["legacy_exit_only_status"] == "NOT_APPLICABLE" if raw["owner_epoch"] == "PEE" else safety["legacy_exit_only_status"] in {"REQUIRED", "ACTIVE", "COMPLETE"}
    if safety["restart_authorization_status"] not in expected_restart or not owner_status_valid:
        group_results = (*group_results[:-1], "FAIL")
    lag = raw["atomic_journal_sequence"] - raw["projection_cursor_sequence"]
    reasons = []
    hard_fail = False
    def add_reason(reason):
        if reason not in reasons:
            reasons.append(reason)
    if raw["runtime_session_status"] in {"OPEN_UNCLEAN", "CLOSED_UNCLEAN"}:
        add_reason("PEE_IU4_RUNTIME_SESSION_UNCLEAN"); hard_fail = True
    if raw["open_prepare_count"]:
        add_reason("PEE_IU4_AUTHORITY_PREPARE_COMPLETION_REQUIRED"); hard_fail = True
    if raw["authority_root_ancestry_result"] != "PASS":
        add_reason("PEE_IU4_AUTHORITY_ROOT_MISMATCH"); hard_fail = True
    reason_map = (
        "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "PEE_IU4_TERMINAL_GUARDIAN_INVALID",
        "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "PEE_IU4_TERMINAL_CONTROL_WORD_CONFLICT",
        "PEE_IU4_TERMINAL_SIGNAL_ENVELOPE_INVALID", "PEE_IU4_TERMINAL_TRIP_CHANNEL_INVALID",
        "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID", None,
        "PEE_IU4_TERMINAL_GUARDIAN_INVALID", "PEE_IU4_TERMINAL_FAILSTOP_REAP_PENDING",
        "PEE_IU4_GENESIS_PROVENANCE_INVALID", "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH",
    )
    index = 0
    for result in group_results:
        if index == 7:
            if close_reason != "NONE": add_reason(close_reason)
            if result == "FAIL": hard_fail = True
        elif result == "FAIL":
            add_reason(reason_map[index]); hard_fail = True
        index += 1
    if lag: add_reason("PEE_IU4_PROJECTION_LAG")
    if raw["authorization_valid"] is not True:
        add_reason("PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH"); hard_fail = True
    if raw["terminal_gap_status"] in {"PENDING", "FAILED"}:
        add_reason("PEE_IU4_TERMINAL_GAP_RECONCILIATION_REQUIRED"); hard_fail = True
    overall = "FAIL" if hard_fail else "WARN" if lag or "WARN" in group_results else "PASS"
    entry = "AVAILABLE" if raw["owner_epoch"] == "PEE" and not hard_fail and not lag and safety["entry_allowed"] is True else "BLOCKED"
    exit_result = "AVAILABLE" if raw["owner_epoch"] == "PEE" and safety["exit_evaluation_allowed"] is True else "BLOCKED" if raw["owner_epoch"] == "PEE" else "NOT_APPLICABLE"

    if mode == "DERIVE":
        raw["projection_lag_transactions"] = lag
        raw["terminal_monitoring_observation_id"] = observation["terminal_monitoring_observation_id"]
        raw["terminal_monitoring_observation_fingerprint"] = observation["observation_fingerprint"]
        raw["runtime_close_fsm_record"] = {key: close[key] for key in close}
        raw["runtime_close_fsm_reason_code"] = close_reason
        index = 0
        for name in group_fields:
            raw[name] = group_results[index]; index += 1
        raw["entry_capability_result"] = entry
        raw["exit_capability_result"] = exit_result
        raw["overall_result"] = overall
        raw["reason_codes"] = [*reasons]
    else:
        supplied_groups = (*((raw[name]) for name in group_fields),)
        if (
            raw["projection_lag_transactions"] != lag
            or raw["terminal_monitoring_observation_id"] != observation["terminal_monitoring_observation_id"]
            or raw["terminal_monitoring_observation_fingerprint"] != observation["observation_fingerprint"]
            or raw["runtime_close_fsm_record"] != close
            or raw["runtime_close_fsm_reason_code"] != close_reason
            or supplied_groups != group_results
            or raw["entry_capability_result"] != entry
            or raw["exit_capability_result"] != exit_result
            or raw["overall_result"] != overall
            or raw["reason_codes"] != [*reasons]
        ):
            reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring result derivation differs")

    if raw["schema_version"] != 1 or raw["artifact_type"] != "iu4_recovery_monitoring_report_v1":
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring schema differs")
    if raw["owner_epoch"] not in {"LEGACY", "PEE"} or raw["report_operation"] not in {"MONITOR_ONLY", "ATOMIC_GENESIS", "LEGACY_TO_PEE", "PEE_TO_LEGACY", "RECOVER_AND_RESTART", "COMPLETE_AUTHORITY_PREPARE", "RECONCILE_TERMINAL_GAP"}:
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring owner/operation is invalid")
    if raw["runtime_session_status"] not in {"ABSENT", "OPEN_CLEAN", "OPEN_UNCLEAN", "CLOSED_CLEAN", "CLOSED_UNCLEAN"}:
        reject("PEE_IU4_RUNTIME_SESSION_UNCLEAN", "monitoring Session status is invalid")
    if (
        (raw["runtime_session_id"], raw["runtime_session_open_record_fingerprint"], raw["authority_generation_id"], raw["authority_commit_anchor"], raw["atomic_root_fingerprint"])
        != (observation["runtime_session_id"], observation["runtime_session_open_record_fingerprint"], observation["authority_generation_id"], observation["authority_commit_anchor"], observation["atomic_root_fingerprint"])
    ):
        reject("PEE_IU4_AUTHORITY_ROOT_MISMATCH", "monitoring Observation root binding differs")
    if (
        liveness["terminal_gap_status"] != raw["terminal_gap_status"]
        or (raw["runtime_session_status"] == "ABSENT") != (observation["runtime_session_id"] == "NONE")
        or liveness["runtime_session_unclean"] != (raw["runtime_session_status"] in {"OPEN_UNCLEAN", "CLOSED_UNCLEAN"})
    ):
        reject("PEE_IU4_RUNTIME_SESSION_UNCLEAN", "monitoring Session/Terminal binding differs")
    if raw["runtime_session_status"] == "ABSENT":
        if (raw["runtime_session_id"], raw["runtime_session_open_record_fingerprint"]) != ("NONE", "NONE"):
            reject("PEE_IU4_RUNTIME_SESSION_UNCLEAN", "monitoring absent Session pair differs")
    elif not text_value(raw["runtime_session_id"]) or not sha_value(raw["runtime_session_open_record_fingerprint"]):
        reject("PEE_IU4_RUNTIME_SESSION_UNCLEAN", "monitoring Session pair is invalid")
    for name in ("authority_generation_id", "runtime_profile_id", "economics_profile_id", "entry_throttle_profile_id", "lifecycle_ledger_tip_event_id", "terminal_monitoring_observation_id", "profile_registry_id"):
        if not text_value(raw[name]): reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring identifier is invalid")
    for name in ("authority_commit_anchor", "atomic_root_fingerprint", "lifecycle_root_inventory_fingerprint", "atomic_root_inventory_fingerprint", "projection_root_inventory_fingerprint", "runtime_profile_fingerprint", "profile_registry_fingerprint", "economics_profile_fingerprint", "entry_throttle_profile_fingerprint", "runtime_control_fingerprint", "lifecycle_ledger_tip_fingerprint", "atomic_snapshot_fingerprint", "s2_fingerprint", "account_fingerprint", "throttle_fingerprint", "loss_cluster_fingerprint", "s4_fingerprint", "entry_quote_fingerprint", "progress_cursor_fingerprint", "terminal_monitoring_observation_fingerprint"):
        if not sha_value(raw[name]): reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring fingerprint is invalid")
    if exact_type(raw["authorization_valid"]) is not boolean_type or not integer_value(raw["open_prepare_count"]) or not integer_value(raw["atomic_journal_sequence"]) or not integer_value(raw["projection_cursor_sequence"]):
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring scalar is invalid")
    if raw["atomic_journal_sequence"] == 0:
        if raw["atomic_journal_head"] != "EMPTY": reject("PEE_IU4_AUTHORITY_ROOT_MISMATCH", "monitoring Journal head differs")
    elif not sha_value(raw["atomic_journal_head"]): reject("PEE_IU4_AUTHORITY_ROOT_MISMATCH", "monitoring Journal head is invalid")
    if raw["authority_root_ancestry_result"] not in {"PASS", "FAIL"} or raw["terminal_gap_status"] not in {"NONE", "PENDING", "COMPLETE", "FAILED"}:
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring authority/Gap result is invalid")
    manifest_absent = raw["handoff_or_genesis_manifest_id"] == "NONE" or raw["handoff_or_genesis_manifest_fingerprint"] == "NONE"
    if manifest_absent:
        if (raw["handoff_or_genesis_manifest_id"], raw["handoff_or_genesis_manifest_fingerprint"]) != ("NONE", "NONE") or not (raw["owner_epoch"] == "LEGACY" and raw["report_operation"] == "MONITOR_ONLY" and raw["open_prepare_count"] == 0):
            reject("PEE_IU4_HANDOFF_GENESIS_REQUIRED", "monitoring absent manifest pair differs")
    elif not text_value(raw["handoff_or_genesis_manifest_id"]) or not sha_value(raw["handoff_or_genesis_manifest_fingerprint"]):
        reject("PEE_IU4_HANDOFF_GENESIS_REQUIRED", "monitoring manifest pair is invalid")
    cursor_absent = raw["projection_cursor_id"] == "NONE" or raw["projection_cursor_fingerprint"] == "NONE"
    if cursor_absent:
        if (raw["projection_cursor_id"], raw["projection_cursor_fingerprint"], raw["projection_cursor_sequence"], raw["projection_cursor_journal_head"]) != ("NONE", "NONE", 0, "EMPTY"):
            reject("PEE_IU4_PROJECTION_LAG", "monitoring absent Cursor pair differs")
    elif not text_value(raw["projection_cursor_id"]) or not sha_value(raw["projection_cursor_fingerprint"]) or not integer_value(raw["projection_cursor_sequence"], 1) or not sha_value(raw["projection_cursor_journal_head"]):
        reject("PEE_IU4_PROJECTION_LAG", "monitoring Cursor pair is invalid")
    if lag < 0: reject("PEE_IU4_PROJECTION_LAG", "Projection cursor is ahead")
    if not utc_value(raw["reported_at_utc"]): reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring report time is invalid")

    if mode in {"DERIVE", "ADDRESS"}:
        material = {name: raw[name] for name in report_fields if name not in {"monitoring_report_id", "report_fingerprint"}}
        report_id = "IU4-RECOVERY-MONITORING-REPORT-V1-" + sha256(material)
        raw["monitoring_report_id"] = report_id
        material["monitoring_report_id"] = report_id
        raw["report_fingerprint"] = sha256(material)
        raw["reason_codes"] = (*raw["reason_codes"],)
        return raw
    material = {name: raw[name] for name in report_fields if name not in {"monitoring_report_id", "report_fingerprint"}}
    expected_report_id = "IU4-RECOVERY-MONITORING-REPORT-V1-" + sha256(material)
    if raw["monitoring_report_id"] != expected_report_id:
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring report ID differs")
    material["monitoring_report_id"] = expected_report_id
    if raw["report_fingerprint"] != sha256(material):
        reject("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring report fingerprint differs")
    if mode == "CONSTRUCT":
        storage = []
        for name in report_fields:
            value = raw[name]
            if name in nested_report_fields:
                value = freeze(value)
            elif name == "reason_codes":
                value = (*value,)
            storage.append(value)
        return tuple_new(report_type, (*storage,))
    return {name: raw[name] for name in report_fields}


def _immutable_monitoring_report_build(factory_authority, cls, **values):
    pinned_report_type, constructor_authority = factory_authority
    if cls is not pinned_report_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "monitoring build type is not exact",
        )

    tuple_type = ().__class__
    dict_type = {}.__class__
    list_type = [].__class__
    text_type = "".__class__
    integer_type = (0).__class__
    boolean_type = True.__class__
    exact_type = tuple_type.__class__

    field_names = (
        "schema_version", "artifact_type", "monitoring_report_id", "runtime_session_id", "runtime_session_open_record_fingerprint", "authority_generation_id", "authority_commit_anchor", "owner_epoch", "report_operation", "atomic_root_fingerprint", "lifecycle_root_inventory_fingerprint", "atomic_root_inventory_fingerprint", "projection_root_inventory_fingerprint", "authorization_valid", "runtime_profile_id", "runtime_profile_fingerprint", "runtime_profile_anchor_record", "profile_registry_id", "profile_registry_fingerprint", "economics_profile_id", "economics_profile_fingerprint", "entry_throttle_profile_id", "entry_throttle_profile_fingerprint", "runtime_control_fingerprint", "lifecycle_ledger_tip_event_id", "lifecycle_ledger_tip_fingerprint", "open_prepare_count", "runtime_session_status", "handoff_or_genesis_manifest_id", "handoff_or_genesis_manifest_fingerprint", "atomic_journal_sequence", "atomic_journal_head", "atomic_snapshot_fingerprint", "authority_root_ancestry_result", "projection_cursor_id", "projection_cursor_fingerprint", "projection_cursor_sequence", "projection_cursor_journal_head", "projection_lag_transactions", "s2_fingerprint", "account_fingerprint", "throttle_fingerprint", "loss_cluster_fingerprint", "s4_fingerprint", "entry_quote_fingerprint", "progress_cursor_fingerprint", "terminal_gap_status", "terminal_monitoring_observation_id", "terminal_monitoring_observation_fingerprint", "terminal_monitoring_observation_record", "role_readiness_result", "lease_and_self_death_result", "pidfd_targets_result", "control_word_and_memfd_result", "signal_envelope_result", "runtime_channels_result", "seccomp_lsm_capability_result", "runtime_close_fsm_record", "runtime_close_fsm_result", "runtime_close_fsm_reason_code", "heartbeat_and_budgets_result", "failstop_and_terminal_gap_result", "completion_provenance_result", "safety_resource_schema_result", "entry_capability_result", "exit_capability_result", "overall_result", "reason_codes", "reported_at_utc", "report_fingerprint",
    )
    required = []
    for name in field_names:
        if name not in {"schema_version", "artifact_type", "monitoring_report_id", "report_fingerprint"}:
            required.append(name)
    actual_count = 0
    required_count = 0
    for _name in required:
        required_count += 1
    exact = exact_type(values) is dict_type
    if exact:
        for name in values:
            actual_count += 1
            if name not in required:
                exact = False
    if not exact or actual_count != required_count:
        raise IU4RecoveryProjectionError("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring build fields differ")
    for name in (
        "runtime_profile_anchor_record",
        "terminal_monitoring_observation_record",
        "runtime_close_fsm_record",
    ):
        if exact_type(values[name]) is not dict_type:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                "monitoring public nested record is not an exact mapping",
            )
    if exact_type(values["reason_codes"]) is not tuple_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            "monitoring public reasons are not immutable",
        )

    def count(value):
        result = 0
        for _item in value: result += 1
        return result

    def encode(value):
        value_type = exact_type(value)
        if value is None: return "null"
        if value_type is boolean_type: return "true" if value else "false"
        if value_type is integer_type: return f"{value}"
        if value_type is text_type:
            result = '"'
            for char in value:
                if char == '"': result += '\\"'
                elif char == "\\": result += "\\\\"
                elif char < " " or char > "~":
                    raise IU4RecoveryProjectionError("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring string is not canonical ASCII")
                else: result += char
            return result + '"'
        if value_type in (list_type, tuple_type):
            return "[" + ",".join(encode(item) for item in value) + "]"
        if value_type is dict_type:
            keys = []
            for key in value:
                if exact_type(key) is not text_type:
                    raise IU4RecoveryProjectionError("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring key is not exact")
                keys.append(key)
            keys.sort()
            return "{" + ",".join(encode(key) + ":" + encode(value[key]) for key in keys) + "}"
        raise IU4RecoveryProjectionError("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring build value is not canonical")

    def sha256(value):
        message = []
        bit_length = 0
        for byte in encode(value).encode("ascii"):
            message.append(byte); bit_length += 8
        message.append(128)
        while count(message) % 64 != 56: message.append(0)
        for shift in (56, 48, 40, 32, 24, 16, 8, 0): message.append((bit_length >> shift) & 255)
        state = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
        constants = (0x428A2F98,0x71374491,0xB5C0FBCF,0xE9B5DBA5,0x3956C25B,0x59F111F1,0x923F82A4,0xAB1C5ED5,0xD807AA98,0x12835B01,0x243185BE,0x550C7DC3,0x72BE5D74,0x80DEB1FE,0x9BDC06A7,0xC19BF174,0xE49B69C1,0xEFBE4786,0x0FC19DC6,0x240CA1CC,0x2DE92C6F,0x4A7484AA,0x5CB0A9DC,0x76F988DA,0x983E5152,0xA831C66D,0xB00327C8,0xBF597FC7,0xC6E00BF3,0xD5A79147,0x06CA6351,0x14292967,0x27B70A85,0x2E1B2138,0x4D2C6DFC,0x53380D13,0x650A7354,0x766A0ABB,0x81C2C92E,0x92722C85,0xA2BFE8A1,0xA81A664B,0xC24B8B70,0xC76C51A3,0xD192E819,0xD6990624,0xF40E3585,0x106AA070,0x19A4C116,0x1E376C08,0x2748774C,0x34B0BCB5,0x391C0CB3,0x4ED8AA4A,0x5B9CCA4F,0x682E6FF3,0x748F82EE,0x78A5636F,0x84C87814,0x8CC70208,0x90BEFFFA,0xA4506CEB,0xBEF9A3F7,0xC67178F2)
        def rotate(value, bits): return ((value >> bits) | (value << (32 - bits))) & 0xFFFFFFFF
        offset = 0
        while offset < count(message):
            words = []
            index = 0
            while index < 16:
                start = offset + index * 4
                words.append((message[start] << 24) | (message[start + 1] << 16) | (message[start + 2] << 8) | message[start + 3]); index += 1
            while index < 64:
                s0 = rotate(words[index - 15], 7) ^ rotate(words[index - 15], 18) ^ (words[index - 15] >> 3)
                s1 = rotate(words[index - 2], 17) ^ rotate(words[index - 2], 19) ^ (words[index - 2] >> 10)
                words.append((words[index - 16] + s0 + words[index - 7] + s1) & 0xFFFFFFFF); index += 1
            a,b,c,d,e,f,g,h = state
            index = 0
            while index < 64:
                t1 = (h + (rotate(e,6)^rotate(e,11)^rotate(e,25)) + ((e&f)^((~e)&g)) + constants[index] + words[index]) & 0xFFFFFFFF
                t2 = ((rotate(a,2)^rotate(a,13)^rotate(a,22)) + ((a&b)^(a&c)^(b&c))) & 0xFFFFFFFF
                h,g,f,e,d,c,b,a = g,f,e,(d+t1)&0xFFFFFFFF,c,b,a,(t1+t2)&0xFFFFFFFF; index += 1
            state = [(state[0]+a)&0xFFFFFFFF,(state[1]+b)&0xFFFFFFFF,(state[2]+c)&0xFFFFFFFF,(state[3]+d)&0xFFFFFFFF,(state[4]+e)&0xFFFFFFFF,(state[5]+f)&0xFFFFFFFF,(state[6]+g)&0xFFFFFFFF,(state[7]+h)&0xFFFFFFFF]
            offset += 64
        digits = "0123456789abcdef"
        result = ""
        for word in state:
            for shift in (28,24,20,16,12,8,4,0): result += digits[(word >> shift) & 15]
        return result

    addressed = {name: values[name] for name in values}
    addressed["schema_version"] = 1
    addressed["artifact_type"] = "iu4_recovery_monitoring_report_v1"
    material = {name: addressed[name] for name in field_names if name not in {"monitoring_report_id", "report_fingerprint"}}
    report_id = "IU4-RECOVERY-MONITORING-REPORT-V1-" + sha256(material)
    addressed["monitoring_report_id"] = report_id
    material["monitoring_report_id"] = report_id
    addressed["report_fingerprint"] = sha256(material)
    instance = constructor_authority(pinned_report_type, **addressed)
    if exact_type(instance) is not pinned_report_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "monitoring build returned a non-exact report",
        )
    return instance


def _immutable_monitoring_report_from_record(factory_authority, cls, record):
    pinned_report_type, constructor_authority = factory_authority
    if cls is not pinned_report_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "monitoring record type is not exact",
        )

    tuple_type = ().__class__
    dict_type = {}.__class__
    list_type = [].__class__
    text_type = "".__class__
    exact_type = tuple_type.__class__
    fields_literal = (
        "schema_version", "artifact_type", "monitoring_report_id", "runtime_session_id", "runtime_session_open_record_fingerprint", "authority_generation_id", "authority_commit_anchor", "owner_epoch", "report_operation", "atomic_root_fingerprint", "lifecycle_root_inventory_fingerprint", "atomic_root_inventory_fingerprint", "projection_root_inventory_fingerprint", "authorization_valid", "runtime_profile_id", "runtime_profile_fingerprint", "runtime_profile_anchor_record", "profile_registry_id", "profile_registry_fingerprint", "economics_profile_id", "economics_profile_fingerprint", "entry_throttle_profile_id", "entry_throttle_profile_fingerprint", "runtime_control_fingerprint", "lifecycle_ledger_tip_event_id", "lifecycle_ledger_tip_fingerprint", "open_prepare_count", "runtime_session_status", "handoff_or_genesis_manifest_id", "handoff_or_genesis_manifest_fingerprint", "atomic_journal_sequence", "atomic_journal_head", "atomic_snapshot_fingerprint", "authority_root_ancestry_result", "projection_cursor_id", "projection_cursor_fingerprint", "projection_cursor_sequence", "projection_cursor_journal_head", "projection_lag_transactions", "s2_fingerprint", "account_fingerprint", "throttle_fingerprint", "loss_cluster_fingerprint", "s4_fingerprint", "entry_quote_fingerprint", "progress_cursor_fingerprint", "terminal_gap_status", "terminal_monitoring_observation_id", "terminal_monitoring_observation_fingerprint", "terminal_monitoring_observation_record", "role_readiness_result", "lease_and_self_death_result", "pidfd_targets_result", "control_word_and_memfd_result", "signal_envelope_result", "runtime_channels_result", "seccomp_lsm_capability_result", "runtime_close_fsm_record", "runtime_close_fsm_result", "runtime_close_fsm_reason_code", "heartbeat_and_budgets_result", "failstop_and_terminal_gap_result", "completion_provenance_result", "safety_resource_schema_result", "entry_capability_result", "exit_capability_result", "overall_result", "reason_codes", "reported_at_utc", "report_fingerprint",
    )
    if exact_type(record) is not dict_type:
        raise IU4RecoveryProjectionError("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring record/type is not exact")
    actual_count = 0
    exact = True
    for key in record:
        actual_count += 1
        if exact_type(key) is not text_type or key not in fields_literal:
            exact = False
    if not exact or actual_count != 70:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            "monitoring record fields are missing or unknown",
        )
    values = {name: record[name] for name in fields_literal}
    if exact_type(values["reason_codes"]) is not list_type:
        raise IU4RecoveryProjectionError("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "monitoring reasons are not a canonical array")
    values["reason_codes"] = (*values["reason_codes"],)
    instance = constructor_authority(pinned_report_type, **values)
    if exact_type(instance) is not pinned_report_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "monitoring record construction returned a non-exact report",
        )
    return instance


def _immutable_monitoring_report_getattribute(self, name):
    tuple_type = ().__class__
    text_type = "".__class__
    exact_type = tuple_type.__class__
    object_type = exact_type.__base__
    raw_getattribute = object_type.__getattribute__
    tuple_item = tuple_type.__getitem__
    if exact_type(name) is text_type:
        fields_literal = (
            "schema_version", "artifact_type", "monitoring_report_id", "runtime_session_id", "runtime_session_open_record_fingerprint", "authority_generation_id", "authority_commit_anchor", "owner_epoch", "report_operation", "atomic_root_fingerprint", "lifecycle_root_inventory_fingerprint", "atomic_root_inventory_fingerprint", "projection_root_inventory_fingerprint", "authorization_valid", "runtime_profile_id", "runtime_profile_fingerprint", "runtime_profile_anchor_record", "profile_registry_id", "profile_registry_fingerprint", "economics_profile_id", "economics_profile_fingerprint", "entry_throttle_profile_id", "entry_throttle_profile_fingerprint", "runtime_control_fingerprint", "lifecycle_ledger_tip_event_id", "lifecycle_ledger_tip_fingerprint", "open_prepare_count", "runtime_session_status", "handoff_or_genesis_manifest_id", "handoff_or_genesis_manifest_fingerprint", "atomic_journal_sequence", "atomic_journal_head", "atomic_snapshot_fingerprint", "authority_root_ancestry_result", "projection_cursor_id", "projection_cursor_fingerprint", "projection_cursor_sequence", "projection_cursor_journal_head", "projection_lag_transactions", "s2_fingerprint", "account_fingerprint", "throttle_fingerprint", "loss_cluster_fingerprint", "s4_fingerprint", "entry_quote_fingerprint", "progress_cursor_fingerprint", "terminal_gap_status", "terminal_monitoring_observation_id", "terminal_monitoring_observation_fingerprint", "terminal_monitoring_observation_record", "role_readiness_result", "lease_and_self_death_result", "pidfd_targets_result", "control_word_and_memfd_result", "signal_envelope_result", "runtime_channels_result", "seccomp_lsm_capability_result", "runtime_close_fsm_record", "runtime_close_fsm_result", "runtime_close_fsm_reason_code", "heartbeat_and_budgets_result", "failstop_and_terminal_gap_result", "completion_provenance_result", "safety_resource_schema_result", "entry_capability_result", "exit_capability_result", "overall_result", "reason_codes", "reported_at_utc", "report_fingerprint",
        )
        index = 0
        for field_name in fields_literal:
            if name == field_name:
                return tuple_item(self, index)
            index += 1
    return raw_getattribute(self, name)


def _immutable_monitoring_report_init(self, **constructor_values):
    return None


def _immutable_monitoring_report_new(authority_types, cls, **constructor_values):
    tuple_type = ().__class__
    exact_type = tuple_type.__class__
    report_type, authority = authority_types
    if cls is not report_type or exact_type(cls) is not exact_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "monitoring report type is not exact",
        )
    instance = authority(cls, **constructor_values)
    if exact_type(instance) is not report_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "monitoring constructor returned a non-exact report",
        )
    return instance


def _immutable_monitoring_report_storage_view(self):
    tuple_type = ().__class__
    tuple_count = tuple_type.__len__
    tuple_item = tuple_type.__getitem__
    items = []
    index = 0
    while index < tuple_count(self):
        items.append(tuple_item(self, index))
        index += 1
    return tuple_type(items)


@dataclass(frozen=True, init=False)
class IU4RecoveryMonitoringReportV1(tuple, _ContentAddressedArtifact):
    __slots__ = ()
    schema_version: int
    artifact_type: str
    monitoring_report_id: str
    runtime_session_id: str
    runtime_session_open_record_fingerprint: str
    authority_generation_id: str
    authority_commit_anchor: str
    owner_epoch: str
    report_operation: str
    atomic_root_fingerprint: str
    lifecycle_root_inventory_fingerprint: str
    atomic_root_inventory_fingerprint: str
    projection_root_inventory_fingerprint: str
    authorization_valid: bool
    runtime_profile_id: str
    runtime_profile_fingerprint: str
    runtime_profile_anchor_record: dict[str, Any]
    profile_registry_id: str
    profile_registry_fingerprint: str
    economics_profile_id: str
    economics_profile_fingerprint: str
    entry_throttle_profile_id: str
    entry_throttle_profile_fingerprint: str
    runtime_control_fingerprint: str
    lifecycle_ledger_tip_event_id: str
    lifecycle_ledger_tip_fingerprint: str
    open_prepare_count: int
    runtime_session_status: str
    handoff_or_genesis_manifest_id: str
    handoff_or_genesis_manifest_fingerprint: str
    atomic_journal_sequence: int
    atomic_journal_head: str
    atomic_snapshot_fingerprint: str
    authority_root_ancestry_result: str
    projection_cursor_id: str
    projection_cursor_fingerprint: str
    projection_cursor_sequence: int
    projection_cursor_journal_head: str
    projection_lag_transactions: int
    s2_fingerprint: str
    account_fingerprint: str
    throttle_fingerprint: str
    loss_cluster_fingerprint: str
    s4_fingerprint: str
    entry_quote_fingerprint: str
    progress_cursor_fingerprint: str
    terminal_gap_status: str
    terminal_monitoring_observation_id: str
    terminal_monitoring_observation_fingerprint: str
    terminal_monitoring_observation_record: tuple[Any, ...]
    role_readiness_result: str
    lease_and_self_death_result: str
    pidfd_targets_result: str
    control_word_and_memfd_result: str
    signal_envelope_result: str
    runtime_channels_result: str
    seccomp_lsm_capability_result: str
    runtime_close_fsm_record: dict[str, Any]
    runtime_close_fsm_result: str
    runtime_close_fsm_reason_code: str
    heartbeat_and_budgets_result: str
    failstop_and_terminal_gap_result: str
    completion_provenance_result: str
    safety_resource_schema_result: str
    entry_capability_result: str
    exit_capability_result: str
    overall_result: str
    reason_codes: tuple[str, ...]
    reported_at_utc: str
    report_fingerprint: str

    ARTIFACT_TYPE = "iu4_recovery_monitoring_report_v1"
    ID_FIELD = "monitoring_report_id"
    FINGERPRINT_FIELD = "report_fingerprint"
    ID_PREFIX = "IU4-RECOVERY-MONITORING-REPORT-V1-"
    TUPLE_FIELDS = frozenset({"reason_codes"})

    def group_results(self) -> tuple[str, ...]:
        return (
            self.role_readiness_result, self.lease_and_self_death_result,
            self.pidfd_targets_result, self.control_word_and_memfd_result,
            self.signal_envelope_result, self.runtime_channels_result,
            self.seccomp_lsm_capability_result, self.runtime_close_fsm_result,
            self.heartbeat_and_budgets_result,
            self.failstop_and_terminal_gap_result,
            self.completion_provenance_result,
            self.safety_resource_schema_result,
        )

    __getattribute__ = _immutable_monitoring_report_getattribute
    __init__ = _immutable_monitoring_report_init
    _authority_storage = property(_immutable_monitoring_report_storage_view)
    __post_init__ = _immutable_monitoring_report_authority
    _validate_specific = _immutable_monitoring_report_authority
    to_record = _immutable_monitoring_report_authority


_monitoring_report_new_authority = (
    IU4RecoveryMonitoringReportV1,
    _immutable_monitoring_report_authority,
)
IU4RecoveryMonitoringReportV1.__new__ = _immutable_monitoring_report_new.__get__(
    _monitoring_report_new_authority,
    _monitoring_report_new_authority.__class__,
)
del _monitoring_report_new_authority

_monitoring_report_build_authority = (
    IU4RecoveryMonitoringReportV1,
    _immutable_monitoring_report_authority,
)
IU4RecoveryMonitoringReportV1.build = classmethod(
    _immutable_monitoring_report_build.__get__(
        _monitoring_report_build_authority,
        _monitoring_report_build_authority.__class__,
    )
)
del _monitoring_report_build_authority

_monitoring_report_from_record_authority = (
    IU4RecoveryMonitoringReportV1,
    _immutable_monitoring_report_authority,
)
IU4RecoveryMonitoringReportV1.from_record = classmethod(
    _immutable_monitoring_report_from_record.__get__(
        _monitoring_report_from_record_authority,
        _monitoring_report_from_record_authority.__class__,
    )
)
del _monitoring_report_from_record_authority


def build_monitoring_report(
    authority_types, *, observation: IU4TerminalMonitoringObservationV1,
    owner_epoch: str,
    expected_runtime_session_id: str,
    expected_runtime_session_open_record_fingerprint: str,
    expected_authority_generation_id: str,
    expected_authority_commit_anchor: str,
    expected_atomic_root_fingerprint: str,
    report_operation: str, lifecycle_root_inventory_fingerprint: str,
    atomic_root_inventory_fingerprint: str, projection_root_inventory_fingerprint: str,
    authorization_valid: bool, runtime_profile_id: str,
    economics_profile_id: str, economics_profile_fingerprint: str,
    entry_throttle_profile_id: str, entry_throttle_profile_fingerprint: str,
    runtime_control_fingerprint: str, lifecycle_ledger_tip_event_id: str,
    lifecycle_ledger_tip_fingerprint: str, open_prepare_count: int,
    runtime_session_status: str, handoff_or_genesis_manifest_id: str,
    handoff_or_genesis_manifest_fingerprint: str, atomic_journal_sequence: int,
    atomic_journal_head: str, atomic_snapshot_fingerprint: str,
    authority_root_ancestry_result: str, projection_cursor_id: str,
    projection_cursor_fingerprint: str, projection_cursor_sequence: int,
    projection_cursor_journal_head: str, component_fingerprints: Mapping[str, str],
    terminal_gap_status: str, reported_at_utc: str,
    untrusted_profile_registry: object | None = None,
) -> IU4RecoveryMonitoringReportV1:
    report_type, observation_type, authority = authority_types
    tuple_type = ().__class__
    dict_type = {}.__class__
    list_type = [].__class__
    text_type = "".__class__
    integer_type = (0).__class__
    boolean_type = True.__class__
    exact_type = tuple_type.__class__
    object_type = exact_type.__base__
    raw_getattribute = object_type.__getattribute__

    def normalize_public(value):
        value_type = exact_type(value)
        if value is None or value_type in (text_type, integer_type, boolean_type):
            return value
        if value_type is list_type:
            normalized = []
            for item in value:
                normalized.append(normalize_public(item))
            return normalized
        if value_type is dict_type:
            normalized = {}
            for key in value:
                if exact_type(key) is not text_type:
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
                        "monitoring public mapping key is not exact text",
                    )
                normalized[key] = normalize_public(value[key])
            return normalized
        raise IU4RecoveryProjectionError(
            "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED",
            "monitoring public value is not canonical",
        )

    if exact_type(observation) is not observation_type:
        raise IU4RecoveryProjectionError("PEE_IU4_TERMINAL_GUARDIAN_INVALID", "monitoring requires exact Observation")
    observation_values = normalize_public(
        raw_getattribute(observation, "__dict__")
    )
    observation_field_names = (
        "schema_version", "artifact_type",
        "terminal_monitoring_observation_id", "runtime_session_id",
        "runtime_session_open_record_fingerprint", "authority_generation_id",
        "authority_commit_anchor", "atomic_root_fingerprint",
        "source_collector_id", "source_evidence_id", "source_evidence_sha256",
        "observation_sequence", "observed_at_utc", "role_readiness",
        "lease_and_self_death", "pidfd_targets", "control_word_and_memfd",
        "signal_envelope", "runtime_channels", "seccomp_lsm_capability",
        "runtime_close_fsm", "heartbeat_and_budgets",
        "failstop_and_terminal_gap", "completion_provenance",
        "safety_resource_schema", "observation_fingerprint",
    )
    observation_count = 0
    observation_names_exact = exact_type(observation_values) is dict_type
    if observation_names_exact:
        for name in observation_values:
            observation_count += 1
            if exact_type(name) is not text_type or name not in observation_field_names:
                observation_names_exact = False
    if not observation_names_exact or observation_count != 26:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_GUARDIAN_INVALID",
            "monitoring Observation storage is not exact",
        )
    expected_observation_bindings = (
        normalize_public(expected_runtime_session_id),
        normalize_public(expected_runtime_session_open_record_fingerprint),
        normalize_public(expected_authority_generation_id),
        normalize_public(expected_authority_commit_anchor),
        normalize_public(expected_atomic_root_fingerprint),
    )
    actual_observation_bindings = (
        observation_values["runtime_session_id"],
        observation_values["runtime_session_open_record_fingerprint"],
        observation_values["authority_generation_id"],
        observation_values["authority_commit_anchor"],
        observation_values["atomic_root_fingerprint"],
    )
    if expected_observation_bindings != actual_observation_bindings:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_AUTHORITY_ROOT_MISMATCH",
            "Monitoring Observation trusted root/session binding differs",
        )
    if untrusted_profile_registry is not None:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "caller-provided profile registries are untrusted and cannot authorize a report",
        )
    if exact_type(runtime_profile_id) is not text_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "runtime profile ID is not exact",
        )
    required_components = (
        "s2", "account", "throttle", "loss_cluster", "s4", "entry_quote",
        "progress_cursor",
    )
    component_fingerprints = normalize_public(component_fingerprints)
    component_count = 0
    components_exact = exact_type(component_fingerprints) is dict_type
    if components_exact:
        for name in component_fingerprints:
            component_count += 1
            if exact_type(name) is not text_type or name not in required_components:
                components_exact = False
    if not components_exact or component_count != 7:
        raise IU4RecoveryProjectionError("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "component fingerprints are incomplete")
    observation_record = {}
    for name in observation_field_names:
        value = observation_values[name]
        observation_record[name] = value
    values = {
        "runtime_session_id": observation_values["runtime_session_id"],
        "runtime_session_open_record_fingerprint": observation_values["runtime_session_open_record_fingerprint"],
        "authority_generation_id": observation_values["authority_generation_id"],
        "authority_commit_anchor": observation_values["authority_commit_anchor"],
        "owner_epoch": owner_epoch, "report_operation": report_operation,
        "atomic_root_fingerprint": observation_values["atomic_root_fingerprint"],
        "lifecycle_root_inventory_fingerprint": lifecycle_root_inventory_fingerprint,
        "atomic_root_inventory_fingerprint": atomic_root_inventory_fingerprint,
        "projection_root_inventory_fingerprint": projection_root_inventory_fingerprint,
        "authorization_valid": authorization_valid, "runtime_profile_id": runtime_profile_id,
        "economics_profile_id": economics_profile_id,
        "economics_profile_fingerprint": economics_profile_fingerprint,
        "entry_throttle_profile_id": entry_throttle_profile_id,
        "entry_throttle_profile_fingerprint": entry_throttle_profile_fingerprint,
        "runtime_control_fingerprint": runtime_control_fingerprint,
        "lifecycle_ledger_tip_event_id": lifecycle_ledger_tip_event_id,
        "lifecycle_ledger_tip_fingerprint": lifecycle_ledger_tip_fingerprint,
        "open_prepare_count": open_prepare_count, "runtime_session_status": runtime_session_status,
        "handoff_or_genesis_manifest_id": handoff_or_genesis_manifest_id,
        "handoff_or_genesis_manifest_fingerprint": handoff_or_genesis_manifest_fingerprint,
        "atomic_journal_sequence": atomic_journal_sequence, "atomic_journal_head": atomic_journal_head,
        "atomic_snapshot_fingerprint": atomic_snapshot_fingerprint,
        "authority_root_ancestry_result": authority_root_ancestry_result,
        "projection_cursor_id": projection_cursor_id,
        "projection_cursor_fingerprint": projection_cursor_fingerprint,
        "projection_cursor_sequence": projection_cursor_sequence,
        "projection_cursor_journal_head": projection_cursor_journal_head,
        "s2_fingerprint": component_fingerprints["s2"],
        "account_fingerprint": component_fingerprints["account"],
        "throttle_fingerprint": component_fingerprints["throttle"],
        "loss_cluster_fingerprint": component_fingerprints["loss_cluster"],
        "s4_fingerprint": component_fingerprints["s4"],
        "entry_quote_fingerprint": component_fingerprints["entry_quote"],
        "progress_cursor_fingerprint": component_fingerprints["progress_cursor"],
        "terminal_gap_status": terminal_gap_status,
        "terminal_monitoring_observation_record": observation_record,
        "reported_at_utc": reported_at_utc,
    }
    addressed = authority(("DERIVE", values))
    report = report_type(**addressed)
    if exact_type(report) is not report_type:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID",
            "monitoring builder returned a non-exact report",
        )
    authority(report)
    return report


_monitoring_report_authority_types = (
    IU4RecoveryMonitoringReportV1,
    IU4TerminalMonitoringObservationV1,
    _immutable_monitoring_report_authority,
)
build_monitoring_report = build_monitoring_report.__get__(
    _monitoring_report_authority_types,
    _monitoring_report_authority_types.__class__,
)
del _monitoring_report_authority_types


def classify_owner_state(owner_epoch: str, legacy_s2: str, atomic_s2: str) -> str:
    if owner_epoch not in {"LEGACY", "PEE"} or legacy_s2 not in {"FLAT", "OPEN"} or atomic_s2 not in {"FLAT", "OPEN"}:
        return "PEE_IU4_HANDOFF_GENESIS_REQUIRED"
    matrix = {
        ("LEGACY", "OPEN", "FLAT"): "LEGACY_EXIT_ONLY",
        ("LEGACY", "OPEN", "OPEN"): "PEE_IU4_HANDOFF_DUAL_OPEN_CONFLICT",
        ("LEGACY", "FLAT", "FLAT"): "HANDOFF_REQUIRED",
        ("LEGACY", "FLAT", "OPEN"): "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID",
        ("PEE", "FLAT", "OPEN"): "PEE_RESUME_CANDIDATE",
        ("PEE", "FLAT", "FLAT"): "PEE_FLAT_CANDIDATE",
        ("PEE", "OPEN", "OPEN"): "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID",
        ("PEE", "OPEN", "FLAT"): "PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID",
    }
    return matrix[(owner_epoch, legacy_s2, atomic_s2)]


def handoff_planned_generation_id(
    *, operation: str, source_authority_generation_id: str,
    source_authority_commit_anchor: str, approval_fingerprint: str,
    target_business_payload: Mapping[str, Any],
) -> str:
    """Self-reference-free I6 Handoff Generation derivation."""

    if operation not in {"LEGACY_TO_PEE", "PEE_TO_LEGACY"} or type(target_business_payload) is not dict:
        raise IU4RecoveryProjectionError("PEE_IU4_HANDOFF_SAFETY_CONFLICT", "invalid Handoff Generation input")
    _sha(source_authority_commit_anchor, "source_authority_commit_anchor")
    _sha(approval_fingerprint, "approval_fingerprint")
    material = {
        "schema_version": 1,
        "operation": operation,
        "source_authority_generation_id": _text(source_authority_generation_id, "source_authority_generation_id"),
        "source_authority_commit_anchor": source_authority_commit_anchor,
        "approval_fingerprint": approval_fingerprint,
        "target_business_payload_fingerprint": lifecycle_fingerprint(target_business_payload),
    }
    return "IU4-AUTHORITY-GENERATION-" + _hash(material)


def handoff_mapping_record(
    *,
    direction: str,
    source_snapshot: IU4LegacySafetySnapshotV1,
    target_business_fingerprint: str,
    target_core_fingerprint: str,
) -> dict[str, str]:
    if direction not in {"LEGACY_TO_PEE", "PEE_TO_LEGACY"}:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "invalid mapping direction"
        )
    if type(source_snapshot) is not IU4LegacySafetySnapshotV1:
        raise IU4RecoveryProjectionError(
            "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "mapping source requires exact Snapshot"
        )
    return {
        "direction": direction,
        "source_snapshot_id": source_snapshot.legacy_safety_snapshot_id,
        "source_snapshot_fingerprint": source_snapshot.snapshot_fingerprint,
        "position_fingerprint": source_snapshot.position_fingerprint,
        "risk_fingerprint": source_snapshot.risk_fingerprint,
        "loss_cluster_fingerprint": source_snapshot.loss_cluster_fingerprint,
        "throttle_fingerprint": source_snapshot.throttle_fingerprint,
        "progress_cursor_fingerprint": source_snapshot.progress_cursor_fingerprint,
        "target_business_fingerprint": _sha(
            target_business_fingerprint, "target_business_fingerprint"
        ),
        "target_core_fingerprint": _sha(
            target_core_fingerprint, "target_core_fingerprint"
        ),
    }


def _atomic_profile_bindings(state: Any) -> dict[str, str]:
    return {
        "runtime_control_profile_id": state.runtime_control_profile_id,
        "runtime_control_fingerprint": state.runtime_control_fingerprint,
        "loss_cluster_policy_id": state.loss_cluster_policy_id,
        "loss_cluster_policy_fingerprint": state.loss_cluster_policy_fingerprint,
        "economics_profile_id": state.account.economics_profile_id,
        "economics_config_fingerprint": state.account.config_fingerprint,
        "throttle_policy_profile_id": state.throttle.policy_profile_id,
        "throttle_policy_fingerprint": state.throttle.policy_fingerprint,
    }


def _atomic_component_fingerprints(state: Any) -> dict[str, str]:
    return {
        "position": state.position.state_fingerprint,
        "account": state.account.state_fingerprint,
        "throttle": state.throttle.state_fingerprint,
        "loss_cluster": state.loss_cluster.state_fingerprint,
        "progress_cursor": state.progress_cursor.cursor_fingerprint,
        "risk": state.risk.state_fingerprint,
        "entry_quote": NONE if state.entry_quote is None else state.entry_quote.quote_fingerprint,
        "state": state.state_fingerprint,
        "business": lifecycle_fingerprint(state.business_payload()),
        "core": lifecycle_fingerprint(state.core_payload()),
    }


def _absence_proof_sha256(kind: str, path: str) -> str:
    return _hash(
        {
            "absent": True,
            "artifact_kind": _text(kind, "artifact_kind"),
            "path": _path(path, "absence_path"),
            "schema_version": 1,
        }
    )


def _empty_journal_inventory_fingerprint(path: str) -> str:
    return _hash(
        {
            "entries": [],
            "journal_path": _path(path, "journal_path"),
            "schema_version": 1,
        }
    )


class IU4ProjectionPublisherV1:
    """Crash-safe, one-transaction-at-a-time compatibility publisher."""

    def __init__(self, caller_root_path: str) -> None:
        if type(caller_root_path) is not str:
            raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "caller root must be exact str")
        if not caller_root_path.startswith("/") or caller_root_path == "/" or caller_root_path.endswith("/") or "\x00" in caller_root_path or unicodedata.normalize("NFC", caller_root_path) != caller_root_path:
            raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "caller root spelling is unsafe")
        components = caller_root_path.split("/")[1:]
        if (
            any(component in {"", ".", ".."} for component in components)
            or caller_root_path != "/" + "/".join(components)
        ):
            raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "caller root is not canonical")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
        descriptor = next_descriptor = -1
        try:
            descriptor = os.open("/", flags)
            for component in components:
                next_descriptor = os.open(component, flags, dir_fd=descriptor)
                info = os.fstat(next_descriptor)
                if not stat.S_ISDIR(info.st_mode):
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_PROJECTION_LAG",
                        "caller root component is not a directory",
                    )
                _cleanup_descriptors_preserving_primary(
                    (descriptor,),
                    primary_active=False,
                    message="caller root traversal descriptor close failed",
                )
                descriptor = next_descriptor
                next_descriptor = -1
            identity = os.fstat(descriptor)
        except BaseException as exc:
            _cleanup_descriptors_preserving_primary(
                (next_descriptor, descriptor),
                primary_active=True,
                message="caller root traversal cleanup failed",
            )
            if _has_resource_cause(exc):
                self._raise_filesystem_error(
                    exc, "caller root traversal is unsafe"
                )
            raise
        self.caller_root_path = caller_root_path
        self._caller_root_fd = descriptor
        self._caller_root_identity = (
            identity.st_dev, identity.st_ino
        )
        self.projection_root = Path(caller_root_path + "/projection")
        self.records_root = self.projection_root / "records"
        self.cursor_path = self.projection_root / "projection_cursor_v1.json"
        self.lock_path = self.projection_root / ".projection_v1.lock"

    def __del__(self) -> None:
        descriptor = getattr(self, "_caller_root_fd", -1)
        if type(descriptor) is int and descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass
            self._caller_root_fd = -1

    @staticmethod
    def _topology_error(exc: OSError) -> bool:
        return exc.errno in {
            errno.ENOENT, errno.ENOTDIR, errno.ELOOP, errno.EEXIST,
            errno.EISDIR,
        }

    @classmethod
    def _raise_filesystem_error(cls, exc: BaseException, message: str) -> None:
        code = (
            "PEE_IU4_PROJECTION_LAG"
            if isinstance(exc, OSError) and cls._topology_error(exc)
            else "PEE_IU4_RESOURCE_EXHAUSTED"
        )
        raise IU4RecoveryProjectionError(code, message) from exc

    @staticmethod
    def _sync_fd(descriptor: int) -> None:
        os.fsync(descriptor)

    @classmethod
    def _close_fd(cls, descriptor: int, message: str) -> None:
        try:
            os.close(descriptor)
        except Exception as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", message
                ) from exc
            raise

    @classmethod
    def _open_directory_at(
        cls, parent_fd: int, name: str, *, create: bool,
    ) -> int:
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
        try:
            return os.open(name, flags, dir_fd=parent_fd)
        except FileNotFoundError:
            if not create:
                raise
        except BaseException as exc:
            if _has_resource_cause(exc):
                cls._raise_filesystem_error(
                    exc, f"Projection directory {name} is unsafe"
                )
            raise
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent_fd)
            cls._sync_fd(parent_fd)
            descriptor = os.open(name, flags, dir_fd=parent_fd)
            info = os.fstat(descriptor)
            if not stat.S_ISDIR(info.st_mode):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_PROJECTION_LAG",
                    f"Projection directory {name} is not a directory",
                )
        except BaseException as exc:
            if "descriptor" in locals():
                _cleanup_descriptors_preserving_primary(
                    (descriptor,),
                    primary_active=True,
                    message="Projection directory descriptor close failed",
                )
            if _has_resource_cause(exc):
                cls._raise_filesystem_error(
                    exc, f"Projection directory {name} is unsafe"
                )
            raise
        return descriptor

    def _open_tree(self, *, create: bool) -> tuple[int, int]:
        if self._caller_root_fd < 0:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_PROJECTION_LAG", "caller root descriptor is closed"
            )
        current = os.fstat(self._caller_root_fd)
        if (current.st_dev, current.st_ino) != self._caller_root_identity:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_PROJECTION_LAG", "caller root descriptor identity changed"
            )
        projection_fd = self._open_directory_at(
            self._caller_root_fd, "projection", create=create
        )
        try:
            records_fd = self._open_directory_at(
                projection_fd, "records", create=create
            )
        except BaseException:
            _cleanup_descriptors_preserving_primary(
                (projection_fd,),
                primary_active=True,
                message="Projection directory close failed",
            )
            raise
        return projection_fd, records_fd

    @classmethod
    def _open_regular_at(
        cls, directory_fd: int, name: str, flags: int, mode: int = 0o600,
    ) -> int:
        try:
            descriptor = os.open(
                name, flags | os.O_CLOEXEC | os.O_NOFOLLOW,
                mode, dir_fd=directory_fd,
            )
        except BaseException as exc:
            if _has_resource_cause(exc):
                cls._raise_filesystem_error(
                    exc, f"Projection file {name} is unsafe"
                )
            raise
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_PROJECTION_LAG", f"Projection file {name} is not regular"
                )
        except BaseException:
            _cleanup_descriptors_preserving_primary(
                (descriptor,),
                primary_active=True,
                message="Projection file descriptor close failed",
            )
            raise
        return descriptor

    @staticmethod
    def _read_descriptor(descriptor: int) -> bytes:
        os.lseek(descriptor, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)

    @classmethod
    def _read_regular_at(
        cls, directory_fd: int, name: str, *, allow_missing: bool = False,
    ) -> tuple[bytes, os.stat_result] | None:
        descriptor = -1
        try:
            descriptor = cls._open_regular_at(directory_fd, name, os.O_RDONLY)
        except IU4RecoveryProjectionError as exc:
            cause = exc.__cause__
            if (
                allow_missing and isinstance(cause, OSError)
                and cause.errno == errno.ENOENT
            ):
                return None
            raise
        try:
            before = os.fstat(descriptor)
            raw = cls._read_descriptor(descriptor)
            after = os.fstat(descriptor)
            if (
                (before.st_dev, before.st_ino, before.st_size)
                != (after.st_dev, after.st_ino, after.st_size)
                or len(raw) != after.st_size
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_PROJECTION_LAG", "Projection file changed during readback"
                )
            return raw, after
        except BaseException as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "Projection readback resource operation failed",
                ) from exc
            raise
        finally:
            _cleanup_descriptors_preserving_primary(
                (descriptor,),
                primary_active=sys.exc_info()[0] is not None,
                message="Projection read descriptor close failed",
            )

    @staticmethod
    def _write_descriptor(descriptor: int, data: bytes) -> None:
        offset = 0
        while offset < len(data):
            written = os.write(descriptor, data[offset:])
            if written <= 0:
                raise OSError("short Projection write")
            offset += written

    def initialize(self) -> None:
        projection_fd = records_fd = descriptor = -1
        try:
            projection_fd, records_fd = self._open_tree(create=True)
            descriptor = self._open_regular_at(
                projection_fd, ".projection_v1.lock", os.O_CREAT | os.O_RDWR
            )
            self._sync_fd(projection_fd)
        except Exception as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "Projection initialization failed",
                ) from exc
            if isinstance(exc, IU4RecoveryProjectionError):
                raise
            raise
        finally:
            _cleanup_descriptors_preserving_primary(
                (descriptor, records_fd, projection_fd),
                primary_active=sys.exc_info()[0] is not None,
                message="Projection initialization descriptor close failed",
            )

    def read_cursor(self) -> IU4ProjectionCursorV1 | None:
        projection_fd = records_fd = -1
        try:
            projection_fd, records_fd = self._open_tree(create=False)
        except FileNotFoundError:
            return None
        except BaseException as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "Projection Cursor tree open failed",
                ) from exc
            raise
        try:
            return self._read_cursor_at(projection_fd)
        except BaseException as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "Projection Cursor read failed",
                ) from exc
            raise
        finally:
            _cleanup_descriptors_preserving_primary(
                (records_fd, projection_fd),
                primary_active=sys.exc_info()[0] is not None,
                message="Projection Cursor directory close failed",
            )

    def _read_cursor_at(self, projection_fd: int) -> IU4ProjectionCursorV1 | None:
        item = self._read_regular_at(
            projection_fd, "projection_cursor_v1.json", allow_missing=True
        )
        if item is None:
            return None
        raw, _info = item
        try:
            value = json.loads(raw.decode("ascii"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "Projection Cursor is unreadable") from exc
        if raw != canonical_json_bytes(value) + b"\n":
            raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "Projection Cursor bytes are noncanonical")
        try:
            return IU4ProjectionCursorV1.from_record(value)
        except IU4RecoveryProjectionError as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_PROJECTION_LAG",
                "Projection Cursor schema is invalid",
            ) from exc

    def _inventory(self, operation_attempt_id: str) -> tuple[dict[str, Any], str]:
        projection_fd = records_fd = -1
        try:
            projection_fd, records_fd = self._open_tree(create=False)
            return self._inventory_at(
                projection_fd, records_fd, operation_attempt_id
            )
        except BaseException as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "Projection inventory read failed",
                ) from exc
            raise
        finally:
            _cleanup_descriptors_preserving_primary(
                (records_fd, projection_fd),
                primary_active=sys.exc_info()[0] is not None,
                message="Projection inventory directory close failed",
            )

    def _inventory_at(
        self, projection_fd: int, records_fd: int, operation_attempt_id: str,
    ) -> tuple[dict[str, Any], str]:
        _text(operation_attempt_id, "operation_attempt_id")
        entries: list[list[str]] = []
        allowed_unknown = {self.lock_path.name, self.cursor_path.name, f".projection_cursor_v1.tmp.{operation_attempt_id}"}
        for name in os.listdir(projection_fd):
            if name == "records":
                continue
            if name in allowed_unknown:
                info = os.stat(name, dir_fd=projection_fd, follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode):
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_PROJECTION_LAG", "invalid projection root entry"
                    )
                continue
            raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "unknown projection root entry")
        for name in os.listdir(records_fd):
            match = re.fullmatch(
                r"([0-9]{20})_(IU4-COMPATIBILITY-PROJECTION-V1-[0-9a-f]{64})\.json",
                name,
            )
            if match is None:
                raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "invalid projection inventory entry")
            item = self._read_regular_at(records_fd, name)
            if item is None:
                raise AssertionError("required Projection inventory entry disappeared")
            raw, info = item
            try:
                record = json.loads(raw.decode("ascii"))
                projection = IU4CompatibilityProjectionV1.from_record(record)
            except (UnicodeError, json.JSONDecodeError, IU4RecoveryProjectionError) as exc:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_PROJECTION_LAG", "invalid Projection record in inventory"
                ) from exc
            if (
                raw != canonical_json_bytes(record) + b"\n"
                or int(match.group(1)) != projection.atomic_transaction_sequence
                or match.group(2) != projection.projection_id
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_PROJECTION_LAG", "Projection filename/content binding differs"
                )
            relative = f"records/{name}"
            entries.append([relative, "REGULAR", f"{stat.S_IMODE(info.st_mode):04o}", str(info.st_size), hashlib.sha256(raw).hexdigest()])
        entries.sort(key=lambda row: row[0].encode("utf-8"))
        value = {
            "entries": entries,
            "observation_point": "AFTER_OUTPUT_READBACK_BEFORE_CURSOR_TEMP_CREATE",
            "projection_root_realpath_sha256": projection_root_realpath_sha256(str(self.projection_root)),
            "schema_version": 1,
        }
        return value, _hash(value)

    def publish(
        self, *, transaction: Any, projected_legacy_safety: IU4LegacySafetySnapshotV1,
        operation_attempt_id: str, published_at_utc: str, fault_point: str = "",
    ) -> IU4ProjectionCursorV1:
        from live_l1.state.paper_atomic_coordinator import AtomicPaperTransactionV2

        if type(transaction) is not AtomicPaperTransactionV2 or type(projected_legacy_safety) is not IU4LegacySafetySnapshotV1:
            raise IU4RecoveryProjectionError("PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED", "projection requires exact Atomic transaction and Legacy snapshot")
        if (
            projected_legacy_safety.owner_epoch != "PEE"
            or projected_legacy_safety.system_state_id
            != transaction.state_after.system_state_id
            or projected_legacy_safety.symbol != transaction.state_after.position.symbol
            or projected_legacy_safety.authority_generation_id
            != transaction.state_after.authority_generation_id
            or projected_legacy_safety.source_bytes_sha256
            != hashlib.sha256(
                canonical_json_bytes(transaction.state_after.to_record())
            ).hexdigest()
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_AUTHORITY_ROOT_MISMATCH",
                "Projection Legacy payload is not bound to Atomic source",
            )
        self.initialize()
        projection_fd = records_fd = lock = -1
        lock_held = False
        try:
            projection_fd, records_fd = self._open_tree(create=False)
            lock = self._open_regular_at(
                projection_fd, ".projection_v1.lock", os.O_RDWR
            )
            fcntl.flock(lock, fcntl.LOCK_EX)
            lock_held = True
            previous = self._read_cursor_at(projection_fd)
            sequence = transaction.transaction_sequence
            if previous is not None and sequence == previous.atomic_transaction_sequence:
                if (
                    transaction.transaction_event_id
                    != previous.atomic_transaction_event_id
                    or transaction.transaction_fingerprint
                    != previous.atomic_transaction_fingerprint
                    or transaction.state_after.journal_head
                    != previous.atomic_journal_head
                    or transaction.state_after.state_fingerprint
                    != previous.atomic_state_fingerprint
                ):
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_PROJECTION_LAG",
                        "same Projection sequence contains divergent Atomic content",
                    )
                output_name = f"{sequence:020d}_{previous.projection_id}.json"
                existing = self._read_regular_at(records_fd, output_name)
                if existing is None or hashlib.sha256(existing[0]).hexdigest() != previous.projection_output_bytes_sha256:
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_PROJECTION_LAG",
                        "durable Cursor has no exact Projection output",
                    )
                _, current_inventory_fingerprint = self._inventory_at(
                    projection_fd, records_fd, operation_attempt_id
                )
                if current_inventory_fingerprint != previous.projection_root_inventory_fingerprint:
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_PROJECTION_LAG",
                        "Projection replay inventory diverged from Cursor",
                    )
                return previous
            if previous is None:
                if sequence != 1 or transaction.state_before.transaction_sequence != 0 or transaction.previous_journal_head != EMPTY:
                    raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "first projection is not the Authority base successor")
                previous_sequence, previous_head = 0, EMPTY
                previous_state = transaction.state_before.state_fingerprint
                previous_id = previous_fp = NONE
                base_state = previous_state
            else:
                if sequence != previous.atomic_transaction_sequence + 1 or transaction.state_before.state_fingerprint != previous.atomic_state_fingerprint or transaction.previous_journal_head != previous.atomic_journal_head:
                    raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "projection sequence or ancestry is not contiguous")
                previous_sequence, previous_head = previous.atomic_transaction_sequence, previous.atomic_journal_head
                previous_state = previous.atomic_state_fingerprint
                previous_id, previous_fp = previous.projection_cursor_id, previous.projection_cursor_fingerprint
                base_state = previous.projection_base_state_fingerprint
            projection = IU4CompatibilityProjectionV1.build(
                projection_id_material=transaction.transaction_event_id,
                atomic_transaction_event_id=transaction.transaction_event_id,
                atomic_transaction_fingerprint=transaction.transaction_fingerprint,
                atomic_transaction_sequence=sequence,
                atomic_journal_head=transaction.state_after.journal_head,
                atomic_state_fingerprint=transaction.state_after.state_fingerprint,
                authority_generation_id=transaction.state_after.authority_generation_id,
                authority_prepare_record_fingerprint=transaction.state_after.authority_prepare_record_fingerprint,
                projected_legacy_safety=projected_legacy_safety.to_record(),
                source_path=projected_legacy_safety.source_path,
                target_path=str(self.records_root),
                source_bytes_sha256=hashlib.sha256(canonical_json_bytes(transaction.state_after.to_record())).hexdigest(),
                target_bytes_sha256=hashlib.sha256(canonical_json_bytes(projected_legacy_safety.to_record())).hexdigest(),
                projected_at_utc=_utc(published_at_utc, "published_at_utc"),
            )
            output_name = f"{sequence:020d}_{projection.projection_id}.json"
            output_bytes = canonical_json_bytes(projection.to_record()) + b"\n"
            if fault_point == "BEFORE_OUTPUT_CREATE":
                raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated pre-output crash")
            existing_output = self._read_regular_at(
                records_fd, output_name, allow_missing=True
            )
            if existing_output is not None:
                if existing_output[0] != output_bytes:
                    raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "Projection output replay conflicts")
            else:
                descriptor = self._open_regular_at(
                    records_fd, output_name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                )
                try:
                    self._write_descriptor(descriptor, output_bytes)
                    if fault_point == "AFTER_OUTPUT_CREATE":
                        raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-output-create crash")
                    os.fsync(descriptor)
                    if fault_point == "AFTER_OUTPUT_FILE_SYNC":
                        raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-output-sync crash")
                finally:
                    _cleanup_descriptors_preserving_primary(
                        (descriptor,),
                        primary_active=sys.exc_info()[0] is not None,
                        message="Projection output descriptor close failed",
                    )
                self._sync_fd(records_fd)
                if fault_point == "AFTER_OUTPUT_DIRECTORY_SYNC":
                    raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-output-directory-sync crash")
            output_readback = self._read_regular_at(records_fd, output_name)
            if output_readback is None or output_readback[0] != output_bytes:
                raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "Projection output readback differs")
            if fault_point == "AFTER_OUTPUT_READBACK":
                raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated output-only crash")
            _, inventory_fingerprint = self._inventory_at(
                projection_fd, records_fd, operation_attempt_id
            )
            if fault_point == "AFTER_INVENTORY":
                raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-inventory crash")
            cursor = IU4ProjectionCursorV1.build(
                authority_generation_id=transaction.state_after.authority_generation_id,
                authority_prepare_record_fingerprint=transaction.state_after.authority_prepare_record_fingerprint,
                projection_base_sequence=0, projection_base_journal_head=EMPTY,
                projection_base_state_fingerprint=base_state,
                previous_atomic_transaction_sequence=previous_sequence,
                previous_atomic_journal_head=previous_head,
                previous_atomic_state_fingerprint=previous_state,
                atomic_transaction_event_id=transaction.transaction_event_id,
                atomic_transaction_fingerprint=transaction.transaction_fingerprint,
                atomic_transaction_sequence=sequence,
                atomic_journal_head=transaction.state_after.journal_head,
                atomic_state_fingerprint=transaction.state_after.state_fingerprint,
                projection_id=projection.projection_id,
                projection_fingerprint=projection.projection_fingerprint,
                projection_output_bytes_sha256=hashlib.sha256(output_bytes).hexdigest(),
                previous_projection_cursor_id=previous_id,
                previous_projection_cursor_fingerprint=previous_fp,
                published_at_utc=published_at_utc,
                projection_root_inventory_fingerprint=inventory_fingerprint,
            )
            temp_name = f".projection_cursor_v1.tmp.{operation_attempt_id}"
            data = canonical_json_bytes(cursor.to_record()) + b"\n"
            existing_temp = self._read_regular_at(
                projection_fd, temp_name, allow_missing=True
            )
            if existing_temp is not None and existing_temp[0] != data:
                raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "stale Cursor temporary conflicts")
            flags = os.O_WRONLY | os.O_CLOEXEC
            if existing_temp is None:
                flags |= os.O_CREAT | os.O_EXCL
            descriptor = self._open_regular_at(projection_fd, temp_name, flags)
            try:
                if os.fstat(descriptor).st_size == 0:
                    self._write_descriptor(descriptor, data)
                if fault_point == "AFTER_CURSOR_TEMP_CREATE":
                    raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-Cursor-temp crash")
                os.fsync(descriptor)
                if fault_point == "AFTER_CURSOR_FILE_SYNC":
                    raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-Cursor-sync crash")
            finally:
                _cleanup_descriptors_preserving_primary(
                    (descriptor,),
                    primary_active=sys.exc_info()[0] is not None,
                    message="Projection Cursor temp descriptor close failed",
                )
            os.replace(
                temp_name, "projection_cursor_v1.json",
                src_dir_fd=projection_fd, dst_dir_fd=projection_fd,
            )
            if fault_point == "AFTER_CURSOR_REPLACE":
                raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-Cursor-replace crash")
            self._sync_fd(projection_fd)
            if fault_point == "AFTER_CURSOR_DIRECTORY_SYNC":
                raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-Cursor-directory-sync crash")
            if self._read_cursor_at(projection_fd) != cursor:
                raise IU4RecoveryProjectionError("PEE_IU4_PROJECTION_LAG", "Cursor readback mismatch")
            if fault_point == "AFTER_CURSOR_READBACK":
                raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-Cursor-readback crash")
            return cursor
        except Exception as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", "projection publication failed"
                ) from exc
            if isinstance(exc, IU4RecoveryProjectionError):
                raise
            raise
        finally:
            _cleanup_descriptors_preserving_primary(
                (lock, records_fd, projection_fd),
                primary_active=sys.exc_info()[0] is not None,
                message="Projection lock release or descriptor close failed",
                unlock_descriptor=lock if lock_held else -1,
            )


@dataclass(frozen=True)
class IU4LifecycleOperationResultV1:
    operation: str
    target_fingerprint: str
    prepare_record_fingerprint: str
    commit_record_fingerprint: str
    outcome: str


class IU4RecoveryOrchestratorV1:
    """Explicit offline lifecycle/recovery orchestration for tests and I7+ only."""

    def __init__(
        self,
        *,
        lifecycle_ledger: IU4LifecycleLedgerV1,
        atomic_coordinator: Any,
        expected_repository_commit: str,
        expected_operator: str,
        expected_secured_logs_manifest_sha256: str,
        expected_environment_check_sha256: str,
        expected_last_state_timestamp_utc: str,
    ) -> None:
        from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinatorV2

        if type(lifecycle_ledger) is not IU4LifecycleLedgerV1 or type(atomic_coordinator) is not PaperAtomicCoordinatorV2:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH",
                "I6 orchestrator requires exact Lifecycle and Coordinator types",
            )
        self.lifecycle_ledger = lifecycle_ledger
        self.atomic_coordinator = atomic_coordinator
        self.expected_repository_commit = _hex40(
            expected_repository_commit, "expected_repository_commit"
        )
        self.expected_operator = _text(expected_operator, "expected_operator")
        self.expected_secured_logs_manifest_sha256 = _sha(
            expected_secured_logs_manifest_sha256,
            "expected_secured_logs_manifest_sha256",
        )
        self.expected_environment_check_sha256 = _sha(
            expected_environment_check_sha256,
            "expected_environment_check_sha256",
        )
        self.expected_last_state_timestamp_utc = _utc(
            expected_last_state_timestamp_utc,
            "expected_last_state_timestamp_utc",
        )

    def _lifecycle_records_read(
        self, message: str
    ) -> tuple[IU4LifecycleRecordV1, ...]:
        try:
            return self.lifecycle_ledger.records()
        except Exception as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", message
                ) from exc
            raise

    def _lifecycle_view_read(self, message: str) -> Any:
        try:
            return self.lifecycle_ledger.view()
        except Exception as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", message
                ) from exc
            raise

    def _lifecycle_initialize(self, message: str) -> None:
        try:
            self.lifecycle_ledger.initialize()
        except Exception as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", message
                ) from exc
            raise

    @staticmethod
    def _legacy_projection_read(path: str, message: str) -> dict[str, Any]:
        try:
            return read_legacy_safety_projection(Path(path))
        except BaseException as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", message
                ) from exc
            raise

    @staticmethod
    def _legacy_projection_write(
        path: str, record: dict[str, Any], message: str,
    ) -> None:
        try:
            write_legacy_safety_projection(path, record)
        except BaseException as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", message
                ) from exc
            raise

    def _append_lifecycle_record_with_lock_held(
        self, *, record_type: str, lifecycle_event_id: str,
        payload: Mapping[str, Any],
    ) -> IU4LifecycleRecordV1:
        """Append through the accepted Ledger format while its writer lock is held."""

        current = self._lifecycle_records_read(
            "Lifecycle read failed during locked append"
        )
        if any(
            record.lifecycle_event_id == lifecycle_event_id for record in current
        ):
            raise IU4LifecycleLedgerError("duplicate lifecycle event id")
        sequence = len(current) + 1
        previous = EMPTY if not current else current[-1].record_fingerprint
        record = IU4LifecycleRecordV1.build(
            sequence=sequence, event_id=lifecycle_event_id,
            record_type=record_type, previous=previous, payload=payload,
        )
        self.lifecycle_ledger._derive((*current, record))
        path = self.lifecycle_ledger.records_directory / f"{sequence:020d}.json"
        data = lifecycle_canonical_json(record.to_mapping()) + b"\n"
        descriptor = -1
        try:
            descriptor = os.open(
                path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
                0o600,
            )
            try:
                offset = 0
                while offset < len(data):
                    written = os.write(descriptor, data[offset:])
                    if written <= 0:
                        raise IU4LifecycleLedgerError("short ledger write")
                    offset += written
                os.fsync(descriptor)
            finally:
                _cleanup_descriptors_preserving_primary(
                    (descriptor,),
                    primary_active=sys.exc_info()[0] is not None,
                    message="locked Lifecycle record descriptor close failed",
                )
                descriptor = -1
            self.lifecycle_ledger._fsync_directory(
                self.lifecycle_ledger.records_directory
            )
            readback = self._lifecycle_records_read(
                "Lifecycle readback failed during locked append"
            )
        except BaseException as exc:
            if _has_resource_cause(exc):
                raise IU4LifecycleLedgerError(
                    "locked ledger append failed"
                ) from exc
            raise
        if not readback or readback[-1] != record:
            raise IU4LifecycleLedgerError("locked ledger readback mismatch")
        return record

    def _terminal_kill_and_gap_under_lifecycle_lock(
        self, *, consumption: IU4LifecycleRecordV1,
        authorization: Any, proof: IU4PersistenceWorkerExclusionProofV1,
        open_session_id: str, runtime_session_open_event_id: str,
        runtime_session_open_record_fingerprint: str,
        runtime_session_open_journal_head: str,
        terminal_event_id: str, gap_event_id: str,
        consumption_timestamp_utc: str, fault_point: str,
    ) -> tuple[Any, IU4LifecycleRecordV1]:
        """Hold the Lifecycle writer lock across KILL, readback and Gap append."""

        lock_fd = -1
        lock_held = False
        try:
            self._lifecycle_initialize(
                "Terminal Lifecycle initialization failed"
            )
            lock_fd = os.open(
                self.lifecycle_ledger.lock_path, os.O_RDWR | os.O_CLOEXEC
            )
        except Exception as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "Terminal Lifecycle lock acquisition failed",
                ) from exc
            raise
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            lock_held = True
            locked_view = self._lifecycle_view_read(
                "Terminal Lifecycle locked view failed"
            )
            if (
                locked_view.ledger_tip != consumption.record_fingerprint
                or locked_view.open_runtime_session_id != open_session_id
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_LIFECYCLE_EXTENSION_INVALID",
                    "Lifecycle changed before Terminal reconciliation lock",
                )
            if fault_point in {"BEFORE_KILL", "BEFORE_SNAPSHOT_REPLACE"}:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", "simulated pre-KILL crash"
                )
            committed = self.atomic_coordinator.i6_reconcile_terminal_journal(
                runtime_session_open_journal_head=runtime_session_open_journal_head,
                worker_exclusion_proof_fingerprint=proof.proof_fingerprint,
                transaction_event_id=terminal_event_id,
                transaction_timestamp_utc=consumption_timestamp_utc,
                causal_tick_id=0,
                control_authorization_reference=(
                    authorization.restart_recovery_authorization_id
                ),
                reason_code="PEE_IU4_TERMINAL_GAP_RECONCILIATION_REQUIRED",
            )
            post_kill_view = self._lifecycle_view_read(
                "Terminal Lifecycle post-KILL view failed"
            )
            if (
                post_kill_view.ledger_tip != consumption.record_fingerprint
                or post_kill_view.open_runtime_session_id != open_session_id
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_LIFECYCLE_EXTENSION_INVALID",
                    "Lifecycle changed during Terminal reconciliation",
                )
            if fault_point in {"AFTER_KILL", "AFTER_SNAPSHOT_REPLACE"}:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE",
                    "simulated post-KILL crash",
                )
            payload = {
                "session_id": proof.runtime_session_id,
                "runtime_session_open_event_id": runtime_session_open_event_id,
                "runtime_session_open_record_fingerprint": (
                    runtime_session_open_record_fingerprint
                ),
                "authorization_consumption_record_fingerprint": (
                    consumption.record_fingerprint
                ),
                "worker_exclusion_proof_id": proof.worker_exclusion_proof_id,
                "worker_exclusion_proof_fingerprint": proof.proof_fingerprint,
                "terminal_transaction_event_id": terminal_event_id,
                "terminal_state_fingerprint": committed.state.state_fingerprint,
                "terminal_journal_head": committed.state.journal_head,
                "timestamp_utc": consumption_timestamp_utc,
            }
            if fault_point == "BEFORE_GAP_RECORD":
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "simulated pre-Gap-record crash",
                )
            try:
                gap = self._append_lifecycle_record_with_lock_held(
                    record_type="TERMINAL_GAP_RECONCILIATION",
                    lifecycle_event_id=gap_event_id, payload=payload,
                )
            except Exception as exc:
                if _has_resource_cause(exc):
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_RESOURCE_EXHAUSTED",
                        "Terminal Gap resource publication failed",
                    ) from exc
                if isinstance(exc, IU4LifecycleLedgerError):
                    raise IU4RecoveryProjectionError(
                        "PEE_IU4_LIFECYCLE_LEDGER_CONFLICT",
                        "Terminal Gap record failed",
                    ) from exc
                raise
            if fault_point == "AFTER_GAP_RECORD":
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "simulated post-Gap-record crash",
                )
            return committed, gap
        except Exception as exc:
            if _has_resource_cause(exc):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED",
                    "Terminal reconciliation resource operation failed",
                ) from exc
            raise
        finally:
            _cleanup_descriptors_preserving_primary(
                (lock_fd,),
                primary_active=sys.exc_info()[0] is not None,
                message="Terminal Lifecycle lock release or close failed",
                unlock_descriptor=lock_fd if lock_held else -1,
            )

    def atomic_genesis(
        self,
        *,
        manifest: IU4CleanGenesisManifestV1,
        target_state_template: Any,
        prepare_event_id: str,
        commit_event_id: str,
        completion_provenance: str = "DIRECT",
        fault_point: str = "",
    ) -> IU4LifecycleOperationResultV1:
        from live_l1.state.paper_atomic_coordinator import (
            AtomicPaperStateV2,
            PaperAtomicCoordinatorError,
        )

        if type(manifest) is not IU4CleanGenesisManifestV1 or type(target_state_template) is not AtomicPaperStateV2:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "Genesis inputs require exact types"
            )
        if completion_provenance != "DIRECT":
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID", "direct Genesis cannot claim recovered provenance"
            )
        expected_components = _atomic_component_fingerprints(target_state_template)
        expected_profiles = _atomic_profile_bindings(target_state_template)
        if (
            manifest.operator != self.expected_operator
            or manifest.coordinator_id != self.atomic_coordinator.coordinator_id
            or manifest.coordinator_id != target_state_template.coordinator_id
            or manifest.system_state_id != target_state_template.system_state_id
            or manifest.symbol != self.atomic_coordinator.symbol
            or manifest.symbol != target_state_template.position.symbol
            or manifest.state_path != str(self.atomic_coordinator.state_path)
            or manifest.journal_path != str(self.atomic_coordinator.transaction_directory)
            or manifest.initial_state_record != target_state_template.to_record()
            or manifest.profile_bindings != expected_profiles
            or manifest.component_fingerprints != expected_components
            or manifest.empty_journal_inventory_fingerprint
            != _empty_journal_inventory_fingerprint(manifest.journal_path)
            or manifest.atomic_absence_proof_sha256
            != _absence_proof_sha256("ATOMIC_STATE", manifest.state_path)
            or manifest.legacy_absence_proof_sha256
            != _absence_proof_sha256("LEGACY_STATE", manifest.state_path + ".legacy")
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_GENESIS_PROVENANCE_INVALID",
                "Genesis manifest is not bound to the Coordinator target",
            )
        view = self._lifecycle_view_read(
            "Genesis Lifecycle view failed before PREPARE"
        )
        existing_records = self._lifecycle_records_read(
            "Genesis Lifecycle records read failed before PREPARE"
        )
        existing_prepare = next(
            (record for record in existing_records if record.lifecycle_event_id == prepare_event_id),
            None,
        )
        existing_commit = next(
            (record for record in existing_records if record.lifecycle_event_id == commit_event_id),
            None,
        )
        if existing_prepare is not None or existing_commit is not None:
            if (
                existing_prepare is None
                or existing_commit is None
                or existing_prepare.record_type != "ATOMIC_GENESIS_PREPARE"
                or existing_commit.record_type != "ATOMIC_GENESIS_COMMIT"
                or existing_prepare.payload.get("manifest_id")
                != manifest.clean_genesis_manifest_id
                or existing_prepare.payload.get("manifest_fingerprint")
                != manifest.manifest_fingerprint
                or existing_commit.payload.get("prepare_record_fingerprint")
                != existing_prepare.record_fingerprint
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Genesis event replay conflicts"
                )
            state = self.atomic_coordinator.load_state()
            if existing_commit.payload.get("target_state_fingerprint") != state.state_fingerprint:
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Genesis committed target differs"
                )
            return IU4LifecycleOperationResultV1(
                operation="ATOMIC_GENESIS", target_fingerprint=state.state_fingerprint,
                prepare_record_fingerprint=existing_prepare.record_fingerprint,
                commit_record_fingerprint=existing_commit.record_fingerprint,
                outcome="GENESIS_COMPLETE_LOOP_NOT_AUTHORIZED",
            )
        if view.record_count or view.authority_generation_id != "NONE" or self.atomic_coordinator.state_path.exists() or self.atomic_coordinator.transaction_directory.exists() and any(self.atomic_coordinator.transaction_directory.iterdir()):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_GENESIS_REQUIRED", "Genesis absence proof no longer holds"
            )
        business = target_state_template.business_payload()
        generation = authority_generation_id(
            operation="ATOMIC_GENESIS",
            source_authority_generation_id="NONE",
            source_authority_commit_anchor="NONE",
            manifest_fingerprint=manifest.manifest_fingerprint,
            approval_fingerprint=manifest.approval_fingerprint,
            target_business_payload=business,
        )
        prepare_payload = {
            "operation": "ATOMIC_GENESIS",
            "authority_generation_id": generation,
            "source_authority_generation_id": "NONE",
            "source_authority_commit_anchor": "NONE",
            "manifest_id": manifest.clean_genesis_manifest_id,
            "manifest_fingerprint": manifest.manifest_fingerprint,
            "approval_fingerprint": manifest.approval_fingerprint,
            "target_state_path": str(self.atomic_coordinator.state_path),
            "target_business_payload": business,
            "target_state_core_fingerprint": lifecycle_fingerprint(business),
            "previous_owner_epoch": 0,
            "new_owner_epoch": 1,
            "operator": manifest.operator,
            "timestamp_utc": manifest.operation_timestamp_utc,
        }
        if fault_point == "BEFORE_PREPARE":
            raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated pre-PREPARE crash")
        try:
            prepare = self.lifecycle_ledger.append(
                record_type="ATOMIC_GENESIS_PREPARE",
                lifecycle_event_id=_text(prepare_event_id, "prepare_event_id"),
                payload=prepare_payload,
            )
        except (IU4LifecycleLedgerError, OSError, MemoryError) as exc:
            _raise_lifecycle_publication_error(
                exc, "PEE_IU4_LIFECYCLE_LEDGER_CONFLICT", "Genesis PREPARE failed"
            )
        if fault_point == "AFTER_PREPARE":
            raise IU4RecoveryProjectionError("PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE", "simulated post-PREPARE crash")
        risk = replace(target_state_template.risk, authority_generation_id=generation)
        target = replace(
            target_state_template,
            authority_generation_id=generation,
            authority_prepare_record_fingerprint=prepare.record_fingerprint,
            authority_manifest_id=manifest.clean_genesis_manifest_id,
            authority_manifest_fingerprint=manifest.manifest_fingerprint,
            risk=risk,
        )
        if fault_point == "BEFORE_TARGET_REPLACE":
            raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated pre-target crash")
        self.atomic_coordinator.initialize(
            target,
            committed_authority_target_state_fingerprint=target.state_fingerprint,
        )
        if fault_point in {"AFTER_TARGET", "AFTER_TARGET_REPLACE", "AFTER_TARGET_FILE_SYNC", "AFTER_TARGET_DIRECTORY_SYNC"}:
            raise IU4RecoveryProjectionError("PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE", "simulated post-target crash")
        reconciled = self.atomic_coordinator.load_state()
        if reconciled != target:
            raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Genesis target readback differs")
        if fault_point == "AFTER_RECONCILIATION":
            raise IU4RecoveryProjectionError("PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE", "simulated post-reconciliation crash")
        commit_payload = {
            "prepare_record_fingerprint": prepare.record_fingerprint,
            "authority_generation_id": generation,
            "new_owner_epoch": 1,
            "target_state_fingerprint": target.state_fingerprint,
            "target_state_core_fingerprint": prepare_payload["target_state_core_fingerprint"],
            "target_state_path": str(self.atomic_coordinator.state_path),
            "reconciliation_result": "PASS",
            "completion_provenance": "DIRECT",
            "direct_process_instance_id": manifest.process_instance_id,
            "genesis_operation_attempt_id": manifest.operation_attempt_id,
            "operator": manifest.operator,
            "timestamp_utc": manifest.operation_timestamp_utc,
        }
        if fault_point == "BEFORE_COMMIT":
            raise IU4RecoveryProjectionError("PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE", "simulated pre-COMMIT crash")
        try:
            commit = self.lifecycle_ledger.append(
                record_type="ATOMIC_GENESIS_COMMIT",
                lifecycle_event_id=_text(commit_event_id, "commit_event_id"),
                payload=commit_payload,
            )
        except (IU4LifecycleLedgerError, OSError, MemoryError) as exc:
            _raise_lifecycle_publication_error(
                exc, "PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Genesis COMMIT failed"
            )
        if fault_point == "AFTER_COMMIT":
            raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-COMMIT crash")
        return IU4LifecycleOperationResultV1(
            operation="ATOMIC_GENESIS",
            target_fingerprint=target.state_fingerprint,
            prepare_record_fingerprint=prepare.record_fingerprint,
            commit_record_fingerprint=commit.record_fingerprint,
            outcome="GENESIS_COMPLETE_LOOP_NOT_AUTHORIZED",
        )

    def consume_restart_authorization(
        self,
        *,
        authorization: Any,
        operation: str,
        consumption_event_id: str,
        consumption_timestamp_utc: str,
        expected_startup_attempt_id: str,
    ) -> Any:
        from live_l1.core.paper_iu4_startup_gate import IU4RestartRecoveryAuthorizationV1
        from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinatorError

        if type(authorization) is not IU4RestartRecoveryAuthorizationV1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RESTART_AUTHORIZATION_REQUIRED", "exact Restart Authorization required"
            )
        if authorization.operation != operation or authorization.coordinator_id != self.atomic_coordinator.coordinator_id:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH", "Restart Authorization binding differs"
            )
        if (
            authorization.operator != self.expected_operator
            or authorization.repository_commit_sha != self.expected_repository_commit
            or authorization.secured_logs_manifest_sha256
            != self.expected_secured_logs_manifest_sha256
            or authorization.environment_check_sha256
            != self.expected_environment_check_sha256
            or authorization.last_state_timestamp_utc
            != self.expected_last_state_timestamp_utc
            or authorization.startup_attempt_id
            != _text(expected_startup_attempt_id, "expected_startup_attempt_id")
            or authorization.no_open_intents_confirmed is not True
            or authorization.economics_config_fingerprint
            != self.atomic_coordinator.config.config_fingerprint
            or authorization.throttle_policy_fingerprint
            != self.atomic_coordinator.throttle_policy.policy_fingerprint
            or authorization.runtime_control_fingerprint
            != self.atomic_coordinator.runtime_control_fingerprint
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH",
                "Restart Authorization trusted environment differs",
            )
        observed = _as_datetime(_utc(consumption_timestamp_utc, "consumption_timestamp_utc"))
        if not (_as_datetime(authorization.valid_from_utc) <= observed <= _as_datetime(authorization.valid_until_utc)):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH", "Restart Authorization is stale"
            )
        try:
            current = self.atomic_coordinator.load_state()
        except PaperAtomicCoordinatorError:
            current = None
        view = self._lifecycle_view_read(
            "Restart Authorization Lifecycle view failed before Consumption"
        )
        genesis_completion = (
            operation == "COMPLETE_AUTHORITY_PREPARE"
            and authorization.expected_snapshot_fingerprint == "NO_ATOMIC_STATE"
        )
        if current is None and not genesis_completion:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH", "authorized pre-State is missing"
            )
        pre_state_fingerprint = (
            "NO_ATOMIC_STATE" if genesis_completion else current.state_fingerprint
        )
        pre_journal_head = "EMPTY" if genesis_completion else current.journal_head
        if (
            authorization.pre_attempt_ledger_tip != view.ledger_tip
            or authorization.source_authority_generation_id
            != (view.authority_generation_id if genesis_completion else current.authority_generation_id)
            or authorization.source_authority_commit_anchor
            != (NONE if genesis_completion else view.authority_commit_anchor)
            or authorization.expected_snapshot_fingerprint != pre_state_fingerprint
            or authorization.expected_transaction_sequence
            != (0 if genesis_completion else current.transaction_sequence)
            or authorization.expected_journal_head != pre_journal_head
            or (
                not genesis_completion
                and authorization.previous_kill_level != current.risk.kill_level
            )
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH", "Restart pre-State differs"
            )
        try:
            return self.lifecycle_ledger.consume_restart_authorization(
                lifecycle_event_id=consumption_event_id,
                authorization_id=authorization.restart_recovery_authorization_id,
                authorization_fingerprint=authorization.authorization_fingerprint,
                operation=operation,
                operator=authorization.operator,
                startup_attempt_id=authorization.startup_attempt_id,
                pre_state_fingerprint=pre_state_fingerprint,
                pre_journal_head=pre_journal_head,
                pre_attempt_ledger_tip=view.ledger_tip,
                source_authority_generation_id=authorization.source_authority_generation_id,
                source_authority_commit_anchor=authorization.source_authority_commit_anchor,
                consumption_timestamp_utc=consumption_timestamp_utc,
                completion_prepare_event_id=authorization.completion_prepare_event_id,
                completion_prepare_fingerprint=authorization.completion_prepare_fingerprint,
                target_authority_generation_id=authorization.planned_authority_generation_id,
            )
        except Exception as exc:
            if _has_resource_cause(exc):
                _raise_lifecycle_publication_error(
                    exc,
                    "PEE_IU4_LIFECYCLE_LEDGER_CONFLICT",
                    "Restart Authorization consumption failed",
                )
            if not isinstance(exc, IU4LifecycleLedgerError):
                raise
            consumed_view = self._lifecycle_view_read(
                "Restart Authorization Lifecycle conflict view failed"
            )
            code = "PEE_IU4_RESTART_AUTHORIZATION_CONSUMED" if authorization.restart_recovery_authorization_id in consumed_view.consumed_authorization_ids else "PEE_IU4_LIFECYCLE_LEDGER_CONFLICT"
            raise IU4RecoveryProjectionError(code, "Restart Authorization consumption failed") from exc

    def handoff(
        self,
        *,
        manifest: IU4StateHandoffManifestV1,
        target: Any,
        target_path: str,
        prepare_event_id: str,
        commit_event_id: str,
        fault_point: str = "",
    ) -> IU4LifecycleOperationResultV1:
        from live_l1.state.paper_atomic_coordinator import (
            AtomicPaperStateV2,
            PaperAtomicCoordinatorError,
        )

        if type(manifest) is not IU4StateHandoffManifestV1:
            raise IU4RecoveryProjectionError("PEE_IU4_HANDOFF_SAFETY_CONFLICT", "exact Handoff manifest required")
        source_snapshot = IU4LegacySafetySnapshotV1.from_record(
            manifest.source_safety_snapshot
        )
        if (
            manifest.repository_commit != self.expected_repository_commit
            or manifest.operator != self.expected_operator
            or manifest.coordinator_id != self.atomic_coordinator.coordinator_id
            or manifest.system_state_id != source_snapshot.system_state_id
            or manifest.symbol != self.atomic_coordinator.symbol
            or manifest.symbol != source_snapshot.symbol
            or target_path != manifest.competing_state_path
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT",
                "Handoff manifest authority identity differs",
            )
        records = self._lifecycle_records_read(
            "Handoff Lifecycle records read failed before PREPARE"
        )
        existing_prepare = next(
            (record for record in records if record.lifecycle_event_id == prepare_event_id), None
        )
        existing_commit = next(
            (record for record in records if record.lifecycle_event_id == commit_event_id), None
        )
        if existing_prepare is not None or existing_commit is not None:
            if (
                existing_prepare is None or existing_commit is None
                or existing_prepare.payload.get("manifest_id") != manifest.handoff_manifest_id
                or existing_prepare.payload.get("manifest_fingerprint") != manifest.manifest_fingerprint
                or existing_commit.payload.get("prepare_record_fingerprint") != existing_prepare.record_fingerprint
            ):
                raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Handoff replay conflicts")
            if manifest.direction == "LEGACY_TO_PEE":
                observed_target = self.atomic_coordinator.load_state().state_fingerprint
            elif type(target) is IU4LegacySafetySnapshotV1:
                observed_target = target.snapshot_fingerprint
                if self._legacy_projection_read(
                    target_path, "Handoff Legacy replay read failed"
                ) != target.to_record():
                    raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Handoff Legacy readback differs")
            else:
                raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Handoff replay target type differs")
            if existing_commit.payload.get("target_state_fingerprint") != observed_target:
                raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Handoff committed target differs")
            return IU4LifecycleOperationResultV1(
                operation=manifest.direction, target_fingerprint=observed_target,
                prepare_record_fingerprint=existing_prepare.record_fingerprint,
                commit_record_fingerprint=existing_commit.record_fingerprint,
                outcome="HANDOFF_COMPLETE_LOOP_NOT_AUTHORIZED",
            )
        view = self._lifecycle_view_read(
            "Handoff Lifecycle view failed before PREPARE"
        )
        if (
            view.open_authority_prepare_event_id
            or view.owner_epoch != manifest.previous_owner_epoch
            or view.authority_generation_id != manifest.source_authority_generation_id
            or view.authority_commit_anchor != manifest.source_authority_commit_anchor
        ):
            raise IU4RecoveryProjectionError("PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID", "Handoff source Owner differs")
        operation = manifest.direction
        prepare_type = "LEGACY_TO_PEE_HANDOFF_PREPARE" if operation == "LEGACY_TO_PEE" else "PEE_TO_LEGACY_HANDOFF_PREPARE"
        commit_type = AUTHORITY_PAIRS[prepare_type]
        target_record = (
            target.to_record()
            if type(target) in {AtomicPaperStateV2, IU4LegacySafetySnapshotV1}
            else target
        )
        if type(target_record) is not dict:
            raise IU4RecoveryProjectionError("PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Handoff target must be a canonical record")
        target_business = target.business_payload() if type(target) is AtomicPaperStateV2 else target_record
        target_business_fingerprint = lifecycle_fingerprint(target_business)
        target_core_fingerprint = lifecycle_fingerprint(
            target.core_payload() if type(target) is AtomicPaperStateV2 else target_record
        )
        if (
            manifest.target_business_fingerprint != target_business_fingerprint
            or manifest.target_core_fingerprint != target_core_fingerprint
            or manifest.mapping_record
            != handoff_mapping_record(
                direction=operation,
                source_snapshot=source_snapshot,
                target_business_fingerprint=target_business_fingerprint,
                target_core_fingerprint=target_core_fingerprint,
            )
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Handoff mapping/target differs"
            )
        if operation == "LEGACY_TO_PEE":
            if (
                source_snapshot.owner_epoch != "LEGACY"
                or manifest.source_state_path != source_snapshot.source_path
                or manifest.source_state_schema != 1
                or manifest.source_state_bytes_sha256 != source_snapshot.source_bytes_sha256
                or manifest.source_state_fingerprint != source_snapshot.snapshot_fingerprint
                or manifest.competing_state_path != str(self.atomic_coordinator.state_path)
                or type(target) is not AtomicPaperStateV2
                or target.coordinator_id != manifest.coordinator_id
                or target.system_state_id != manifest.system_state_id
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "Legacy-to-PEE source/target differs"
                )
        else:
            current = self.atomic_coordinator.load_state()
            if (
                source_snapshot.owner_epoch != "PEE"
                or manifest.source_state_path != str(self.atomic_coordinator.state_path)
                or manifest.source_state_schema != 2
                or manifest.source_state_bytes_sha256
                != hashlib.sha256(self.atomic_coordinator.state_path.read_bytes()).hexdigest()
                or manifest.source_state_fingerprint != current.state_fingerprint
                or type(target) is not IU4LegacySafetySnapshotV1
                or target.owner_epoch != "LEGACY"
                or target.source_path != target_path
            ):
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_HANDOFF_SAFETY_CONFLICT", "PEE-to-Legacy source/target differs"
                )
        generation = handoff_planned_generation_id(
            operation=operation,
            source_authority_generation_id=manifest.source_authority_generation_id,
            source_authority_commit_anchor=manifest.source_authority_commit_anchor,
            approval_fingerprint=manifest.approval_fingerprint,
            target_business_payload=target_business,
        )
        if manifest.planned_authority_generation_id != generation:
            raise IU4RecoveryProjectionError("PEE_IU4_HANDOFF_SAFETY_CONFLICT", "planned Handoff Generation differs")
        prepare_payload = {
            "operation": operation,
            "authority_generation_id": generation,
            "source_authority_generation_id": manifest.source_authority_generation_id,
            "source_authority_commit_anchor": manifest.source_authority_commit_anchor,
            "manifest_id": manifest.handoff_manifest_id,
            "manifest_fingerprint": manifest.manifest_fingerprint,
            "approval_fingerprint": manifest.approval_fingerprint,
            "target_state_path": target_path,
            "target_business_payload": target_business,
            "target_state_core_fingerprint": manifest.target_core_fingerprint,
            "previous_owner_epoch": manifest.previous_owner_epoch,
            "new_owner_epoch": manifest.new_owner_epoch,
            "operator": manifest.operator,
            "timestamp_utc": manifest.operation_timestamp_utc,
        }
        if fault_point == "BEFORE_PREPARE":
            raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated Handoff pre-PREPARE crash")
        try:
            prepare = self.lifecycle_ledger.append(
                record_type=prepare_type, lifecycle_event_id=prepare_event_id, payload=prepare_payload
            )
        except (IU4LifecycleLedgerError, OSError, MemoryError) as exc:
            _raise_lifecycle_publication_error(
                exc, "PEE_IU4_LIFECYCLE_LEDGER_CONFLICT", "Handoff PREPARE failed"
            )
        if fault_point == "AFTER_PREPARE":
            raise IU4RecoveryProjectionError("PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE", "simulated Handoff post-PREPARE crash")
        try:
            if operation == "LEGACY_TO_PEE":
                if type(target) is not AtomicPaperStateV2:
                    raise IU4RecoveryProjectionError("PEE_IU4_HANDOFF_SAFETY_CONFLICT", "LEGACY_TO_PEE requires Atomic V2 target")
                risk = replace(target.risk, authority_generation_id=generation)
                materialized = replace(
                    target, authority_generation_id=generation,
                    authority_prepare_record_fingerprint=prepare.record_fingerprint,
                    authority_manifest_id=manifest.handoff_manifest_id,
                    authority_manifest_fingerprint=manifest.manifest_fingerprint,
                    risk=risk,
                )
                if fault_point == "BEFORE_TARGET_REPLACE":
                    raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated Handoff pre-target crash")
                self.atomic_coordinator.initialize(
                    materialized,
                    committed_authority_target_state_fingerprint=materialized.state_fingerprint,
                )
                target_fingerprint = materialized.state_fingerprint
                if self.atomic_coordinator.load_state() != materialized:
                    raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Atomic Handoff target readback differs")
            else:
                if type(target) is not IU4LegacySafetySnapshotV1:
                    raise IU4RecoveryProjectionError("PEE_IU4_HANDOFF_SAFETY_CONFLICT", "PEE_TO_LEGACY requires complete Legacy target")
                if fault_point == "BEFORE_TARGET_REPLACE":
                    raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated Handoff pre-target crash")
                self._legacy_projection_write(
                    target_path,
                    target.to_record(),
                    "Handoff Legacy target publication failed",
                )
                target_fingerprint = target.snapshot_fingerprint
        except (OSError, MemoryError) as exc:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RESOURCE_EXHAUSTED", "Handoff target publication failed"
            ) from exc
        except PaperAtomicCoordinatorError as exc:
            if exc.reason_code == "PEE_IU4_RESOURCE_EXHAUSTED":
                raise IU4RecoveryProjectionError(
                    "PEE_IU4_RESOURCE_EXHAUSTED", "Handoff target publication failed"
                ) from exc
            raise
        if fault_point in {"AFTER_TARGET", "AFTER_TARGET_REPLACE", "AFTER_TARGET_FILE_SYNC", "AFTER_TARGET_DIRECTORY_SYNC", "AFTER_RECONCILIATION"}:
            raise IU4RecoveryProjectionError("PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE", "simulated Handoff post-target crash")
        commit_payload = {
            "prepare_record_fingerprint": prepare.record_fingerprint,
            "authority_generation_id": generation,
            "new_owner_epoch": manifest.new_owner_epoch,
            "target_state_fingerprint": target_fingerprint,
            "target_state_core_fingerprint": prepare_payload["target_state_core_fingerprint"],
            "target_state_path": target_path,
            "reconciliation_result": "PASS",
            "completion_provenance": "DIRECT",
            "operator": manifest.operator,
            "timestamp_utc": manifest.operation_timestamp_utc,
        }
        if fault_point == "BEFORE_COMMIT":
            raise IU4RecoveryProjectionError("PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE", "simulated Handoff pre-COMMIT crash")
        try:
            commit = self.lifecycle_ledger.append(
                record_type=commit_type, lifecycle_event_id=commit_event_id, payload=commit_payload
            )
        except (IU4LifecycleLedgerError, OSError, MemoryError) as exc:
            _raise_lifecycle_publication_error(
                exc, "PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Handoff COMMIT failed"
            )
        if fault_point == "AFTER_COMMIT":
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RESOURCE_EXHAUSTED", "simulated Handoff post-COMMIT crash"
            )
        return IU4LifecycleOperationResultV1(
            operation=operation, target_fingerprint=target_fingerprint,
            prepare_record_fingerprint=prepare.record_fingerprint,
            commit_record_fingerprint=commit.record_fingerprint,
            outcome="HANDOFF_COMPLETE_LOOP_NOT_AUTHORIZED",
        )

    def complete_authority_prepare(
        self,
        *,
        authorization: Any,
        target: Any,
        target_fingerprint: str,
        target_core_fingerprint: str,
        target_path: str,
        consumption_event_id: str,
        materialization_event_id: str,
        commit_event_id: str,
        consumption_timestamp_utc: str,
        expected_startup_attempt_id: str,
    ) -> IU4LifecycleOperationResultV1:
        from live_l1.core.paper_iu4_startup_gate import IU4RestartRecoveryAuthorizationV1

        if type(authorization) is not IU4RestartRecoveryAuthorizationV1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RESTART_AUTHORIZATION_REQUIRED",
                "Completion requires exact Restart Authorization",
            )
        records = self._lifecycle_records_read(
            "Completion Lifecycle records read failed before Consumption"
        )
        prepares = [record for record in records if record.record_type in AUTHORITY_PAIRS]
        commits = {record.payload.get("prepare_record_fingerprint") for record in records if record.record_type in AUTHORITY_PAIRS.values()}
        open_prepares = [record for record in prepares if record.record_fingerprint not in commits]
        if len(open_prepares) != 1:
            raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_PREPARE_COMPLETION_REQUIRED", "exactly one open PREPARE required")
        prepare = open_prepares[0]
        if (
            authorization.completion_prepare_event_id != prepare.lifecycle_event_id
            or authorization.completion_prepare_fingerprint != prepare.record_fingerprint
            or authorization.planned_authority_generation_id != prepare.payload.get("authority_generation_id")
            or authorization.expected_target_path != target_path
            or authorization.target_core_fingerprint != target_core_fingerprint
        ):
            raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Completion target or PREPARE differs")
        consumption = self.consume_restart_authorization(
            authorization=authorization, operation="COMPLETE_AUTHORITY_PREPARE",
            consumption_event_id=consumption_event_id,
            consumption_timestamp_utc=consumption_timestamp_utc,
            expected_startup_attempt_id=expected_startup_attempt_id,
        )
        from live_l1.state.paper_atomic_coordinator import AtomicPaperStateV2

        if type(target) is AtomicPaperStateV2:
            risk = replace(
                target.risk,
                authority_generation_id=prepare.payload["authority_generation_id"],
            )
            materialized = replace(
                target,
                authority_generation_id=prepare.payload["authority_generation_id"],
                authority_prepare_record_fingerprint=prepare.record_fingerprint,
                authority_manifest_id=prepare.payload["manifest_id"],
                authority_manifest_fingerprint=prepare.payload["manifest_fingerprint"],
                risk=risk,
            )
            if self.atomic_coordinator.state_path.exists():
                if self.atomic_coordinator.load_state() != materialized:
                    raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Completion target differs")
            else:
                self.atomic_coordinator.initialize(
                    materialized,
                    committed_authority_target_state_fingerprint=materialized.state_fingerprint,
                )
            if target_fingerprint != materialized.state_fingerprint:
                raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Completion target fingerprint differs")
        elif type(target) is IU4LegacySafetySnapshotV1:
            self._legacy_projection_write(
                target_path,
                target.to_record(),
                "Completion Legacy target publication failed",
            )
            if target_fingerprint != target.snapshot_fingerprint:
                raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Completion Legacy target differs")
        else:
            raise IU4RecoveryProjectionError("PEE_IU4_AUTHORITY_COMMIT_MISMATCH", "Completion target type is unsupported")
        try:
            claim = self.lifecycle_ledger.append(
                record_type="RECOVERY_MATERIALIZATION",
                lifecycle_event_id=materialization_event_id,
                payload={
                    "operation": "COMPLETE_AUTHORITY_PREPARE",
                    "prepare_record_fingerprint": prepare.record_fingerprint,
                    "authorization_record_fingerprint": consumption.record_fingerprint,
                    "target_state_fingerprint": _sha(target_fingerprint, "target_fingerprint"),
                    "target_core_fingerprint": _sha(target_core_fingerprint, "target_core_fingerprint"),
                    "target_path": target_path,
                    "timestamp_utc": consumption_timestamp_utc,
                },
            )
            commit = self.lifecycle_ledger.append(
                record_type=AUTHORITY_PAIRS[prepare.record_type],
                lifecycle_event_id=commit_event_id,
                payload={
                    "prepare_record_fingerprint": prepare.record_fingerprint,
                    "authority_generation_id": prepare.payload["authority_generation_id"],
                    "new_owner_epoch": prepare.payload["new_owner_epoch"],
                    "target_state_fingerprint": target_fingerprint,
                    "target_state_core_fingerprint": target_core_fingerprint,
                    "target_state_path": target_path,
                    "reconciliation_result": "PASS",
                    "completion_provenance": "RECOVERED_AFTER_PREPARE",
                    "completion_authorization_id": authorization.restart_recovery_authorization_id,
                    "completion_consumption_event_id": consumption.lifecycle_event_id,
                    "completion_materialization_record_fingerprint": claim.record_fingerprint,
                    "operator": authorization.operator,
                    "timestamp_utc": consumption_timestamp_utc,
                },
            )
        except (IU4LifecycleLedgerError, OSError, MemoryError) as exc:
            _raise_lifecycle_publication_error(
                exc,
                "PEE_IU4_AUTHORITY_COMMIT_MISMATCH",
                "Completion publication failed",
            )
        return IU4LifecycleOperationResultV1(
            operation="COMPLETE_AUTHORITY_PREPARE", target_fingerprint=target_fingerprint,
            prepare_record_fingerprint=prepare.record_fingerprint,
            commit_record_fingerprint=commit.record_fingerprint,
            outcome="AUTHORITY_PREPARE_COMPLETE_RESTART_ONLY",
        )

    def recover_and_restart(
        self,
        *,
        authorization: Any,
        consumption_event_id: str,
        materialization_event_id: str,
        consumption_timestamp_utc: str,
        expected_startup_attempt_id: str,
        fault_point: str = "",
    ) -> IU4LifecycleOperationResultV1:
        if fault_point == "BEFORE_CONSUMPTION":
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RESOURCE_EXHAUSTED", "simulated pre-Consumption crash"
            )
        consumption = self.consume_restart_authorization(
            authorization=authorization,
            operation="RECOVER_AND_RESTART",
            consumption_event_id=consumption_event_id,
            consumption_timestamp_utc=consumption_timestamp_utc,
            expected_startup_attempt_id=expected_startup_attempt_id,
        )
        if fault_point in {"AFTER_CONSUMPTION", "BEFORE_SNAPSHOT_MATERIALIZATION"}:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE",
                "simulated post-Consumption Recovery crash",
            )
        result = self.atomic_coordinator.i6_materialize_durable_head(
            expected_transaction_sequence=authorization.expected_transaction_sequence,
            expected_journal_head=authorization.expected_journal_head,
            expected_snapshot_fingerprint=authorization.expected_snapshot_fingerprint,
        )
        if fault_point in {
            "AFTER_SNAPSHOT_MATERIALIZATION", "BEFORE_RECOVERY_MATERIALIZATION"
        }:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE",
                "simulated pre-Recovery-record crash",
            )
        payload = {
            "operation": "RECOVER_AND_RESTART",
            "authorization_id": authorization.restart_recovery_authorization_id,
            "authorization_record_fingerprint": consumption.record_fingerprint,
            "materialized_state_fingerprint": result.state.state_fingerprint,
            "materialized_transaction_sequence": result.state.transaction_sequence,
            "materialized_journal_head": result.state.journal_head,
            "operator": authorization.operator,
            "timestamp_utc": consumption_timestamp_utc,
        }
        try:
            materialization = self.lifecycle_ledger.append(
                record_type="RECOVERY_MATERIALIZATION",
                lifecycle_event_id=materialization_event_id,
                payload=payload,
            )
        except (IU4LifecycleLedgerError, OSError, MemoryError) as exc:
            _raise_lifecycle_publication_error(
                exc,
                "PEE_IU4_LIFECYCLE_LEDGER_CONFLICT",
                "Recovery materialization record failed",
            )
        if fault_point == "AFTER_RECOVERY_MATERIALIZATION":
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-Recovery-record crash"
            )
        return IU4LifecycleOperationResultV1(
            operation="RECOVER_AND_RESTART",
            target_fingerprint=result.state.state_fingerprint,
            prepare_record_fingerprint=consumption.record_fingerprint,
            commit_record_fingerprint=materialization.record_fingerprint,
            outcome="RECOVERY_COMPLETE_LOOP_NOT_AUTHORIZED",
        )

    def reconcile_terminal_gap(
        self,
        *,
        authorization: Any,
        anchor: IU4PersistenceWorkerDeathTrustAnchorV1,
        proof: IU4PersistenceWorkerExclusionProofV1,
        expected_death_trust_anchor_id: str,
        expected_death_trust_anchor_fingerprint: str,
        expected_approval_fingerprint: str,
        expected_trusted_anchor_registry_fingerprint: str,
        consumption_event_id: str,
        terminal_event_id: str,
        gap_event_id: str,
        consumption_timestamp_utc: str,
        runtime_session_open_event_id: str,
        runtime_session_open_record_fingerprint: str,
        runtime_session_open_journal_head: str,
        expected_startup_attempt_id: str,
        expected_journal_root_fingerprint: str,
        expected_old_worker_id: str,
        expected_old_worker_boot_id: str,
        fault_point: str = "",
    ) -> IU4LifecycleOperationResultV1:
        # Coordinator lock is the outer lock for the complete recovery boundary.
        # Ledger mutations take their own exclusive lock inside this boundary;
        # every transition is re-derived before the next mutation.
        with self.atomic_coordinator._exclusive_root_lock():
            return self._reconcile_terminal_gap_locked(
                authorization=authorization,
                anchor=anchor,
                proof=proof,
                expected_death_trust_anchor_id=expected_death_trust_anchor_id,
                expected_death_trust_anchor_fingerprint=expected_death_trust_anchor_fingerprint,
                expected_approval_fingerprint=expected_approval_fingerprint,
                expected_trusted_anchor_registry_fingerprint=expected_trusted_anchor_registry_fingerprint,
                consumption_event_id=consumption_event_id,
                terminal_event_id=terminal_event_id,
                gap_event_id=gap_event_id,
                consumption_timestamp_utc=consumption_timestamp_utc,
                runtime_session_open_event_id=runtime_session_open_event_id,
                runtime_session_open_record_fingerprint=runtime_session_open_record_fingerprint,
                runtime_session_open_journal_head=runtime_session_open_journal_head,
                expected_startup_attempt_id=expected_startup_attempt_id,
                expected_journal_root_fingerprint=expected_journal_root_fingerprint,
                expected_old_worker_id=expected_old_worker_id,
                expected_old_worker_boot_id=expected_old_worker_boot_id,
                fault_point=fault_point,
            )

    def _reconcile_terminal_gap_locked(
        self,
        *,
        authorization: Any,
        anchor: IU4PersistenceWorkerDeathTrustAnchorV1,
        proof: IU4PersistenceWorkerExclusionProofV1,
        expected_death_trust_anchor_id: str,
        expected_death_trust_anchor_fingerprint: str,
        expected_approval_fingerprint: str,
        expected_trusted_anchor_registry_fingerprint: str,
        consumption_event_id: str,
        terminal_event_id: str,
        gap_event_id: str,
        consumption_timestamp_utc: str,
        runtime_session_open_event_id: str,
        runtime_session_open_record_fingerprint: str,
        runtime_session_open_journal_head: str,
        expected_startup_attempt_id: str,
        expected_journal_root_fingerprint: str,
        expected_old_worker_id: str,
        expected_old_worker_boot_id: str,
        fault_point: str = "",
    ) -> IU4LifecycleOperationResultV1:
        records = self._lifecycle_records_read(
            "Terminal Lifecycle records read failed before Consumption"
        )
        matching_open = [
            record for record in records
            if record.record_type == "RUNTIME_SESSION_OPEN"
            and record.lifecycle_event_id == runtime_session_open_event_id
        ]
        if len(matching_open) != 1:
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RUNTIME_SESSION_UNCLEAN", "exact Runtime Session OPEN is missing"
            )
        open_record = matching_open[0]
        open_session_id = open_record.payload.get("session_id")
        open_journal_head = open_record.payload.get("journal_head")
        if (
            self._lifecycle_view_read(
                "Terminal Lifecycle OPEN view failed before Consumption"
            ).open_runtime_session_id != open_session_id
            or proof.runtime_session_id != open_session_id
            or proof.runtime_session_open_event_id != runtime_session_open_event_id
            or open_record.record_fingerprint != runtime_session_open_record_fingerprint
            or open_journal_head != runtime_session_open_journal_head
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RUNTIME_SESSION_UNCLEAN", "Runtime Session OPEN binding differs"
            )
        current = self.atomic_coordinator.load_state()
        if fault_point == "BEFORE_PROOF_VALIDATION":
            raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated pre-proof crash")
        validate_worker_exclusion(
            anchor=anchor, proof=proof,
            expected_death_trust_anchor_id=expected_death_trust_anchor_id,
            expected_death_trust_anchor_fingerprint=expected_death_trust_anchor_fingerprint,
            expected_approval_fingerprint=expected_approval_fingerprint,
            expected_trusted_anchor_registry_fingerprint=expected_trusted_anchor_registry_fingerprint,
            runtime_session_id=open_session_id,
            runtime_session_open_event_id=runtime_session_open_event_id,
            runtime_session_open_record_fingerprint=runtime_session_open_record_fingerprint,
            authority_generation_id=current.authority_generation_id,
            authority_commit_anchor=authorization.source_authority_commit_anchor,
            coordinator_id=self.atomic_coordinator.coordinator_id,
            journal_root_fingerprint=_sha(
                expected_journal_root_fingerprint,
                "expected_journal_root_fingerprint",
            ),
            old_worker_id=_text(expected_old_worker_id, "expected_old_worker_id"),
            old_worker_boot_id=_text(
                expected_old_worker_boot_id, "expected_old_worker_boot_id"
            ),
        )
        if fault_point == "AFTER_PROOF_VALIDATION":
            raise IU4RecoveryProjectionError("PEE_IU4_RESOURCE_EXHAUSTED", "simulated post-proof crash")
        if fault_point == "BEFORE_CONSUMPTION":
            raise IU4RecoveryProjectionError(
                "PEE_IU4_RESOURCE_EXHAUSTED", "simulated pre-Consumption crash"
            )
        consumption = self.consume_restart_authorization(
            authorization=authorization, operation="RECONCILE_TERMINAL_GAP",
            consumption_event_id=consumption_event_id,
            consumption_timestamp_utc=consumption_timestamp_utc,
            expected_startup_attempt_id=expected_startup_attempt_id,
        )
        consumed_view = self._lifecycle_view_read(
            "Terminal Lifecycle view failed after Consumption"
        )
        if (
            consumed_view.ledger_tip != consumption.record_fingerprint
            or consumed_view.open_runtime_session_id != open_session_id
        ):
            raise IU4RecoveryProjectionError(
                "PEE_IU4_LIFECYCLE_EXTENSION_INVALID",
                "Lifecycle changed after Terminal authorization consumption",
            )
        if fault_point == "AFTER_CONSUMPTION":
            raise IU4RecoveryProjectionError("PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE", "simulated post-consumption crash")
        committed, gap = self._terminal_kill_and_gap_under_lifecycle_lock(
            consumption=consumption, authorization=authorization, proof=proof,
            open_session_id=open_session_id,
            runtime_session_open_event_id=runtime_session_open_event_id,
            runtime_session_open_record_fingerprint=(
                runtime_session_open_record_fingerprint
            ),
            runtime_session_open_journal_head=runtime_session_open_journal_head,
            terminal_event_id=terminal_event_id, gap_event_id=gap_event_id,
            consumption_timestamp_utc=consumption_timestamp_utc,
            fault_point=fault_point,
        )
        return IU4LifecycleOperationResultV1(
            operation="RECONCILE_TERMINAL_GAP",
            target_fingerprint=committed.state.state_fingerprint,
            prepare_record_fingerprint=consumption.record_fingerprint,
            commit_record_fingerprint=gap.record_fingerprint,
            outcome="TERMINAL_GAP_RECONCILED_LOOP_NOT_AUTHORIZED",
        )


__all__ = [
    "EMPTY", "NONE", "IU4CleanGenesisManifestV1", "IU4CompatibilityProjectionV1",
    "IU4LegacySafetySnapshotV1", "IU4PersistenceWorkerDeathTrustAnchorV1",
    "IU4PersistenceWorkerExclusionProofV1", "IU4ProjectionCursorV1",
    "IU4LifecycleOperationResultV1", "IU4ProjectionPublisherV1",
    "IU4RecoveryMonitoringReportV1", "IU4RecoveryOrchestratorV1",
    "IU4RecoveryProjectionError", "IU4StateHandoffManifestV1",
    "IU4TerminalRuntimeProfileAnchorV1",
    "IU4TerminalRuntimeProfileRegistryV1",
    "IU4TerminalMonitoringObservationV1", "build_monitoring_report",
    "canonical_json_bytes", "classify_owner_state", "projection_root_realpath_sha256",
    "handoff_mapping_record", "handoff_planned_generation_id",
    "terminal_static_bindings_fingerprint",
    "validate_worker_exclusion",
]
