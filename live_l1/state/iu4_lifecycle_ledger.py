#!/usr/bin/env python3
"""Crash-safe append-only IU4 lifecycle ledger V1.

Each record is a create-new canonical JSON file.  The directory is the log;
there is no mutable index and every derived view is rebuilt from the chain.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


EMPTY_LEDGER_TIP = "EMPTY"
NONE_AUTHORITY = "NONE"

AUTHORITY_PAIRS = {
    "LEGACY_GENESIS_PREPARE": "LEGACY_GENESIS_COMMIT",
    "ATOMIC_GENESIS_PREPARE": "ATOMIC_GENESIS_COMMIT",
    "LEGACY_TO_PEE_HANDOFF_PREPARE": "LEGACY_TO_PEE_HANDOFF_COMMIT",
    "PEE_TO_LEGACY_HANDOFF_PREPARE": "PEE_TO_LEGACY_HANDOFF_COMMIT",
    "ATOMIC_V1_TO_V2_MIGRATION_PREPARE": "ATOMIC_V1_TO_V2_MIGRATION_COMMIT",
}
AUTHORITY_COMMITS = frozenset(AUTHORITY_PAIRS.values())
NON_AUTHORITY_RECORDS = frozenset(
    {
        "RESTART_AUTH_CONSUME",
        "RECOVERY_MATERIALIZATION",
        "RUNTIME_SESSION_OPEN",
        "RUNTIME_SESSION_CLOSE_PREPARE",
        "RUNTIME_SESSION_CLOSE_COMMIT",
        "TERMINAL_GAP_RECONCILIATION",
    }
)
ALLOWED_RECORDS = frozenset(AUTHORITY_PAIRS) | AUTHORITY_COMMITS | NON_AUTHORITY_RECORDS


class IU4LifecycleLedgerError(RuntimeError):
    pass


def canonical_json(value: object) -> bytes:
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise IU4LifecycleLedgerError("ledger payload is not canonical JSON") from exc


def fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def authority_generation_id(
    *,
    operation: str,
    source_authority_generation_id: str,
    source_authority_commit_anchor: str,
    manifest_fingerprint: str,
    approval_fingerprint: str,
    target_business_payload: Mapping[str, Any],
) -> str:
    forbidden = {
        "authority_generation_id",
        "authority_prepare_record_fingerprint",
        "authority_commit_anchor",
        "ledger_tip",
    }
    if forbidden.intersection(target_business_payload):
        raise IU4LifecycleLedgerError("business payload contains authority envelope fields")
    material = {
        "schema_version": 1,
        "operation": operation,
        "source_authority_generation_id": source_authority_generation_id,
        "source_authority_commit_anchor": source_authority_commit_anchor,
        "manifest_fingerprint": manifest_fingerprint,
        "approval_fingerprint": approval_fingerprint,
        "target_business_payload_fingerprint": fingerprint(target_business_payload),
    }
    return f"IU4-AUTHORITY-GENERATION-{fingerprint(material)}"


@dataclass(frozen=True)
class IU4LifecycleRecordV1:
    schema_version: int
    lifecycle_sequence: int
    lifecycle_event_id: str
    record_type: str
    previous_record_fingerprint: str
    payload_fingerprint: str
    payload: Mapping[str, Any]
    record_fingerprint: str

    @classmethod
    def build(
        cls,
        *,
        sequence: int,
        event_id: str,
        record_type: str,
        previous: str,
        payload: Mapping[str, Any],
    ) -> "IU4LifecycleRecordV1":
        if record_type not in ALLOWED_RECORDS:
            raise IU4LifecycleLedgerError(f"unknown record type {record_type}")
        core = {
            "schema_version": 1,
            "lifecycle_sequence": sequence,
            "lifecycle_event_id": event_id,
            "record_type": record_type,
            "previous_record_fingerprint": previous,
            "payload_fingerprint": fingerprint(payload),
            "payload": dict(payload),
        }
        return cls(**core, record_fingerprint=fingerprint(core))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "IU4LifecycleRecordV1":
        fields = set(cls.__dataclass_fields__)
        if not isinstance(value, Mapping) or set(value) != fields:
            raise IU4LifecycleLedgerError("record fields are missing or unknown")
        record = cls(**dict(value))
        record.validate()
        return record

    def validate(self) -> None:
        if self.schema_version != 1:
            raise IU4LifecycleLedgerError("unknown ledger schema")
        if isinstance(self.lifecycle_sequence, bool) or self.lifecycle_sequence < 1:
            raise IU4LifecycleLedgerError("invalid lifecycle sequence")
        if not isinstance(self.lifecycle_event_id, str) or not self.lifecycle_event_id:
            raise IU4LifecycleLedgerError("empty lifecycle event id")
        if self.record_type not in ALLOWED_RECORDS:
            raise IU4LifecycleLedgerError("unknown record type")
        if self.payload_fingerprint != fingerprint(self.payload):
            raise IU4LifecycleLedgerError("payload fingerprint mismatch")
        core = {
            "schema_version": self.schema_version,
            "lifecycle_sequence": self.lifecycle_sequence,
            "lifecycle_event_id": self.lifecycle_event_id,
            "record_type": self.record_type,
            "previous_record_fingerprint": self.previous_record_fingerprint,
            "payload_fingerprint": self.payload_fingerprint,
            "payload": dict(self.payload),
        }
        if self.record_fingerprint != fingerprint(core):
            raise IU4LifecycleLedgerError("record fingerprint mismatch")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "lifecycle_sequence": self.lifecycle_sequence,
            "lifecycle_event_id": self.lifecycle_event_id,
            "record_type": self.record_type,
            "previous_record_fingerprint": self.previous_record_fingerprint,
            "payload_fingerprint": self.payload_fingerprint,
            "payload": dict(self.payload),
            "record_fingerprint": self.record_fingerprint,
        }


@dataclass(frozen=True)
class IU4LifecycleLedgerViewV1:
    ledger_tip: str
    authority_commit_anchor: str
    authority_generation_id: str
    owner_epoch: int
    open_authority_prepare_event_id: str
    open_runtime_session_id: str
    consumed_authorization_ids: frozenset[str]
    record_count: int

    @property
    def loop_start_allowed(self) -> bool:
        return not self.open_authority_prepare_event_id and not self.open_runtime_session_id


class IU4LifecycleLedgerV1:
    def __init__(self, root: str | Path) -> None:
        root = Path(root)
        if not root.is_absolute():
            raise IU4LifecycleLedgerError("ledger root must be absolute")
        self.root = root
        self.records_directory = root / "records"
        self.lock_path = root / "writer.lock"

    def initialize(self) -> None:
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.root.is_symlink() or self.root.resolve() != self.root.absolute():
            raise IU4LifecycleLedgerError("ledger root must not be a symlink")
        self.records_directory.mkdir(mode=0o700, exist_ok=True)
        if self.records_directory.is_symlink():
            raise IU4LifecycleLedgerError("records directory must not be a symlink")
        fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR | os.O_CLOEXEC, 0o600)
        os.close(fd)
        self._fsync_directory(self.root)

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def _paths(self) -> list[Path]:
        if not self.records_directory.exists():
            return []
        paths = sorted(self.records_directory.iterdir(), key=lambda p: p.name)
        for path in paths:
            if path.is_symlink() or not path.is_file() or not path.name.endswith(".json"):
                raise IU4LifecycleLedgerError("unknown ledger directory entry")
        return paths

    def records(self) -> tuple[IU4LifecycleRecordV1, ...]:
        result: list[IU4LifecycleRecordV1] = []
        previous = EMPTY_LEDGER_TIP
        events: set[str] = set()
        for expected, path in enumerate(self._paths(), 1):
            if path.name != f"{expected:020d}.json":
                raise IU4LifecycleLedgerError("ledger sequence gap or duplicate")
            try:
                raw = path.read_bytes()
                value = json.loads(raw.decode("ascii"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise IU4LifecycleLedgerError("truncated or unreadable ledger record") from exc
            if raw != canonical_json(value) + b"\n":
                raise IU4LifecycleLedgerError("record bytes are not canonical")
            record = IU4LifecycleRecordV1.from_mapping(value)
            if record.lifecycle_sequence != expected:
                raise IU4LifecycleLedgerError("record sequence mismatch")
            if record.previous_record_fingerprint != previous:
                raise IU4LifecycleLedgerError("ledger fork or chain gap")
            if record.lifecycle_event_id in events:
                raise IU4LifecycleLedgerError("duplicate lifecycle event id")
            events.add(record.lifecycle_event_id)
            previous = record.record_fingerprint
            result.append(record)
        self._derive(result)
        return tuple(result)

    def view(self) -> IU4LifecycleLedgerViewV1:
        return self._derive(self.records())

    @staticmethod
    def _derive(records: Iterable[IU4LifecycleRecordV1]) -> IU4LifecycleLedgerViewV1:
        tip = EMPTY_LEDGER_TIP
        anchor = NONE_AUTHORITY
        generation = NONE_AUTHORITY
        owner_epoch = 0
        open_prepare: IU4LifecycleRecordV1 | None = None
        open_session = ""
        close_prepared = False
        consumed: dict[str, str] = {}
        count = 0
        for record in records:
            count += 1
            tip = record.record_fingerprint
            payload = record.payload
            if record.record_type in AUTHORITY_PAIRS:
                if open_prepare is not None:
                    raise IU4LifecycleLedgerError("multiple open authority PREPARE records")
                open_prepare = record
            elif record.record_type in AUTHORITY_COMMITS:
                if open_prepare is None or AUTHORITY_PAIRS[open_prepare.record_type] != record.record_type:
                    raise IU4LifecycleLedgerError("authority COMMIT has no matching PREPARE")
                if payload.get("prepare_record_fingerprint") != open_prepare.record_fingerprint:
                    raise IU4LifecycleLedgerError("authority COMMIT/PREPARE mismatch")
                generation_value = payload.get("authority_generation_id")
                owner_value = payload.get("new_owner_epoch")
                if generation_value != open_prepare.payload.get("authority_generation_id"):
                    raise IU4LifecycleLedgerError("authority generation mismatch")
                if isinstance(owner_value, bool) or not isinstance(owner_value, int) or owner_value != owner_epoch + 1:
                    raise IU4LifecycleLedgerError("owner epoch is not monotonic")
                generation = str(generation_value)
                owner_epoch = owner_value
                anchor = record.record_fingerprint
                open_prepare = None
            elif record.record_type == "RESTART_AUTH_CONSUME":
                auth = payload.get("authorization_id")
                auth_fp = payload.get("authorization_fingerprint")
                if not isinstance(auth, str) or not auth or not isinstance(auth_fp, str):
                    raise IU4LifecycleLedgerError("invalid authorization consumption")
                if auth in consumed:
                    raise IU4LifecycleLedgerError("authorization was consumed more than once")
                consumed[auth] = auth_fp
            elif record.record_type == "RUNTIME_SESSION_OPEN":
                session = payload.get("session_id")
                if open_session or not isinstance(session, str) or not session:
                    raise IU4LifecycleLedgerError("invalid or overlapping runtime session")
                open_session = session
                close_prepared = False
            elif record.record_type == "RUNTIME_SESSION_CLOSE_PREPARE":
                if not open_session or payload.get("session_id") != open_session or close_prepared:
                    raise IU4LifecycleLedgerError("invalid runtime close PREPARE")
                close_prepared = True
            elif record.record_type == "RUNTIME_SESSION_CLOSE_COMMIT":
                if not open_session or payload.get("session_id") != open_session or not close_prepared:
                    raise IU4LifecycleLedgerError("invalid runtime close COMMIT")
                open_session = ""
                close_prepared = False
            elif record.record_type == "TERMINAL_GAP_RECONCILIATION":
                if not open_session or payload.get("session_id") != open_session:
                    raise IU4LifecycleLedgerError("terminal gap does not match open session")
                open_session = ""
                close_prepared = False
        return IU4LifecycleLedgerViewV1(
            ledger_tip=tip,
            authority_commit_anchor=anchor,
            authority_generation_id=generation,
            owner_epoch=owner_epoch,
            open_authority_prepare_event_id=("" if open_prepare is None else open_prepare.lifecycle_event_id),
            open_runtime_session_id=open_session,
            consumed_authorization_ids=frozenset(consumed),
            record_count=count,
        )

    def append(
        self,
        *,
        record_type: str,
        lifecycle_event_id: str,
        payload: Mapping[str, Any],
    ) -> IU4LifecycleRecordV1:
        self.initialize()
        lock_fd = os.open(self.lock_path, os.O_RDWR | os.O_CLOEXEC)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            current = self.records()
            sequence = len(current) + 1
            previous = EMPTY_LEDGER_TIP if not current else current[-1].record_fingerprint
            record = IU4LifecycleRecordV1.build(
                sequence=sequence,
                event_id=lifecycle_event_id,
                record_type=record_type,
                previous=previous,
                payload=payload,
            )
            candidate = list(current) + [record]
            self._derive(candidate)
            path = self.records_directory / f"{sequence:020d}.json"
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600)
            data = canonical_json(record.to_mapping()) + b"\n"
            try:
                written = 0
                while written < len(data):
                    count = os.write(fd, data[written:])
                    if count <= 0:
                        raise IU4LifecycleLedgerError("short ledger write")
                    written += count
                os.fsync(fd)
            finally:
                os.close(fd)
            self._fsync_directory(self.records_directory)
            readback = self.records()
            if readback[-1] != record:
                raise IU4LifecycleLedgerError("ledger readback mismatch")
            return record
        finally:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            finally:
                os.close(lock_fd)

    def consume_restart_authorization(
        self,
        *,
        lifecycle_event_id: str,
        authorization_id: str,
        authorization_fingerprint: str,
        operation: str,
        operator: str,
        startup_attempt_id: str,
        pre_state_fingerprint: str,
        pre_journal_head: str,
        pre_attempt_ledger_tip: str,
        source_authority_generation_id: str,
        source_authority_commit_anchor: str,
        consumption_timestamp_utc: str,
        completion_prepare_event_id: str = "NONE",
        completion_prepare_fingerprint: str = "NONE",
        target_authority_generation_id: str = "NONE",
    ) -> IU4LifecycleRecordV1:
        view = self.view()
        if pre_attempt_ledger_tip != view.ledger_tip:
            raise IU4LifecycleLedgerError("pre-attempt ledger tip mismatch")
        if authorization_id in view.consumed_authorization_ids:
            raise IU4LifecycleLedgerError("authorization already consumed")
        completion = operation == "COMPLETE_AUTHORITY_PREPARE"
        for value in (
            completion_prepare_event_id,
            completion_prepare_fingerprint,
            target_authority_generation_id,
        ):
            if completion == (value == "NONE"):
                raise IU4LifecycleLedgerError("completion fields are not canonical")
        payload = {
            "authorization_id": authorization_id,
            "authorization_fingerprint": authorization_fingerprint,
            "operation": operation,
            "operator": operator,
            "startup_attempt_id": startup_attempt_id,
            "pre_state_fingerprint": pre_state_fingerprint,
            "pre_journal_head": pre_journal_head,
            "pre_attempt_ledger_tip": pre_attempt_ledger_tip,
            "source_authority_generation_id": source_authority_generation_id,
            "source_authority_commit_anchor": source_authority_commit_anchor,
            "consumption_timestamp_utc": consumption_timestamp_utc,
            "completion_prepare_event_id": completion_prepare_event_id,
            "completion_prepare_fingerprint": completion_prepare_fingerprint,
            "target_authority_generation_id": target_authority_generation_id,
        }
        return self.append(
            record_type="RESTART_AUTH_CONSUME",
            lifecycle_event_id=lifecycle_event_id,
            payload=payload,
        )


__all__ = [
    "ALLOWED_RECORDS",
    "AUTHORITY_PAIRS",
    "EMPTY_LEDGER_TIP",
    "IU4LifecycleLedgerError",
    "IU4LifecycleLedgerV1",
    "IU4LifecycleLedgerViewV1",
    "IU4LifecycleRecordV1",
    "NONE_AUTHORITY",
    "authority_generation_id",
    "canonical_json",
    "fingerprint",
]
