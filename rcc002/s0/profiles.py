"""Registered Binance Vision source-period and timestamp profiles.

This module implements the pure profile functions shared by the S0 structural
coverage scan and S1 row materialization. Unit selection depends exclusively
on the registered archive-period descriptor; raw timestamp magnitude is never
used to choose a branch.
"""

from __future__ import annotations

import dataclasses
import enum
import re
from datetime import datetime, timedelta, timezone


SOURCE_RETRIEVAL_PROFILE_ID = "RCC002_BINANCE_VISION_SPOT_KLINES_V1"
SOURCE_RETRIEVAL_PROFILE_VERSION = "1.0.0"
COLUMN_PROFILE_ID = "BINANCE_SPOT_KLINE_12_COLUMN_V1"
TIMESTAMP_UNIT_PROFILE_ID = "BINANCE_SPOT_TIMESTAMP_UNITS_V1"
TIMESTAMP_UNIT_PROFILE_VERSION = "1.0.0"

_BOUNDARY = datetime(2025, 1, 1, tzinfo=timezone.utc)
_DAILY_PATTERN = re.compile(
    r"^data/spot/daily/klines/"
    r"(?P<path_symbol>[A-Z0-9]+)/(?P<path_interval>1m)/"
    r"(?P<name_symbol>[A-Z0-9]+)-(?P<name_interval>1m)-"
    r"(?P<period>[0-9]{4}-[0-9]{2}-[0-9]{2})\.zip$"
)
_MONTHLY_PATTERN = re.compile(
    r"^data/spot/monthly/klines/"
    r"(?P<path_symbol>[A-Z0-9]+)/(?P<path_interval>1m)/"
    r"(?P<name_symbol>[A-Z0-9]+)-(?P<name_interval>1m)-"
    r"(?P<period>[0-9]{4}-[0-9]{2})\.zip$"
)


class SourceProfileError(ValueError):
    """Fail-closed registered-source-profile violation."""

    def __init__(self, reason_code: str, detail: str) -> None:
        self.reason_code = reason_code
        super().__init__(f"{reason_code}: {detail}")


class TimestampUnit(str, enum.Enum):
    MILLISECOND = "MILLISECOND"
    MICROSECOND = "MICROSECOND"


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise SourceProfileError(
            "RCC_SOURCE_ARCHIVE_PERIOD_INVALID",
            f"invalid canonical UTC timestamp {value!r}",
        ) from exc
    return parsed.replace(tzinfo=timezone.utc)


def _epoch_ms(value: datetime) -> int:
    return int(value.timestamp()) * 1000


@dataclasses.dataclass(frozen=True, slots=True)
class ArchivePeriod:
    archive_family: str
    period_token: str
    period_start_utc: str
    period_end_utc: str

    def __post_init__(self) -> None:
        if self.archive_family not in {"DAILY", "MONTHLY"}:
            raise SourceProfileError(
                "RCC_SOURCE_ARCHIVE_FAMILY_UNKNOWN",
                f"unsupported archive family {self.archive_family!r}",
            )
        start = _parse_utc(self.period_start_utc)
        end = _parse_utc(self.period_end_utc)
        if start >= end:
            raise SourceProfileError(
                "RCC_SOURCE_ARCHIVE_PERIOD_INVALID",
                "archive period start must be before end",
            )

    @property
    def start(self) -> datetime:
        return _parse_utc(self.period_start_utc)

    @property
    def end(self) -> datetime:
        return _parse_utc(self.period_end_utc)

    @property
    def start_ms(self) -> int:
        return _epoch_ms(self.start)

    @property
    def end_ms(self) -> int:
        return _epoch_ms(self.end)

    def as_preimage(self) -> dict[str, str]:
        return {
            "archive_family": self.archive_family,
            "period_token": self.period_token,
            "period_start_utc": self.period_start_utc,
            "period_end_utc": self.period_end_utc,
        }


def parse_archive_period(
    provider_relative_name: str,
) -> tuple[str, str, ArchivePeriod]:
    """Resolve symbol, interval, and period from a registered portable name."""
    if (
        not provider_relative_name
        or provider_relative_name.startswith("/")
        or "\\" in provider_relative_name
        or ".." in provider_relative_name.split("/")
    ):
        raise SourceProfileError(
            "RCC_SOURCE_PORTABLE_PATH_INVALID",
            f"unsafe provider-relative name {provider_relative_name!r}",
        )

    match = _DAILY_PATTERN.fullmatch(provider_relative_name)
    family = "DAILY"
    if match is None:
        match = _MONTHLY_PATTERN.fullmatch(provider_relative_name)
        family = "MONTHLY"
    if match is None:
        raise SourceProfileError(
            "RCC_SOURCE_ARCHIVE_NAME_MISMATCH",
            f"name is not registered by {SOURCE_RETRIEVAL_PROFILE_ID}",
        )

    values = match.groupdict()
    if (
        values["path_symbol"] != values["name_symbol"]
        or values["path_interval"] != values["name_interval"]
    ):
        raise SourceProfileError(
            "RCC_SOURCE_ARCHIVE_NAME_MISMATCH",
            "path and archive basename symbol/interval disagree",
        )
    symbol = values["path_symbol"]
    interval = values["path_interval"]
    if symbol != "BTCUSDT" or interval != "1m":
        raise SourceProfileError(
            "RCC_SOURCE_PROFILE_VALUE_UNREGISTERED",
            f"unregistered symbol/interval {symbol}/{interval}",
        )

    token = values["period"]
    try:
        if family == "DAILY":
            start = datetime.strptime(token, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            end = start + timedelta(days=1)
        else:
            start = datetime.strptime(token, "%Y-%m").replace(
                tzinfo=timezone.utc
            )
            if start.month == 12:
                end = start.replace(
                    year=start.year + 1,
                    month=1,
                )
            else:
                end = start.replace(month=start.month + 1)
    except ValueError as exc:
        raise SourceProfileError(
            "RCC_SOURCE_ARCHIVE_PERIOD_INVALID",
            f"invalid {family} period token {token!r}",
        ) from exc

    return (
        symbol,
        interval,
        ArchivePeriod(
            archive_family=family,
            period_token=token,
            period_start_utc=_format_utc(start),
            period_end_utc=_format_utc(end),
        ),
    )


def resolve_timestamp_unit(period: ArchivePeriod) -> TimestampUnit:
    """Select the registered unit branch from the period descriptor only."""
    if period.end <= _BOUNDARY:
        return TimestampUnit.MILLISECOND
    if period.start >= _BOUNDARY:
        return TimestampUnit.MICROSECOND
    raise SourceProfileError(
        "RCC_SOURCE_ARCHIVE_PERIOD_CROSSES_UNIT_BOUNDARY",
        "archive period crosses 2025-01-01T00:00:00Z",
    )


def normalize_timestamp_pair(
    raw_open_time: int,
    raw_close_time: int,
    timestamp_unit: TimestampUnit,
) -> tuple[int, int]:
    """Convert one registered Binance Spot 1m timestamp pair to UTC ms."""
    for name, value in (
        ("raw_open_time", raw_open_time),
        ("raw_close_time", raw_close_time),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise SourceProfileError(
                "RCC_SOURCE_TIMESTAMP_INVALID",
                f"{name} must be a non-negative integer",
            )

    if timestamp_unit is TimestampUnit.MICROSECOND:
        if raw_open_time % 1000 != 0:
            raise SourceProfileError(
                "RCC_SOURCE_TIMESTAMP_OPEN_REMAINDER",
                "microsecond open time must have remainder 0 modulo 1000",
            )
        if raw_close_time % 1000 != 999:
            raise SourceProfileError(
                "RCC_SOURCE_TIMESTAMP_CLOSE_REMAINDER",
                "microsecond close time must have remainder 999 modulo 1000",
            )
        open_time_ms = raw_open_time // 1000
        close_time_ms = raw_close_time // 1000
    elif timestamp_unit is TimestampUnit.MILLISECOND:
        open_time_ms = raw_open_time
        close_time_ms = raw_close_time
    else:
        raise SourceProfileError(
            "RCC_SOURCE_TIMESTAMP_UNIT_UNKNOWN",
            f"unsupported timestamp unit {timestamp_unit!r}",
        )

    if (
        open_time_ms % 60_000 != 0
        or close_time_ms != open_time_ms + 59_999
        or close_time_ms - open_time_ms != 59_999
    ):
        raise SourceProfileError(
            "RCC_SOURCE_TIMESTAMP_UNIT_MISMATCH",
            "timestamps contradict the selected registered 1m unit profile",
        )
    return open_time_ms, close_time_ms


def reconcile_timestamp_to_period(
    open_time_ms: int,
    close_time_ms: int,
    period: ArchivePeriod,
) -> None:
    if open_time_ms < period.start_ms or close_time_ms >= period.end_ms:
        raise SourceProfileError(
            "RCC_SOURCE_COVERAGE_OUTSIDE_PERIOD",
            "normalized timestamp pair falls outside registered archive period",
        )


__all__ = [
    "ArchivePeriod",
    "COLUMN_PROFILE_ID",
    "SOURCE_RETRIEVAL_PROFILE_ID",
    "SOURCE_RETRIEVAL_PROFILE_VERSION",
    "SourceProfileError",
    "TIMESTAMP_UNIT_PROFILE_ID",
    "TIMESTAMP_UNIT_PROFILE_VERSION",
    "TimestampUnit",
    "normalize_timestamp_pair",
    "parse_archive_period",
    "reconcile_timestamp_to_period",
    "resolve_timestamp_unit",
]
