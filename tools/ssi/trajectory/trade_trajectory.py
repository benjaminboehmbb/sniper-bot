from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from tools.ssi.analytics.state_key import StateKey, build_state_key
from tools.ssi.common.scientific_object import ScientificObject


@dataclass(frozen=True, slots=True)
class TrajectoryState(ScientificObject):
    snapshot_id: str
    timestamp_utc: datetime
    state_key: StateKey
    tsv_id: str
    source_row_index: int
    unrealized_pnl: float
    duration_sec: float

    def deterministic_id(self) -> str:
        return self.snapshot_id


@dataclass(frozen=True, slots=True)
class TradeTrajectory(ScientificObject):
    trajectory_id: str
    runtime_trade_id: str
    side: str
    states: tuple[TrajectoryState, ...]
    first_timestamp_utc: datetime
    last_timestamp_utc: datetime
    duration_sec: float
    reconstruction_method: str
    reconstruction_confidence: float

    def deterministic_id(self) -> str:
        return self.trajectory_id

    def state_count(self) -> int:
        return len(self.states)

    def has_transitions(self) -> bool:
        return len(self.states) >= 2


def parse_tsv_datetime(value: str) -> datetime:
    return datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))


def _parse_float(value: str, field_name: str) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid float for {field_name}: {value}") from exc


def _parse_int(value: str, field_name: str) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid int for {field_name}: {value}") from exc


def trajectory_state_from_tsv_row(row: dict[str, str]) -> TrajectoryState:
    required = [
        "snapshot_id",
        "timestamp_utc",
        "tsv_id",
        "source_row_index",
        "unrealized_pnl",
        "duration_sec",
    ]

    missing = [field for field in required if field not in row]
    if missing:
        raise KeyError("Missing required TSV trajectory fields: " + ", ".join(missing))

    return TrajectoryState(
        snapshot_id=str(row["snapshot_id"]).strip(),
        timestamp_utc=parse_tsv_datetime(row["timestamp_utc"]),
        state_key=build_state_key(row),
        tsv_id=str(row["tsv_id"]).strip(),
        source_row_index=_parse_int(row["source_row_index"], "source_row_index"),
        unrealized_pnl=_parse_float(row["unrealized_pnl"], "unrealized_pnl"),
        duration_sec=_parse_float(row["duration_sec"], "duration_sec"),
    )


def build_trade_trajectory(
    runtime_trade_id: str,
    side: str,
    states: list[TrajectoryState],
    reconstruction_method: str,
    reconstruction_confidence: float,
) -> TradeTrajectory:
    if runtime_trade_id.strip() == "":
        raise ValueError("runtime_trade_id must not be empty")

    if not states:
        raise ValueError("TradeTrajectory requires at least one state")

    ordered_states = tuple(sorted(states, key=lambda item: item.timestamp_utc))

    first_timestamp = ordered_states[0].timestamp_utc
    last_timestamp = ordered_states[-1].timestamp_utc

    return TradeTrajectory(
        trajectory_id=runtime_trade_id,
        runtime_trade_id=runtime_trade_id,
        side=side.strip().upper(),
        states=ordered_states,
        first_timestamp_utc=first_timestamp,
        last_timestamp_utc=last_timestamp,
        duration_sec=(last_timestamp - first_timestamp).total_seconds(),
        reconstruction_method=reconstruction_method,
        reconstruction_confidence=reconstruction_confidence,
    )