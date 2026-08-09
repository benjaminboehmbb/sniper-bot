#!/usr/bin/env python3
"""Atomic persistence and restart recovery for paper entry throttling.

Each accepted entry is durably journaled before the throttle snapshot advances.
The immutable envelope contains both the event and its resulting state, allowing
an interrupted write to be recovered exactly once.

This store is not wired into the active L1 runtime yet.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    EntryThrottleReasonCode,
    PaperEntryThrottleError,
    PaperEntryThrottlePolicy,
    PaperEntryThrottleState,
    apply_accepted_entry,
)


ARTIFACT_ENTRY_THROTTLE_ENVELOPE = "paper_entry_throttle_event"


class EntryThrottleStoreReasonCode:
    STATE_MISSING = "PEE_RATE_STATE_MISSING"
    STATE_ALREADY_INITIALIZED = "PEE_RATE_STATE_ALREADY_INITIALIZED"
    JSON_INVALID = "PEE_RATE_JSON_INVALID"
    JOURNAL_CONFLICT = "PEE_RATE_JOURNAL_CONFLICT"
    JOURNAL_GAP = "PEE_RATE_JOURNAL_GAP"
    STATE_AHEAD_OF_JOURNAL = "PEE_RATE_STATE_AHEAD_OF_JOURNAL"
    RECOVERY_REQUIRED = "PEE_RATE_RECOVERY_REQUIRED"


class PaperEntryThrottleStoreError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


class SimulatedEntryThrottleInterruption(RuntimeError):
    """Test-only interruption after the durable journal write."""


def _canonical_json_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"{field_name} must be a string",
        )
    result = value.strip()
    if len(result) != 64 or any(
        character not in "0123456789abcdef" for character in result
    ):
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"{field_name} must be a lowercase SHA-256 hex digest",
        )
    return result


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PaperEntryThrottleStoreError(
            EntryThrottleStoreReasonCode.JSON_INVALID,
            f"cannot read valid JSON object from {path}",
        ) from exc
    if not isinstance(value, dict):
        raise PaperEntryThrottleStoreError(
            EntryThrottleStoreReasonCode.JSON_INVALID,
            f"JSON root in {path} must be an object",
        )
    return value


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


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        _fsync_directory(path.parent)
    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


@dataclass(frozen=True)
class EntryThrottleEnvelopeV1:
    schema_version: int
    state_before_fingerprint: str
    event: AcceptedEntryEventV1
    state_after: PaperEntryThrottleState

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "EntryThrottleEnvelopeV1 requires schema_version 1",
            )
        object.__setattr__(
            self,
            "state_before_fingerprint",
            _sha256_text(
                self.state_before_fingerprint,
                "state_before_fingerprint",
            ),
        )
        if self.state_after.total_accepted_entry_count != self.event.entry_sequence:
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "envelope state and event sequences differ",
            )
        if (
            self.state_after.last_entry_event_id != self.event.entry_event_id
            or self.state_after.last_update_event_id != self.event.entry_event_id
            or self.state_after.recent_entry_events[-1].event_fingerprint
            != self.event.event_fingerprint
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "envelope state does not reference its entry event",
            )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_type": ARTIFACT_ENTRY_THROTTLE_ENVELOPE,
            "state_before_fingerprint": self.state_before_fingerprint,
            "event": self.event.to_record(),
            "state_after": self.state_after.to_record(),
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "EntryThrottleEnvelopeV1":
        schema_version = record.get("schema_version")
        if (
            isinstance(schema_version, bool)
            or not isinstance(schema_version, int)
            or schema_version != 1
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "entry throttle envelope schema is unsupported",
            )
        if record.get("artifact_type") != ARTIFACT_ENTRY_THROTTLE_ENVELOPE:
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "entry throttle envelope artifact type is invalid",
            )
        event_raw = record.get("event")
        state_raw = record.get("state_after")
        if not isinstance(event_raw, Mapping) or not isinstance(state_raw, Mapping):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "entry throttle envelope requires event and state_after objects",
            )
        return cls(
            schema_version=record.get("schema_version"),
            state_before_fingerprint=record.get("state_before_fingerprint"),
            event=AcceptedEntryEventV1.from_record(event_raw),
            state_after=PaperEntryThrottleState.from_record(state_raw),
        )

    @property
    def envelope_fingerprint(self) -> str:
        return _canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class EntryThrottleCommitResult:
    state: PaperEntryThrottleState
    journal_path: Path
    newly_committed: bool
    already_committed: bool
    recovered_incomplete_commit: bool


@dataclass(frozen=True)
class EntryThrottleRecoveryResult:
    state: PaperEntryThrottleState
    journal_count: int
    recovered_entry_count: int


@dataclass(frozen=True)
class EntryThrottleReconciliationReport:
    consistent: bool
    entry_allowed: bool
    exit_allowed: bool
    reason_codes: tuple[str, ...]
    state_entry_count: int
    journal_entry_count: int


class PaperEntryThrottleStore:
    """Single-writer store for one profile-bound entry throttle."""

    def __init__(
        self,
        root_directory: str | Path,
        policy: PaperEntryThrottlePolicy,
    ) -> None:
        self.root_directory = Path(root_directory)
        self.policy = policy
        self.state_path = self.root_directory / "paper_entry_throttle.json"
        self.event_directory = self.root_directory / "entry_throttle_events"

    def _ensure_policy_state(self, state: PaperEntryThrottleState) -> None:
        if (
            state.policy_model_version != self.policy.policy_model_version
            or state.policy_profile_id != self.policy.policy_profile_id
            or state.policy_fingerprint != self.policy.policy_fingerprint
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.POLICY_MISMATCH,
                "throttle state does not match store policy",
            )

    def _ensure_policy_event(self, event: AcceptedEntryEventV1) -> None:
        if (
            event.policy_model_version != self.policy.policy_model_version
            or event.policy_profile_id != self.policy.policy_profile_id
            or event.policy_fingerprint != self.policy.policy_fingerprint
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.POLICY_MISMATCH,
                "entry event does not match store policy",
            )

    def initialize(self, state: PaperEntryThrottleState) -> PaperEntryThrottleState:
        self._ensure_policy_state(state)
        if state.total_accepted_entry_count != 0:
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.STATE_AHEAD_OF_JOURNAL,
                "new throttle store must be initialized with an empty state",
            )
        if self.state_path.exists():
            existing = self.load_state()
            if existing == state:
                return existing
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.STATE_ALREADY_INITIALIZED,
                "paper entry throttle already exists with different state",
            )
        if self.event_directory.exists() and any(self.event_directory.glob("*.json")):
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                "cannot initialize throttle while entry journal is non-empty",
            )
        _atomic_write_json(self.state_path, state.to_record())
        return state

    def load_state(self) -> PaperEntryThrottleState:
        if not self.state_path.exists():
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.STATE_MISSING,
                "paper entry throttle has not been initialized",
            )
        state = PaperEntryThrottleState.from_record(_read_json_object(self.state_path))
        self._ensure_policy_state(state)
        return state

    def _journal_path(self, event: AcceptedEntryEventV1) -> Path:
        event_id_hash = hashlib.sha256(event.entry_event_id.encode("utf-8")).hexdigest()[:20]
        filename = f"{event.entry_sequence:020d}_{event_id_hash}.json"
        return self.event_directory / filename

    def _load_envelope(self, path: Path) -> EntryThrottleEnvelopeV1:
        envelope = EntryThrottleEnvelopeV1.from_record(_read_json_object(path))
        self._ensure_policy_event(envelope.event)
        self._ensure_policy_state(envelope.state_after)
        return envelope

    def _journal_envelopes(self) -> list[tuple[Path, EntryThrottleEnvelopeV1]]:
        if not self.event_directory.exists():
            return []
        entries = [
            (path, self._load_envelope(path))
            for path in sorted(self.event_directory.glob("*.json"))
        ]
        for path, envelope in entries:
            if path != self._journal_path(envelope.event):
                raise PaperEntryThrottleStoreError(
                    EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                    "entry journal filename does not match its event identity",
                )
        self._validate_journal_chain(entries)
        return entries

    def _validate_journal_chain(
        self,
        entries: list[tuple[Path, EntryThrottleEnvelopeV1]],
    ) -> None:
        previous: EntryThrottleEnvelopeV1 | None = None
        event_ids: set[str] = set()
        for expected_sequence, (_, envelope) in enumerate(entries, start=1):
            event = envelope.event
            if event.entry_sequence != expected_sequence:
                raise PaperEntryThrottleStoreError(
                    EntryThrottleStoreReasonCode.JOURNAL_GAP,
                    f"journal expected sequence {expected_sequence} but found {event.entry_sequence}",
                )
            if event.entry_event_id in event_ids:
                raise PaperEntryThrottleStoreError(
                    EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                    f"duplicate journal entry_event_id {event.entry_event_id}",
                )
            event_ids.add(event.entry_event_id)
            if previous is None:
                if event.previous_entry_event_id:
                    raise PaperEntryThrottleStoreError(
                        EntryThrottleStoreReasonCode.JOURNAL_GAP,
                        "first journal entry must not reference a predecessor",
                    )
                replay_before = PaperEntryThrottleState.initial(
                    self.policy,
                    utc_day=event.entry_timestamp_utc[:10],
                )
            else:
                if event.previous_entry_event_id != previous.event.entry_event_id:
                    raise PaperEntryThrottleStoreError(
                        EntryThrottleStoreReasonCode.JOURNAL_GAP,
                        "journal previous-entry chain is broken",
                    )
                if envelope.state_before_fingerprint != previous.state_after.state_fingerprint:
                    raise PaperEntryThrottleStoreError(
                        EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                        "journal state fingerprint chain is broken",
                    )
                replay_before = previous.state_after
            try:
                replay_after = apply_accepted_entry(
                    replay_before,
                    self.policy,
                    event,
                )
            except PaperEntryThrottleError as exc:
                raise PaperEntryThrottleStoreError(
                    EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                    "entry journal contains a policy-invalid transition",
                ) from exc
            if replay_after != envelope.state_after:
                raise PaperEntryThrottleStoreError(
                    EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                    "entry journal resulting state is not reproducible",
                )
            previous = envelope

    @staticmethod
    def _assert_snapshot_matches_journal(
        state: PaperEntryThrottleState,
        entries: list[tuple[Path, EntryThrottleEnvelopeV1]],
    ) -> None:
        journal_count = len(entries)
        if state.total_accepted_entry_count > journal_count:
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.STATE_AHEAD_OF_JOURNAL,
                "throttle state contains more entries than its journal",
            )
        if state.total_accepted_entry_count < journal_count:
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.RECOVERY_REQUIRED,
                "entry journal is ahead of throttle state",
            )
        if entries and state != entries[-1][1].state_after:
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                "throttle state does not match journal head",
            )

    def commit_entry(
        self,
        event: AcceptedEntryEventV1,
        *,
        simulate_interruption_after_journal: bool = False,
    ) -> EntryThrottleCommitResult:
        self._ensure_policy_event(event)
        current = self.load_state()
        journal_path = self._journal_path(event)
        entries = self._journal_envelopes()

        duplicate_identity = next(
            (
                existing
                for _, existing in entries
                if existing.event.entry_event_id == event.entry_event_id
            ),
            None,
        )
        if duplicate_identity is not None and not journal_path.exists():
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                "entry_event_id already exists under a different sequence",
            )

        if journal_path.exists():
            existing = self._load_envelope(journal_path)
            if existing.event.event_fingerprint != event.event_fingerprint:
                raise PaperEntryThrottleStoreError(
                    EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                    "same entry identity contains different event data",
                )
            if current == existing.state_after or (
                current.total_accepted_entry_count > event.entry_sequence
                and entries
                and current == entries[-1][1].state_after
            ):
                return EntryThrottleCommitResult(
                    state=current,
                    journal_path=journal_path,
                    newly_committed=False,
                    already_committed=True,
                    recovered_incomplete_commit=False,
                )
            if current.state_fingerprint == existing.state_before_fingerprint:
                if len(entries) != event.entry_sequence:
                    raise PaperEntryThrottleStoreError(
                        EntryThrottleStoreReasonCode.RECOVERY_REQUIRED,
                        "entry journal contains later events and requires full recovery",
                    )
                _atomic_write_json(self.state_path, existing.state_after.to_record())
                return EntryThrottleCommitResult(
                    state=existing.state_after,
                    journal_path=journal_path,
                    newly_committed=False,
                    already_committed=False,
                    recovered_incomplete_commit=True,
                )
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                "existing journal entry does not match current or resulting state",
            )

        self._assert_snapshot_matches_journal(current, entries)
        state_after = apply_accepted_entry(current, self.policy, event)
        envelope = EntryThrottleEnvelopeV1(
            schema_version=1,
            state_before_fingerprint=current.state_fingerprint,
            event=event,
            state_after=state_after,
        )
        _atomic_write_json(journal_path, envelope.to_record())

        if simulate_interruption_after_journal:
            raise SimulatedEntryThrottleInterruption(
                "simulated interruption after durable entry-throttle journal"
            )

        _atomic_write_json(self.state_path, state_after.to_record())
        return EntryThrottleCommitResult(
            state=state_after,
            journal_path=journal_path,
            newly_committed=True,
            already_committed=False,
            recovered_incomplete_commit=False,
        )

    def reconciliation_report(self) -> EntryThrottleReconciliationReport:
        try:
            state = self.load_state()
            entries = self._journal_envelopes()
            self._assert_snapshot_matches_journal(state, entries)
        except (PaperEntryThrottleStoreError, PaperEntryThrottleError) as exc:
            reason_code = getattr(
                exc,
                "reason_code",
                EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
            )
            state_count = 0
            journal_count = 0
            try:
                state_count = self.load_state().total_accepted_entry_count
            except (PaperEntryThrottleStoreError, PaperEntryThrottleError):
                pass
            try:
                journal_count = len(self._journal_envelopes())
            except (PaperEntryThrottleStoreError, PaperEntryThrottleError):
                pass
            return EntryThrottleReconciliationReport(
                consistent=False,
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(reason_code,),
                state_entry_count=state_count,
                journal_entry_count=journal_count,
            )

        return EntryThrottleReconciliationReport(
            consistent=True,
            entry_allowed=True,
            exit_allowed=True,
            reason_codes=(),
            state_entry_count=state.total_accepted_entry_count,
            journal_entry_count=len(entries),
        )

    def recover(self) -> EntryThrottleRecoveryResult:
        current = self.load_state()
        entries = self._journal_envelopes()
        journal_count = len(entries)
        state_count = current.total_accepted_entry_count

        if state_count > journal_count:
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.STATE_AHEAD_OF_JOURNAL,
                "throttle state contains more entries than its journal",
            )
        if state_count == journal_count:
            self._assert_snapshot_matches_journal(current, entries)
            return EntryThrottleRecoveryResult(
                state=current,
                journal_count=journal_count,
                recovered_entry_count=0,
            )

        next_envelope = entries[state_count][1]
        if current.state_fingerprint != next_envelope.state_before_fingerprint:
            raise PaperEntryThrottleStoreError(
                EntryThrottleStoreReasonCode.JOURNAL_CONFLICT,
                "throttle state is not a prefix of its entry journal",
            )
        recovered_count = journal_count - state_count
        recovered_state = entries[-1][1].state_after
        _atomic_write_json(self.state_path, recovered_state.to_record())
        return EntryThrottleRecoveryResult(
            state=recovered_state,
            journal_count=journal_count,
            recovered_entry_count=recovered_count,
        )
