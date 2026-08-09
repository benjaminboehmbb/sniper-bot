#!/usr/bin/env python3
"""Versioned S2 V2 snapshot and transition-journal persistence.

The immutable transition journal is written before the current-position
snapshot.  Every envelope contains complete before/after states, so a restart
can finish an interrupted OPEN or CLOSE exactly once without reconstructing
economic values from legacy floats.

This store is not connected to the active L1 loop.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from live_l1.core.paper_economics import PaperEconomicsConfig
from live_l1.state.paper_artifacts import (
    ArtifactReasonCode,
    LegacyArtifact,
    PaperArtifactError,
    PositionArtifactV2,
    PositionStateS2FlatV2,
    PositionStateS2V2,
    canonical_json_sha256,
    parse_position_artifact,
)


ARTIFACT_S2_TRANSITION = "paper_s2_transition"
TRANSITION_OPEN = "OPEN"
TRANSITION_CLOSE = "CLOSE"


class PaperPositionStoreReasonCode:
    STATE_MISSING = "PEE_S2_STATE_MISSING"
    STATE_ALREADY_INITIALIZED = "PEE_S2_STATE_ALREADY_INITIALIZED"
    JSON_INVALID = "PEE_S2_JSON_INVALID"
    JOURNAL_CONFLICT = "PEE_S2_JOURNAL_CONFLICT"
    JOURNAL_GAP = "PEE_S2_JOURNAL_GAP"
    RECOVERY_REQUIRED = "PEE_S2_RECOVERY_REQUIRED"
    TRANSITION_INVALID = "PEE_S2_TRANSITION_INVALID"


class PaperPositionStoreError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


class SimulatedPositionTransitionInterruption(RuntimeError):
    """Test-only interruption after a durable transition journal write."""


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.JSON_INVALID,
            f"cannot read valid JSON object from {path}",
        ) from exc
    if not isinstance(value, dict):
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.JSON_INVALID,
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


def _non_empty_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
            f"{field_name} must be a non-empty string",
        )
    return value.strip()


def _optional_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
            f"{field_name} must be a string",
        )
    return value.strip()


def _positive_integer(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
            f"{field_name} must be an integer >= 1",
        )
    return value


def _non_negative_integer(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
            f"{field_name} must be an integer >= 0",
        )
    return value


def _canonical_utc_seconds(value: object, field_name: str) -> str:
    text = _non_empty_text(value, field_name)
    try:
        parsed = datetime.fromisoformat(
            text[:-1] + "+00:00" if text.endswith("Z") else text
        )
    except ValueError as exc:
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
            f"{field_name} must be an ISO-8601 timestamp",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.microsecond:
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
            f"{field_name} must be timezone-aware with whole-second resolution",
        )
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def _position_from_record(record: Mapping[str, Any]) -> PositionArtifactV2:
    state = parse_position_artifact(record)
    if isinstance(state, LegacyArtifact):
        raise PaperArtifactError(
            ArtifactReasonCode.LEGACY_ECONOMICS_INCOMPLETE,
            "legacy S2 state is not valid in the V2 position store",
        )
    return state


def _validate_transition(
    transition_type: str,
    state_before: PositionArtifactV2,
    state_after: PositionArtifactV2,
) -> None:
    if (
        state_before.symbol != state_after.symbol
        or state_before.economics_profile_id != state_after.economics_profile_id
        or state_before.economics_model_version != state_after.economics_model_version
        or state_before.config_fingerprint != state_after.config_fingerprint
    ):
        raise PaperPositionStoreError(
            PaperPositionStoreReasonCode.TRANSITION_INVALID,
            "S2 transition identity must not change",
        )

    if transition_type == TRANSITION_OPEN:
        if not isinstance(state_before, PositionStateS2FlatV2) or not isinstance(
            state_after,
            PositionStateS2V2,
        ):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "OPEN transition must move from FLAT to LONG/SHORT",
            )
        return

    if transition_type == TRANSITION_CLOSE:
        if not isinstance(state_before, PositionStateS2V2) or not isinstance(
            state_after,
            PositionStateS2FlatV2,
        ):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "CLOSE transition must move from LONG/SHORT to FLAT",
            )
        if state_after.last_closed_trade_id != state_before.trade_id:
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "FLAT state must reference the trade closed by the transition",
            )
        return

    raise PaperPositionStoreError(
        PaperPositionStoreReasonCode.TRANSITION_INVALID,
        "transition_type must be OPEN or CLOSE",
    )


@dataclass(frozen=True)
class PositionTransitionEnvelopeV1:
    schema_version: int
    transition_sequence: int
    transition_event_id: str
    previous_transition_event_id: str
    transition_type: str
    transition_timestamp_utc: str
    transition_tick_id: int
    state_before: PositionArtifactV2
    state_after: PositionArtifactV2

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "PositionTransitionEnvelopeV1 requires schema_version 1",
            )
        object.__setattr__(
            self,
            "transition_sequence",
            _positive_integer(self.transition_sequence, "transition_sequence"),
        )
        object.__setattr__(
            self,
            "transition_event_id",
            _non_empty_text(self.transition_event_id, "transition_event_id"),
        )
        object.__setattr__(
            self,
            "previous_transition_event_id",
            _optional_text(
                self.previous_transition_event_id,
                "previous_transition_event_id",
            ),
        )
        if self.transition_sequence == 1 and self.previous_transition_event_id:
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "first S2 transition must not reference a predecessor",
            )
        if self.transition_sequence > 1 and not self.previous_transition_event_id:
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "S2 transition after sequence 1 must reference its predecessor",
            )
        transition_type = _non_empty_text(
            self.transition_type,
            "transition_type",
        ).upper()
        object.__setattr__(self, "transition_type", transition_type)
        object.__setattr__(
            self,
            "transition_timestamp_utc",
            _canonical_utc_seconds(
                self.transition_timestamp_utc,
                "transition_timestamp_utc",
            ),
        )
        object.__setattr__(
            self,
            "transition_tick_id",
            _non_negative_integer(self.transition_tick_id, "transition_tick_id"),
        )
        _validate_transition(transition_type, self.state_before, self.state_after)
        if transition_type == TRANSITION_OPEN:
            if (
                self.transition_timestamp_utc
                != self.state_after.entry_timestamp_utc
                or self.transition_tick_id != self.state_after.entry_tick_id
            ):
                raise PaperPositionStoreError(
                    PaperPositionStoreReasonCode.TRANSITION_INVALID,
                    "OPEN event time/tick must equal the persisted entry time/tick",
                )
        elif (
            self.transition_timestamp_utc < self.state_before.entry_timestamp_utc
            or self.transition_tick_id < self.state_before.entry_tick_id
        ):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "CLOSE event must not precede the persisted entry time/tick",
            )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_type": ARTIFACT_S2_TRANSITION,
            "transition_sequence": self.transition_sequence,
            "transition_event_id": self.transition_event_id,
            "previous_transition_event_id": self.previous_transition_event_id,
            "transition_type": self.transition_type,
            "transition_timestamp_utc": self.transition_timestamp_utc,
            "transition_tick_id": self.transition_tick_id,
            "state_before": self.state_before.to_record(),
            "state_after": self.state_after.to_record(),
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PositionTransitionEnvelopeV1":
        if record.get("artifact_type") != ARTIFACT_S2_TRANSITION:
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "S2 transition artifact type is invalid",
            )
        before_raw = record.get("state_before")
        after_raw = record.get("state_after")
        if not isinstance(before_raw, Mapping) or not isinstance(after_raw, Mapping):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "S2 transition requires state_before and state_after objects",
            )
        return cls(
            schema_version=record.get("schema_version"),
            transition_sequence=record.get("transition_sequence"),
            transition_event_id=record.get("transition_event_id"),
            previous_transition_event_id=record.get("previous_transition_event_id"),
            transition_type=record.get("transition_type"),
            transition_timestamp_utc=record.get("transition_timestamp_utc"),
            transition_tick_id=record.get("transition_tick_id"),
            state_before=_position_from_record(before_raw),
            state_after=_position_from_record(after_raw),
        )

    @property
    def envelope_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class PositionTransitionCommitResult:
    state: PositionArtifactV2
    journal_path: Path
    newly_committed: bool
    already_committed: bool
    recovered_incomplete_commit: bool


@dataclass(frozen=True)
class PositionRecoveryResult:
    state: PositionArtifactV2
    journal_count: int
    recovered_transition_count: int


@dataclass(frozen=True)
class PositionReconciliationReport:
    consistent: bool
    entry_allowed: bool
    exit_allowed: bool
    reason_codes: tuple[str, ...]
    journal_transition_count: int
    current_position: str


class PaperPositionStore:
    """Single-writer V2 position store bound to one symbol and PEE profile."""

    def __init__(
        self,
        root_directory: str | Path,
        config: PaperEconomicsConfig,
        *,
        symbol: str,
    ) -> None:
        self.root_directory = Path(root_directory)
        self.config = config
        self.symbol = _non_empty_text(symbol, "symbol")
        self.state_path = self.root_directory / "paper_s2_position.json"
        self.transition_directory = self.root_directory / "paper_s2_transitions"

    def _ensure_identity(self, state: PositionArtifactV2) -> None:
        if (
            state.symbol != self.symbol
            or state.economics_profile_id != self.config.economics_profile_id
            or state.economics_model_version != self.config.economics_model_version
            or state.config_fingerprint != self.config.config_fingerprint
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.CONFIG_MISMATCH,
                "S2 V2 state does not match store symbol/profile identity",
            )

    def initialize(self, state: PositionStateS2FlatV2) -> PositionStateS2FlatV2:
        if not isinstance(state, PositionStateS2FlatV2):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "S2 V2 store must be initialized FLAT",
            )
        self._ensure_identity(state)
        if self.state_path.exists():
            existing = self.load_state()
            if existing == state:
                return state
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.STATE_ALREADY_INITIALIZED,
                "S2 V2 store already exists with different state",
            )
        if self.transition_directory.exists() and any(
            self.transition_directory.glob("*.json")
        ):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
                "cannot initialize S2 V2 while transition journal is non-empty",
            )
        _atomic_write_json(self.state_path, state.to_record())
        return state

    def load_state(self) -> PositionArtifactV2:
        if not self.state_path.exists():
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.STATE_MISSING,
                "S2 V2 state has not been initialized",
            )
        state = _position_from_record(_read_json_object(self.state_path))
        self._ensure_identity(state)
        return state

    def _journal_path(self, sequence: int, event_id: str) -> Path:
        event_hash = hashlib.sha256(event_id.encode("utf-8")).hexdigest()[:20]
        return self.transition_directory / f"{sequence:020d}_{event_hash}.json"

    def _load_envelope(self, path: Path) -> PositionTransitionEnvelopeV1:
        envelope = PositionTransitionEnvelopeV1.from_record(_read_json_object(path))
        self._ensure_identity(envelope.state_before)
        self._ensure_identity(envelope.state_after)
        return envelope

    def _journal_envelopes(self) -> list[tuple[Path, PositionTransitionEnvelopeV1]]:
        if not self.transition_directory.exists():
            return []
        entries = [
            (path, self._load_envelope(path))
            for path in sorted(self.transition_directory.glob("*.json"))
        ]
        previous: PositionTransitionEnvelopeV1 | None = None
        event_ids: set[str] = set()
        trade_ids: set[str] = set()
        for expected_sequence, (path, envelope) in enumerate(entries, start=1):
            if envelope.transition_sequence != expected_sequence:
                raise PaperPositionStoreError(
                    PaperPositionStoreReasonCode.JOURNAL_GAP,
                    "S2 transition journal sequence is not contiguous",
                )
            if path != self._journal_path(
                envelope.transition_sequence,
                envelope.transition_event_id,
            ):
                raise PaperPositionStoreError(
                    PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
                    "S2 transition filename does not match its identity",
                )
            if envelope.transition_event_id in event_ids:
                raise PaperPositionStoreError(
                    PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
                    "S2 transition event ID is duplicated",
                )
            event_ids.add(envelope.transition_event_id)
            if isinstance(envelope.state_after, PositionStateS2V2):
                if envelope.state_after.trade_id in trade_ids:
                    raise PaperPositionStoreError(
                        PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
                        "S2 trade ID is duplicated in the transition journal",
                    )
                trade_ids.add(envelope.state_after.trade_id)
            if previous is None:
                if envelope.previous_transition_event_id:
                    raise PaperPositionStoreError(
                        PaperPositionStoreReasonCode.JOURNAL_GAP,
                        "first S2 transition references a predecessor",
                    )
            else:
                if (
                    envelope.previous_transition_event_id
                    != previous.transition_event_id
                    or envelope.state_before != previous.state_after
                    or envelope.transition_timestamp_utc
                    < previous.transition_timestamp_utc
                    or envelope.transition_tick_id < previous.transition_tick_id
                ):
                    raise PaperPositionStoreError(
                        PaperPositionStoreReasonCode.JOURNAL_GAP,
                        "S2 transition state/event chain is broken",
                    )
            previous = envelope
        return entries

    @staticmethod
    def _next_recovery_index(
        current: PositionArtifactV2,
        entries: list[tuple[Path, PositionTransitionEnvelopeV1]],
    ) -> int | None:
        if not entries:
            return 0 if isinstance(current, PositionStateS2FlatV2) else None
        for index, (_, envelope) in enumerate(entries):
            if current == envelope.state_before:
                return index
            if current == envelope.state_after:
                return index + 1
        return None

    def commit_transition(
        self,
        *,
        transition_event_id: str,
        transition_timestamp_utc: str,
        transition_tick_id: int,
        state_after: PositionArtifactV2,
        simulate_interruption_after_journal: bool = False,
    ) -> PositionTransitionCommitResult:
        event_id = _non_empty_text(transition_event_id, "transition_event_id")
        timestamp = _canonical_utc_seconds(
            transition_timestamp_utc,
            "transition_timestamp_utc",
        )
        tick_id = _non_negative_integer(transition_tick_id, "transition_tick_id")
        if not isinstance(state_after, (PositionStateS2FlatV2, PositionStateS2V2)):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "state_after must be a complete S2 V2 FLAT or OPEN state",
            )
        self._ensure_identity(state_after)
        current = self.load_state()
        entries = self._journal_envelopes()

        duplicate = next(
            (
                (path, envelope)
                for path, envelope in entries
                if envelope.transition_event_id == event_id
            ),
            None,
        )
        if duplicate is not None:
            path, envelope = duplicate
            if (
                envelope.transition_timestamp_utc != timestamp
                or envelope.transition_tick_id != tick_id
                or envelope.state_after != state_after
            ):
                raise PaperPositionStoreError(
                    PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
                    "same S2 transition event contains different data",
                )
            if current == entries[-1][1].state_after:
                return PositionTransitionCommitResult(
                    state=current,
                    journal_path=path,
                    newly_committed=False,
                    already_committed=True,
                    recovered_incomplete_commit=False,
                )
            if current == envelope.state_before and envelope is entries[-1][1]:
                _atomic_write_json(self.state_path, envelope.state_after.to_record())
                return PositionTransitionCommitResult(
                    state=envelope.state_after,
                    journal_path=path,
                    newly_committed=False,
                    already_committed=False,
                    recovered_incomplete_commit=True,
                )
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.RECOVERY_REQUIRED,
                "S2 transition journal requires full recovery",
            )

        recovery_index = self._next_recovery_index(current, entries)
        if recovery_index is None or recovery_index != len(entries):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.RECOVERY_REQUIRED,
                "S2 snapshot is not at the transition journal head",
            )

        if entries and (
            timestamp < entries[-1][1].transition_timestamp_utc
            or tick_id < entries[-1][1].transition_tick_id
        ):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.TRANSITION_INVALID,
                "S2 transition time/tick must not regress",
            )
        if isinstance(state_after, PositionStateS2V2) and any(
            isinstance(envelope.state_after, PositionStateS2V2)
            and envelope.state_after.trade_id == state_after.trade_id
            for _, envelope in entries
        ):
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
                "S2 trade ID was already opened",
            )

        transition_type = (
            TRANSITION_OPEN
            if isinstance(state_after, PositionStateS2V2)
            else TRANSITION_CLOSE
        )
        envelope = PositionTransitionEnvelopeV1(
            schema_version=1,
            transition_sequence=len(entries) + 1,
            transition_event_id=event_id,
            previous_transition_event_id=(
                "" if not entries else entries[-1][1].transition_event_id
            ),
            transition_type=transition_type,
            transition_timestamp_utc=timestamp,
            transition_tick_id=tick_id,
            state_before=current,
            state_after=state_after,
        )
        journal_path = self._journal_path(
            envelope.transition_sequence,
            envelope.transition_event_id,
        )
        _atomic_write_json(journal_path, envelope.to_record())
        if simulate_interruption_after_journal:
            raise SimulatedPositionTransitionInterruption(
                "simulated interruption after durable S2 transition journal"
            )
        _atomic_write_json(self.state_path, state_after.to_record())
        return PositionTransitionCommitResult(
            state=state_after,
            journal_path=journal_path,
            newly_committed=True,
            already_committed=False,
            recovered_incomplete_commit=False,
        )

    def reconciliation_report(self) -> PositionReconciliationReport:
        try:
            current = self.load_state()
            entries = self._journal_envelopes()
            recovery_index = self._next_recovery_index(current, entries)
            if recovery_index is None:
                raise PaperPositionStoreError(
                    PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
                    "S2 snapshot is not part of its transition journal",
                )
            if recovery_index != len(entries):
                raise PaperPositionStoreError(
                    PaperPositionStoreReasonCode.RECOVERY_REQUIRED,
                    "S2 transition journal is ahead of its snapshot",
                )
        except (PaperArtifactError, PaperPositionStoreError) as exc:
            return PositionReconciliationReport(
                consistent=False,
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(getattr(exc, "reason_code", ArtifactReasonCode.ARTIFACT_INVALID),),
                journal_transition_count=0,
                current_position="UNKNOWN",
            )
        return PositionReconciliationReport(
            consistent=True,
            entry_allowed=True,
            exit_allowed=True,
            reason_codes=(),
            journal_transition_count=len(entries),
            current_position=current.position,
        )

    def recover(self) -> PositionRecoveryResult:
        current = self.load_state()
        entries = self._journal_envelopes()
        recovery_index = self._next_recovery_index(current, entries)
        if recovery_index is None:
            raise PaperPositionStoreError(
                PaperPositionStoreReasonCode.JOURNAL_CONFLICT,
                "S2 snapshot is not part of its transition journal",
            )
        recovered_count = len(entries) - recovery_index
        if recovered_count == 0:
            return PositionRecoveryResult(
                state=current,
                journal_count=len(entries),
                recovered_transition_count=0,
            )
        recovered_state = entries[-1][1].state_after
        _atomic_write_json(self.state_path, recovered_state.to_record())
        return PositionRecoveryResult(
            state=recovered_state,
            journal_count=len(entries),
            recovered_transition_count=recovered_count,
        )


__all__ = [
    "ARTIFACT_S2_TRANSITION",
    "PaperPositionStore",
    "PaperPositionStoreError",
    "PaperPositionStoreReasonCode",
    "PositionReconciliationReport",
    "PositionRecoveryResult",
    "PositionTransitionCommitResult",
    "PositionTransitionEnvelopeV1",
    "SimulatedPositionTransitionInterruption",
    "TRANSITION_CLOSE",
    "TRANSITION_OPEN",
]
