"""Deterministic Binance Vision archive scan and Source Snapshot V1 identity."""

from __future__ import annotations

import csv
import dataclasses
import hashlib
import io
import json
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Iterable
from zipfile import BadZipFile, ZipFile

from rcc002.s0.profiles import (
    COLUMN_PROFILE_ID,
    SOURCE_RETRIEVAL_PROFILE_ID,
    SOURCE_RETRIEVAL_PROFILE_VERSION,
    TIMESTAMP_UNIT_PROFILE_ID,
    ArchivePeriod,
    SourceProfileError,
    TimestampUnit,
    normalize_timestamp_pair,
    parse_archive_period,
    reconcile_timestamp_to_period,
    resolve_timestamp_unit,
)


SOURCE_SNAPSHOT_ID_PROFILE_ID = "RCC002_SOURCE_SNAPSHOT_ID_V1"
SOURCE_SNAPSHOT_ID_PROFILE_VERSION = "1.0.0"
SOURCE_ROW_ID_PROFILE_ID = "RCC002_S1_SOURCE_ROW_ID_V2"
SOURCE_ROW_ID_PROFILE_VERSION = "2.0.0"
PROVIDER = "BINANCE_VISION"
MARKET_TYPE = "spot"
DATASET_KIND = "klines"
EXPECTED_COLUMN_COUNT = 12


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonicalize_strings(value: object) -> object:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_canonicalize_strings(item) for item in value]
    if isinstance(value, dict):
        return {
            unicodedata.normalize("NFC", key): _canonicalize_strings(item)
            for key, item in value.items()
        }
    if value is None or isinstance(value, (bool, int)):
        return value
    raise TypeError(
        "Source Snapshot V1 preimages permit only objects, arrays, strings, "
        "integers, Booleans, and null"
    )


def canonical_json_bytes(value: object) -> bytes:
    """RCC JSON canonicalization for the Source Snapshot V1 value domain."""
    normalized = _canonicalize_strings(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


@dataclasses.dataclass(frozen=True, slots=True)
class SourceFileIdentity:
    provider_relative_name: str
    byte_sha256: str
    provider_checksum_sha256: str
    size_bytes: int
    csv_member_name: str
    source_file_ordinal: int
    archive_period: ArchivePeriod
    record_count: int
    min_open_time_utc_ms: int
    max_close_time_utc_ms: int
    timestamp_unit: TimestampUnit

    def as_preimage(self) -> dict[str, object]:
        return {
            "provider_relative_name": self.provider_relative_name,
            "byte_sha256": self.byte_sha256,
            "provider_checksum_sha256": self.provider_checksum_sha256,
            "size_bytes": self.size_bytes,
            "csv_member_name": self.csv_member_name,
            "source_file_ordinal": self.source_file_ordinal,
            "archive_period": self.archive_period.as_preimage(),
            "record_count": self.record_count,
            "min_open_time_utc_ms": self.min_open_time_utc_ms,
            "max_close_time_utc_ms": self.max_close_time_utc_ms,
            "timestamp_unit": self.timestamp_unit.value,
        }


@dataclasses.dataclass(frozen=True, slots=True)
class SourceSnapshot:
    source_snapshot_id: str
    preimage_sha256: str
    symbol: str
    interval: str
    source_revision: str | None
    source_files: tuple[SourceFileIdentity, ...]
    actual_coverage_min_open_time_utc_ms: int
    actual_coverage_max_close_time_utc_ms: int
    source_record_count: int

    def preimage(self) -> dict[str, object]:
        return {
            "identity_profile_id": SOURCE_SNAPSHOT_ID_PROFILE_ID,
            "source_retrieval_profile_id": SOURCE_RETRIEVAL_PROFILE_ID,
            "source_retrieval_profile_version": (
                SOURCE_RETRIEVAL_PROFILE_VERSION
            ),
            "provider": PROVIDER,
            "market_type": MARKET_TYPE,
            "dataset_kind": DATASET_KIND,
            "symbol": self.symbol,
            "interval": self.interval,
            "column_profile_id": COLUMN_PROFILE_ID,
            "timestamp_unit_profile_id": TIMESTAMP_UNIT_PROFILE_ID,
            "source_revision": self.source_revision,
            "source_files": [item.as_preimage() for item in self.source_files],
            "actual_coverage": {
                "min_open_time_utc_ms": (
                    self.actual_coverage_min_open_time_utc_ms
                ),
                "max_close_time_utc_ms": (
                    self.actual_coverage_max_close_time_utc_ms
                ),
                "record_count": self.source_record_count,
            },
        }


def _safe_member_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not path.is_absolute()
        and ".." not in path.parts
        and "\\" not in name
    )


def _parse_raw_integer(raw: str, field_name: str) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        reason = (
            "RCC_SOURCE_HEADER_MODE_MISMATCH"
            if any(character.isalpha() for character in raw)
            else "RCC_SOURCE_TIMESTAMP_INVALID"
        )
        raise SourceProfileError(
            reason,
            f"{field_name} is not a registered integer timestamp",
        ) from exc


def scan_binance_vision_archive(
    archive_path: Path,
    *,
    provider_relative_name: str,
    provider_checksum_sha256: str,
) -> SourceFileIdentity:
    """Inspect every non-empty registered CSV record without emitting S1 rows."""
    symbol, interval, period = parse_archive_period(provider_relative_name)
    del symbol, interval
    timestamp_unit = resolve_timestamp_unit(period)

    archive_bytes = archive_path.read_bytes()
    archive_sha256 = _digest(archive_bytes)
    if (
        not isinstance(provider_checksum_sha256, str)
        or len(provider_checksum_sha256) != 64
        or any(
            character not in "0123456789abcdef"
            for character in provider_checksum_sha256
        )
    ):
        raise SourceProfileError(
            "RCC_SOURCE_PROVIDER_CHECKSUM_INVALID",
            "provider checksum must be 64-character lowercase hex",
        )
    if archive_sha256 != provider_checksum_sha256:
        raise SourceProfileError(
            "RCC_SOURCE_PROVIDER_CHECKSUM_MISMATCH",
            "provider and computed archive SHA-256 values disagree",
        )

    try:
        with ZipFile(io.BytesIO(archive_bytes)) as archive:
            if archive.testzip() is not None:
                raise SourceProfileError(
                    "RCC_SOURCE_ARCHIVE_CORRUPT",
                    "ZIP integrity verification failed",
                )
            members = [
                item
                for item in archive.infolist()
                if not item.is_dir()
            ]
            if len(members) != 1 or not members[0].filename.endswith(".csv"):
                raise SourceProfileError(
                    "RCC_SOURCE_ZIP_MEMBER_COUNT_MISMATCH",
                    "registered archive must contain exactly one CSV member",
                )
            member = members[0]
            if not _safe_member_name(member.filename):
                raise SourceProfileError(
                    "RCC_SOURCE_PORTABLE_PATH_INVALID",
                    f"unsafe CSV member name {member.filename!r}",
                )
            expected_member_name = PurePosixPath(
                provider_relative_name
            ).name.removesuffix(".zip") + ".csv"
            if member.filename != expected_member_name:
                raise SourceProfileError(
                    "RCC_SOURCE_ZIP_MEMBER_NAME_MISMATCH",
                    f"expected member {expected_member_name!r}",
                )
            raw_csv = archive.read(member)
    except BadZipFile as exc:
        raise SourceProfileError(
            "RCC_SOURCE_ARCHIVE_CORRUPT",
            "source archive is not a readable ZIP",
        ) from exc

    try:
        text = raw_csv.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SourceProfileError(
            "RCC_SOURCE_ENCODING_MISMATCH",
            "CSV member is not UTF-8",
        ) from exc
    if text.startswith("\ufeff"):
        raise SourceProfileError(
            "RCC_SOURCE_ENCODING_MISMATCH",
            "UTF-8 BOM is prohibited",
        )
    if "\r" in text:
        raise SourceProfileError(
            "RCC_SOURCE_LINE_ENDING_MISMATCH",
            "registered CSV member must use LF line endings",
        )

    record_count = 0
    min_open_time: int | None = None
    max_close_time: int | None = None
    reader = csv.reader(io.StringIO(text, newline=""))
    for original_record_index, record in enumerate(reader):
        if len(record) != EXPECTED_COLUMN_COUNT:
            raise SourceProfileError(
                "RCC_SOURCE_COLUMN_COUNT_MISMATCH",
                f"record {original_record_index} has {len(record)} columns",
            )
        raw_open = _parse_raw_integer(record[0], "open_time_raw")
        raw_close = _parse_raw_integer(record[6], "close_time_raw")
        open_time_ms, close_time_ms = normalize_timestamp_pair(
            raw_open,
            raw_close,
            timestamp_unit,
        )
        reconcile_timestamp_to_period(open_time_ms, close_time_ms, period)
        min_open_time = (
            open_time_ms
            if min_open_time is None
            else min(min_open_time, open_time_ms)
        )
        max_close_time = (
            close_time_ms
            if max_close_time is None
            else max(max_close_time, close_time_ms)
        )
        record_count += 1

    if record_count == 0 or min_open_time is None or max_close_time is None:
        raise SourceProfileError(
            "RCC_SOURCE_EMPTY",
            "registered source archive contains no data records",
        )

    return SourceFileIdentity(
        provider_relative_name=provider_relative_name,
        byte_sha256=archive_sha256,
        provider_checksum_sha256=provider_checksum_sha256,
        size_bytes=len(archive_bytes),
        csv_member_name=expected_member_name,
        source_file_ordinal=0,
        archive_period=period,
        record_count=record_count,
        min_open_time_utc_ms=min_open_time,
        max_close_time_utc_ms=max_close_time,
        timestamp_unit=timestamp_unit,
    )


def _validate_snapshot_files(
    files: tuple[SourceFileIdentity, ...],
) -> None:
    names: set[str] = set()
    periods: dict[tuple[str, str], str] = {}
    for expected_ordinal, item in enumerate(files):
        if not isinstance(item, SourceFileIdentity):
            raise SourceProfileError(
                "RCC_SOURCE_DESCRIPTOR_INVALID",
                "source_files may contain only SourceFileIdentity entries",
            )
        if item.source_file_ordinal != expected_ordinal:
            raise SourceProfileError(
                "RCC_SOURCE_FILE_ORDINAL_MISMATCH",
                "source-file ordinals must be zero-based and contiguous",
            )
        for name, digest in (
            ("byte_sha256", item.byte_sha256),
            ("provider_checksum_sha256", item.provider_checksum_sha256),
        ):
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(
                    character not in "0123456789abcdef"
                    for character in digest
                )
            ):
                raise SourceProfileError(
                    "RCC_SOURCE_DIGEST_INVALID",
                    f"{name} must be 64-character lowercase hex",
                )
        for name, value in (
            ("size_bytes", item.size_bytes),
            ("record_count", item.record_count),
            ("min_open_time_utc_ms", item.min_open_time_utc_ms),
            ("max_close_time_utc_ms", item.max_close_time_utc_ms),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise SourceProfileError(
                    "RCC_SOURCE_DESCRIPTOR_INVALID",
                    f"{name} must be an integer",
                )
        if item.size_bytes <= 0 or item.record_count <= 0:
            raise SourceProfileError(
                "RCC_SOURCE_DESCRIPTOR_INVALID",
                "source size and record count must be positive",
            )
        if item.min_open_time_utc_ms > item.max_close_time_utc_ms:
            raise SourceProfileError(
                "RCC_SOURCE_DESCRIPTOR_INVALID",
                "source coverage minimum exceeds maximum",
            )
        expected_member_name = PurePosixPath(
            item.provider_relative_name
        ).name.removesuffix(".zip") + ".csv"
        if (
            not _safe_member_name(item.csv_member_name)
            or item.csv_member_name != expected_member_name
        ):
            raise SourceProfileError(
                "RCC_SOURCE_ZIP_MEMBER_NAME_MISMATCH",
                "descriptor CSV member name is not registered",
            )
        if item.provider_relative_name in names:
            raise SourceProfileError(
                "RCC_SOURCE_DUPLICATE_NAME",
                f"duplicate source name {item.provider_relative_name!r}",
            )
        names.add(item.provider_relative_name)
        period_key = (
            item.archive_period.archive_family,
            item.archive_period.period_token,
        )
        prior_digest = periods.get(period_key)
        if prior_digest is not None and prior_digest != item.byte_sha256:
            raise SourceProfileError(
                "RCC_SOURCE_DUPLICATE_PERIOD_CONFLICT",
                f"logical period {period_key!r} has conflicting bytes",
            )
        periods[period_key] = item.byte_sha256
        if item.byte_sha256 != item.provider_checksum_sha256:
            raise SourceProfileError(
                "RCC_SOURCE_PROVIDER_CHECKSUM_MISMATCH",
                "source descriptor checksum and byte digest disagree",
            )

    by_coverage = sorted(
        files,
        key=lambda item: (
            item.min_open_time_utc_ms,
            item.max_close_time_utc_ms,
        ),
    )
    for previous, item in zip(by_coverage, by_coverage[1:]):
        if item.min_open_time_utc_ms <= previous.max_close_time_utc_ms:
            raise SourceProfileError(
                "RCC_SOURCE_COVERAGE_OVERLAP",
                "normalized per-file source coverage overlaps",
            )


def build_source_snapshot(
    source_files: Iterable[SourceFileIdentity],
    *,
    source_revision: str | None = None,
) -> SourceSnapshot:
    if source_revision is not None and (
        not isinstance(source_revision, str) or not source_revision
    ):
        raise SourceProfileError(
            "RCC_SOURCE_REVISION_INVALID",
            "source revision must be null or a non-empty string",
        )
    discovered = tuple(source_files)
    if not discovered:
        raise SourceProfileError(
            "RCC_SOURCE_EMPTY",
            "source snapshot requires at least one source archive",
        )
    sorted_files = tuple(
        dataclasses.replace(item, source_file_ordinal=index)
        for index, item in enumerate(
            sorted(discovered, key=lambda item: item.provider_relative_name)
        )
    )
    _validate_snapshot_files(sorted_files)

    parsed_names = [
        parse_archive_period(item.provider_relative_name)
        for item in sorted_files
    ]
    for item, (_, _, parsed_period) in zip(sorted_files, parsed_names):
        if item.archive_period != parsed_period:
            raise SourceProfileError(
                "RCC_SOURCE_ARCHIVE_PERIOD_MISMATCH",
                "descriptor period disagrees with registered portable name",
            )
        expected_unit = resolve_timestamp_unit(parsed_period)
        if item.timestamp_unit is not expected_unit:
            raise SourceProfileError(
                "RCC_SOURCE_TIMESTAMP_UNIT_MISMATCH",
                "descriptor unit disagrees with registered archive period",
            )
        reconcile_timestamp_to_period(
            item.min_open_time_utc_ms,
            item.max_close_time_utc_ms,
            parsed_period,
        )
    symbols = {item[0] for item in parsed_names}
    intervals = {item[1] for item in parsed_names}
    if len(symbols) != 1 or len(intervals) != 1:
        raise SourceProfileError(
            "RCC_SOURCE_PROFILE_VALUE_MISMATCH",
            "all source files must have one registered symbol and interval",
        )
    symbol = next(iter(symbols))
    interval = next(iter(intervals))
    min_open = min(item.min_open_time_utc_ms for item in sorted_files)
    max_close = max(item.max_close_time_utc_ms for item in sorted_files)
    count = sum(item.record_count for item in sorted_files)

    provisional = SourceSnapshot(
        source_snapshot_id="",
        preimage_sha256="",
        symbol=symbol,
        interval=interval,
        source_revision=source_revision,
        source_files=sorted_files,
        actual_coverage_min_open_time_utc_ms=min_open,
        actual_coverage_max_close_time_utc_ms=max_close,
        source_record_count=count,
    )
    digest = _digest(canonical_json_bytes(provisional.preimage()))
    return dataclasses.replace(
        provisional,
        source_snapshot_id=f"source:sha256:{digest}",
        preimage_sha256=digest,
    )


__all__ = [
    "DATASET_KIND",
    "MARKET_TYPE",
    "PROVIDER",
    "SOURCE_ROW_ID_PROFILE_ID",
    "SOURCE_ROW_ID_PROFILE_VERSION",
    "SOURCE_SNAPSHOT_ID_PROFILE_ID",
    "SOURCE_SNAPSHOT_ID_PROFILE_VERSION",
    "SourceFileIdentity",
    "SourceSnapshot",
    "build_source_snapshot",
    "canonical_json_bytes",
    "scan_binance_vision_archive",
]
