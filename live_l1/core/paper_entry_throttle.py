#!/usr/bin/env python3
"""Pure, deterministic entry-rate and re-entry-cooldown contracts.

This module has no file, environment, local-clock, network, or runtime-state
access.  Candidate entry timestamps are explicit inputs so evaluation remains
identical during live processing, replay, and restart recovery.

The policy is deliberately separate from ``PaperEconomicsConfig`` schema V1.
It protects operational entry rate; it does not calculate execution economics.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


class EntryThrottleReasonCode:
    AUTHORIZED = "PEE_RATE_AUTHORIZED"
    CONFIG_INVALID = "PEE_RATE_CONFIG_INVALID"
    DAILY_ENTRY_LIMIT = "PEE_RATE_DAILY_ENTRY_LIMIT"
    ROLLING_ENTRY_LIMIT = "PEE_RATE_ROLLING_ENTRY_LIMIT"
    REENTRY_COOLDOWN = "PEE_RATE_REENTRY_COOLDOWN"
    POLICY_MISMATCH = "PEE_RATE_POLICY_MISMATCH"
    STATE_INVALID = "PEE_RATE_STATE_INVALID"


class PaperEntryThrottleError(ValueError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


def _canonical_json_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _text(
    value: object,
    field_name: str,
    *,
    reason_code: str,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str):
        raise PaperEntryThrottleError(reason_code, f"{field_name} must be a string")
    result = value.strip()
    if not allow_empty and not result:
        raise PaperEntryThrottleError(reason_code, f"{field_name} must not be empty")
    return result


def _integer(
    value: object,
    field_name: str,
    *,
    reason_code: str,
    minimum: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise PaperEntryThrottleError(
            reason_code,
            f"{field_name} must be an integer >= {minimum}",
        )
    return value


def _sha256_text(value: object, field_name: str) -> str:
    text = _text(
        value,
        field_name,
        reason_code=EntryThrottleReasonCode.STATE_INVALID,
    )
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"{field_name} must be a lowercase SHA-256 hex digest",
        )
    return text


def _utc_datetime(value: object, field_name: str) -> datetime:
    text = _text(
        value,
        field_name,
        reason_code=EntryThrottleReasonCode.STATE_INVALID,
    )
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    except ValueError as exc:
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"{field_name} must be an ISO-8601 timestamp",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"{field_name} must include a UTC offset",
        )
    return parsed.astimezone(timezone.utc)


def canonical_utc_timestamp(value: object, field_name: str = "timestamp_utc") -> str:
    parsed = _utc_datetime(value, field_name)
    if parsed.microsecond:
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"{field_name} must use whole-second resolution",
        )
    return parsed.isoformat(timespec="seconds").replace("+00:00", "Z")


def _utc_day(value: object, field_name: str = "utc_day") -> str:
    text = _text(
        value,
        field_name,
        reason_code=EntryThrottleReasonCode.STATE_INVALID,
    )
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d")
    except ValueError as exc:
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"{field_name} must use YYYY-MM-DD",
        ) from exc
    if parsed.strftime("%Y-%m-%d") != text:
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"{field_name} must use YYYY-MM-DD",
        )
    return text


@dataclass(frozen=True)
class PaperEntryThrottlePolicy:
    schema_version: int
    policy_model_version: str
    policy_profile_id: str
    max_entries_per_utc_day: int
    max_entries_per_rolling_window: int
    rolling_window_seconds: int
    min_reentry_cooldown_seconds: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.CONFIG_INVALID,
                "PaperEntryThrottlePolicy requires schema_version 1",
            )
        for name in ("policy_model_version", "policy_profile_id"):
            object.__setattr__(
                self,
                name,
                _text(
                    getattr(self, name),
                    name,
                    reason_code=EntryThrottleReasonCode.CONFIG_INVALID,
                ),
            )
        for name in (
            "max_entries_per_utc_day",
            "max_entries_per_rolling_window",
            "rolling_window_seconds",
            "min_reentry_cooldown_seconds",
        ):
            object.__setattr__(
                self,
                name,
                _integer(
                    getattr(self, name),
                    name,
                    reason_code=EntryThrottleReasonCode.CONFIG_INVALID,
                    minimum=1,
                ),
            )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "policy_model_version": self.policy_model_version,
            "policy_profile_id": self.policy_profile_id,
            "max_entries_per_utc_day": self.max_entries_per_utc_day,
            "max_entries_per_rolling_window": self.max_entries_per_rolling_window,
            "rolling_window_seconds": self.rolling_window_seconds,
            "min_reentry_cooldown_seconds": self.min_reentry_cooldown_seconds,
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PaperEntryThrottlePolicy":
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})

    @property
    def policy_fingerprint(self) -> str:
        return _canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class AcceptedEntryEventV1:
    schema_version: int
    entry_sequence: int
    entry_event_id: str
    previous_entry_event_id: str
    entry_timestamp_utc: str
    policy_model_version: str
    policy_profile_id: str
    policy_fingerprint: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "AcceptedEntryEventV1 requires schema_version 1",
            )
        object.__setattr__(
            self,
            "entry_sequence",
            _integer(
                self.entry_sequence,
                "entry_sequence",
                reason_code=EntryThrottleReasonCode.STATE_INVALID,
                minimum=1,
            ),
        )
        for name in (
            "entry_event_id",
            "policy_model_version",
            "policy_profile_id",
        ):
            object.__setattr__(
                self,
                name,
                _text(
                    getattr(self, name),
                    name,
                    reason_code=EntryThrottleReasonCode.STATE_INVALID,
                ),
            )
        object.__setattr__(
            self,
            "policy_fingerprint",
            _sha256_text(self.policy_fingerprint, "policy_fingerprint"),
        )
        object.__setattr__(
            self,
            "previous_entry_event_id",
            _text(
                self.previous_entry_event_id,
                "previous_entry_event_id",
                reason_code=EntryThrottleReasonCode.STATE_INVALID,
                allow_empty=True,
            ),
        )
        object.__setattr__(
            self,
            "entry_timestamp_utc",
            canonical_utc_timestamp(self.entry_timestamp_utc, "entry_timestamp_utc"),
        )
        if self.entry_sequence == 1 and self.previous_entry_event_id:
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "first entry event must not reference a predecessor",
            )
        if self.entry_sequence > 1 and not self.previous_entry_event_id:
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "entry event after sequence 1 must reference its predecessor",
            )

    def to_record(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AcceptedEntryEventV1":
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})

    @property
    def event_fingerprint(self) -> str:
        return _canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class PaperEntryThrottleState:
    schema_version: int
    policy_model_version: str
    policy_profile_id: str
    policy_fingerprint: str
    utc_day: str
    entries_today: int
    total_accepted_entry_count: int
    recent_entry_events: tuple[AcceptedEntryEventV1, ...]
    last_entry_event_id: str
    last_entry_timestamp_utc: str
    last_update_event_id: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "PaperEntryThrottleState requires schema_version 1",
            )
        for name in ("policy_model_version", "policy_profile_id"):
            object.__setattr__(
                self,
                name,
                _text(
                    getattr(self, name),
                    name,
                    reason_code=EntryThrottleReasonCode.STATE_INVALID,
                ),
            )
        object.__setattr__(
            self,
            "policy_fingerprint",
            _sha256_text(self.policy_fingerprint, "policy_fingerprint"),
        )
        object.__setattr__(self, "utc_day", _utc_day(self.utc_day))
        for name in ("entries_today", "total_accepted_entry_count"):
            object.__setattr__(
                self,
                name,
                _integer(
                    getattr(self, name),
                    name,
                    reason_code=EntryThrottleReasonCode.STATE_INVALID,
                    minimum=0,
                ),
            )
        if self.entries_today > self.total_accepted_entry_count:
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "entries_today cannot exceed total_accepted_entry_count",
            )
        if not isinstance(self.recent_entry_events, tuple):
            object.__setattr__(self, "recent_entry_events", tuple(self.recent_entry_events))
        for name in ("last_entry_event_id", "last_entry_timestamp_utc", "last_update_event_id"):
            object.__setattr__(
                self,
                name,
                _text(
                    getattr(self, name),
                    name,
                    reason_code=EntryThrottleReasonCode.STATE_INVALID,
                    allow_empty=True,
                ),
            )

        if self.total_accepted_entry_count == 0:
            if self.recent_entry_events or any(
                (self.last_entry_event_id, self.last_entry_timestamp_utc, self.last_update_event_id)
            ):
                raise PaperEntryThrottleError(
                    EntryThrottleReasonCode.STATE_INVALID,
                    "empty throttle state cannot reference an entry event",
                )
            return

        if not self.recent_entry_events or not all(
            (self.last_entry_event_id, self.last_entry_timestamp_utc, self.last_update_event_id)
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "non-empty throttle state must reference its latest entry event",
            )
        object.__setattr__(
            self,
            "last_entry_timestamp_utc",
            canonical_utc_timestamp(self.last_entry_timestamp_utc, "last_entry_timestamp_utc"),
        )

        previous_sequence = 0
        previous_timestamp: datetime | None = None
        previous_event_id = ""
        event_ids: set[str] = set()
        for event in self.recent_entry_events:
            if not isinstance(event, AcceptedEntryEventV1):
                raise PaperEntryThrottleError(
                    EntryThrottleReasonCode.STATE_INVALID,
                    "recent_entry_events must contain AcceptedEntryEventV1 values",
                )
            timestamp = _utc_datetime(event.entry_timestamp_utc, "entry_timestamp_utc")
            if event.entry_sequence <= previous_sequence:
                raise PaperEntryThrottleError(
                    EntryThrottleReasonCode.STATE_INVALID,
                    "recent entry sequences must be strictly increasing",
                )
            if previous_sequence and event.entry_sequence != previous_sequence + 1:
                raise PaperEntryThrottleError(
                    EntryThrottleReasonCode.STATE_INVALID,
                    "recent entry sequences must be contiguous",
                )
            if previous_event_id and event.previous_entry_event_id != previous_event_id:
                raise PaperEntryThrottleError(
                    EntryThrottleReasonCode.STATE_INVALID,
                    "recent entry predecessor chain is broken",
                )
            if previous_timestamp is not None and timestamp < previous_timestamp:
                raise PaperEntryThrottleError(
                    EntryThrottleReasonCode.STATE_INVALID,
                    "recent entry timestamps must not move backwards",
                )
            if event.entry_event_id in event_ids:
                raise PaperEntryThrottleError(
                    EntryThrottleReasonCode.STATE_INVALID,
                    "recent entry event IDs must be unique",
                )
            if (
                event.policy_model_version != self.policy_model_version
                or event.policy_profile_id != self.policy_profile_id
                or event.policy_fingerprint != self.policy_fingerprint
            ):
                raise PaperEntryThrottleError(
                    EntryThrottleReasonCode.POLICY_MISMATCH,
                    "recent entry event policy does not match throttle state",
                )
            previous_sequence = event.entry_sequence
            previous_timestamp = timestamp
            previous_event_id = event.entry_event_id
            event_ids.add(event.entry_event_id)

        latest = self.recent_entry_events[-1]
        if (
            latest.entry_sequence != self.total_accepted_entry_count
            or latest.entry_event_id != self.last_entry_event_id
            or latest.entry_timestamp_utc != self.last_entry_timestamp_utc
            or self.last_update_event_id != self.last_entry_event_id
        ):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "latest entry event does not match throttle state head",
            )
        latest_timestamp = _utc_datetime(
            self.last_entry_timestamp_utc,
            "last_entry_timestamp_utc",
        )
        if latest_timestamp.date().isoformat() != self.utc_day:
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "throttle UTC day must match the latest entry event",
            )
        visible_entries_today = sum(
            1
            for event in self.recent_entry_events
            if _utc_datetime(event.entry_timestamp_utc, "entry_timestamp_utc")
            .date()
            .isoformat()
            == self.utc_day
        )
        if self.entries_today < visible_entries_today:
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "entries_today is lower than the retained events for the UTC day",
            )

    @classmethod
    def initial(
        cls,
        policy: PaperEntryThrottlePolicy,
        *,
        utc_day: str,
    ) -> "PaperEntryThrottleState":
        return cls(
            schema_version=1,
            policy_model_version=policy.policy_model_version,
            policy_profile_id=policy.policy_profile_id,
            policy_fingerprint=policy.policy_fingerprint,
            utc_day=utc_day,
            entries_today=0,
            total_accepted_entry_count=0,
            recent_entry_events=(),
            last_entry_event_id="",
            last_entry_timestamp_utc="",
            last_update_event_id="",
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "policy_model_version": self.policy_model_version,
            "policy_profile_id": self.policy_profile_id,
            "policy_fingerprint": self.policy_fingerprint,
            "utc_day": self.utc_day,
            "entries_today": self.entries_today,
            "total_accepted_entry_count": self.total_accepted_entry_count,
            "recent_entry_events": [event.to_record() for event in self.recent_entry_events],
            "last_entry_event_id": self.last_entry_event_id,
            "last_entry_timestamp_utc": self.last_entry_timestamp_utc,
            "last_update_event_id": self.last_update_event_id,
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PaperEntryThrottleState":
        events_raw = record.get("recent_entry_events")
        if not isinstance(events_raw, list):
            raise PaperEntryThrottleError(
                EntryThrottleReasonCode.STATE_INVALID,
                "recent_entry_events must be a list",
            )
        values = {name: record.get(name) for name in cls.__dataclass_fields__}
        values["recent_entry_events"] = tuple(
            AcceptedEntryEventV1.from_record(event)
            if isinstance(event, Mapping)
            else event
            for event in events_raw
        )
        return cls(**values)

    @property
    def state_fingerprint(self) -> str:
        return _canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class EntryThrottleDecision:
    entry_allowed: bool
    exit_allowed: bool
    reason_codes: tuple[str, ...]
    disable_until_utc: str | None
    entries_today: int
    entries_in_rolling_window: int


def _policy_matches(
    state: PaperEntryThrottleState,
    policy: PaperEntryThrottlePolicy,
) -> bool:
    return (
        state.policy_model_version == policy.policy_model_version
        and state.policy_profile_id == policy.policy_profile_id
        and state.policy_fingerprint == policy.policy_fingerprint
    )


def evaluate_entry_throttle(
    state: PaperEntryThrottleState,
    policy: PaperEntryThrottlePolicy,
    *,
    entry_timestamp_utc: str,
) -> EntryThrottleDecision:
    """Evaluate a candidate entry without mutating throttle state."""

    if not _policy_matches(state, policy):
        return EntryThrottleDecision(
            entry_allowed=False,
            exit_allowed=True,
            reason_codes=(EntryThrottleReasonCode.POLICY_MISMATCH,),
            disable_until_utc=None,
            entries_today=state.entries_today,
            entries_in_rolling_window=len(state.recent_entry_events),
        )

    try:
        candidate = _utc_datetime(entry_timestamp_utc, "entry_timestamp_utc")
    except PaperEntryThrottleError:
        return EntryThrottleDecision(
            entry_allowed=False,
            exit_allowed=True,
            reason_codes=(EntryThrottleReasonCode.STATE_INVALID,),
            disable_until_utc=None,
            entries_today=state.entries_today,
            entries_in_rolling_window=len(state.recent_entry_events),
        )

    candidate_day = candidate.date().isoformat()
    if candidate_day < state.utc_day:
        return EntryThrottleDecision(
            entry_allowed=False,
            exit_allowed=True,
            reason_codes=(EntryThrottleReasonCode.STATE_INVALID,),
            disable_until_utc=None,
            entries_today=state.entries_today,
            entries_in_rolling_window=len(state.recent_entry_events),
        )

    last_timestamp: datetime | None = None
    if state.last_entry_timestamp_utc:
        last_timestamp = _utc_datetime(
            state.last_entry_timestamp_utc,
            "last_entry_timestamp_utc",
        )
        if candidate < last_timestamp:
            return EntryThrottleDecision(
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(EntryThrottleReasonCode.STATE_INVALID,),
                disable_until_utc=None,
                entries_today=state.entries_today,
                entries_in_rolling_window=len(state.recent_entry_events),
            )

    entries_today = state.entries_today if candidate_day == state.utc_day else 0
    window_start = candidate - timedelta(seconds=policy.rolling_window_seconds)
    active_events = tuple(
        event
        for event in state.recent_entry_events
        if _utc_datetime(event.entry_timestamp_utc, "entry_timestamp_utc") > window_start
    )
    reasons: list[str] = []
    block_until: list[datetime] = []

    if entries_today >= policy.max_entries_per_utc_day:
        reasons.append(EntryThrottleReasonCode.DAILY_ENTRY_LIMIT)
        block_until.append(
            datetime.combine(
                candidate.date() + timedelta(days=1),
                datetime.min.time(),
                tzinfo=timezone.utc,
            )
        )

    if len(active_events) >= policy.max_entries_per_rolling_window:
        reasons.append(EntryThrottleReasonCode.ROLLING_ENTRY_LIMIT)
        earliest_active = _utc_datetime(
            active_events[0].entry_timestamp_utc,
            "entry_timestamp_utc",
        )
        block_until.append(
            earliest_active + timedelta(seconds=policy.rolling_window_seconds)
        )

    if last_timestamp is not None:
        cooldown_until = last_timestamp + timedelta(
            seconds=policy.min_reentry_cooldown_seconds
        )
        if candidate < cooldown_until:
            reasons.append(EntryThrottleReasonCode.REENTRY_COOLDOWN)
            block_until.append(cooldown_until)

    disable_until = max(block_until) if block_until else None
    return EntryThrottleDecision(
        entry_allowed=not reasons,
        exit_allowed=True,
        reason_codes=tuple(reasons),
        disable_until_utc=(
            canonical_utc_timestamp(disable_until.isoformat())
            if disable_until is not None
            else None
        ),
        entries_today=entries_today,
        entries_in_rolling_window=len(active_events),
    )


def apply_accepted_entry(
    state: PaperEntryThrottleState,
    policy: PaperEntryThrottlePolicy,
    event: AcceptedEntryEventV1,
) -> PaperEntryThrottleState:
    """Return the next state for one authorized, accepted entry event."""

    if (
        event.policy_model_version != policy.policy_model_version
        or event.policy_profile_id != policy.policy_profile_id
        or event.policy_fingerprint != policy.policy_fingerprint
        or not _policy_matches(state, policy)
    ):
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.POLICY_MISMATCH,
            "entry event, state, and policy identities must match",
        )
    expected_sequence = state.total_accepted_entry_count + 1
    if event.entry_sequence != expected_sequence:
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            f"expected entry sequence {expected_sequence}",
        )
    if event.previous_entry_event_id != state.last_entry_event_id:
        raise PaperEntryThrottleError(
            EntryThrottleReasonCode.STATE_INVALID,
            "entry event predecessor does not match throttle state head",
        )

    decision = evaluate_entry_throttle(
        state,
        policy,
        entry_timestamp_utc=event.entry_timestamp_utc,
    )
    if not decision.entry_allowed:
        raise PaperEntryThrottleError(
            decision.reason_codes[0],
            "accepted entry event is blocked by throttle policy",
        )

    timestamp = _utc_datetime(event.entry_timestamp_utc, "entry_timestamp_utc")
    window_start = timestamp - timedelta(seconds=policy.rolling_window_seconds)
    recent = tuple(
        previous
        for previous in state.recent_entry_events
        if _utc_datetime(previous.entry_timestamp_utc, "entry_timestamp_utc") > window_start
    ) + (event,)
    event_day = timestamp.date().isoformat()
    entries_today = state.entries_today + 1 if event_day == state.utc_day else 1

    return PaperEntryThrottleState(
        schema_version=1,
        policy_model_version=policy.policy_model_version,
        policy_profile_id=policy.policy_profile_id,
        policy_fingerprint=policy.policy_fingerprint,
        utc_day=event_day,
        entries_today=entries_today,
        total_accepted_entry_count=event.entry_sequence,
        recent_entry_events=recent,
        last_entry_event_id=event.entry_event_id,
        last_entry_timestamp_utc=event.entry_timestamp_utc,
        last_update_event_id=event.entry_event_id,
    )
