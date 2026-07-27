"""S0 file-integrity checks.

Transcribed from RCC_002_DATA_VALIDATION_2026-07-23.md:
- §6.1 Zulässige Dateizustände (permitted file states);
- §6.2 Pflichtprüfungen (mandatory checks);
- §6.3 Spreadsheet-Grenzprüfung (spreadsheet boundary check).

Row-level parsing into canonical schema is explicitly S1's job, not S0's
(Data Pipeline §7.1: "Die Quellartefakte selbst besitzen kein zusätzlich
erfundenes RCC-Zeilenschema."). The row count used by the spreadsheet
boundary check below is a bare line count for truncation detection, not a
semantic parse, and is scoped accordingly.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import os
from pathlib import Path

from rcc002.reason_codes import REASON_CODE_SEVERITY, Severity

# Formats explicitly disallowed as canonical S0-to-S2 transformation formats
# (Data Validation §6.3, closing sentence): "XLSX, XLS und ODS sind als
# kanonische S0-bis-S2-Transformationsformate unzulässig."
DISALLOWED_TRANSFORMATION_EXTENSIONS: frozenset[str] = frozenset(
    {".xlsx", ".xls", ".ods"}
)

# Spreadsheet/tool row-limit boundaries (Data Validation §6.3). Values are
# data-row counts, excluding the header row.
SUSPECTED_ROW_LIMIT_TRUNCATION_BOUNDARIES: frozenset[int] = frozenset(
    {65_535, 1_048_575}
)

DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION = "DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION"


class SourceFileState(enum.Enum):
    """The seven permitted S0 artifact states (Data Validation §6.1).

    "Nur `VERIFIED` darf regulär in S1 eingehen." QUARANTINED is not assigned
    by any function in this module: quarantine is a build/artifact-level
    governance decision (Data Pipeline §5.8: quarantine "wirken auf das
    gesamte Artefakt oder den gesamten Build, nicht auf einzelne Zeilen"),
    not a mechanical outcome of a single file's integrity checks.
    """

    RECEIVED_UNVERIFIED = "RECEIVED_UNVERIFIED"
    VERIFIED = "VERIFIED"
    MISSING = "MISSING"
    CORRUPT = "CORRUPT"
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    QUARANTINED = "QUARANTINED"


class UnsupportedSourceFormatError(NotImplementedError):
    """Raised when a source file's format/archive cannot yet be opened.

    Data Validation §6.2 requires "Format oder Archiv kann geöffnet werden"
    to be checked, but the specification does not enumerate a closed list of
    supported source formats (`source_format` is a registered, open string
    field). Plain-text delimited files are supported directly; any other
    registered format must be added explicitly rather than guessed.
    """


@dataclasses.dataclass(frozen=True)
class IntegrityCheckResult:
    """Result of a single named mandatory check (Data Validation §6.2)."""

    name: str
    passed: bool
    detail: str = ""


@dataclasses.dataclass(frozen=True)
class TruncationFinding:
    """A Data Validation §6.3 spreadsheet-boundary truncation finding.

    `severity` is `"CRITICAL"` exactly when §6.3's own escalation condition
    holds (see check_spreadsheet_truncation_boundary); otherwise it is the
    registry's default (`"ERROR"`, per §16.3's Reason-Code-Severity-Register,
    `rcc002.reason_codes.REASON_CODE_SEVERITY`). Prior to DVSEV-001, this
    field was left as `None` in the non-escalated case because no default
    severity was registered anywhere in the certified text; §16.3 closed
    that gap, so the non-escalated default is now always populated.
    """

    reason_code: str
    data_row_count: int
    boundary: int
    severity: str  # "ERROR" (default) or "CRITICAL" (escalated, §6.3)


def check_exists(path: Path) -> IntegrityCheckResult:
    """§6.2: "Datei existiert"."""
    return IntegrityCheckResult("file_exists", path.exists())


def check_readable(path: Path) -> IntegrityCheckResult:
    """§6.2: "Datei ist regulär lesbar"."""
    if not path.exists():
        return IntegrityCheckResult("file_readable", False, "file does not exist")
    return IntegrityCheckResult("file_readable", os.access(path, os.R_OK))


def check_nonempty(path: Path) -> IntegrityCheckResult:
    """§6.2: "Größe ist größer als null"."""
    if not path.exists():
        return IntegrityCheckResult("file_nonempty", False, "file does not exist")
    return IntegrityCheckResult("file_nonempty", path.stat().st_size > 0)


def check_not_disallowed_format(path: Path) -> IntegrityCheckResult:
    """§6.3: XLSX/XLS/ODS are disallowed canonical S0-S2 transformation formats."""
    suffix = path.suffix.lower()
    disallowed = suffix in DISALLOWED_TRANSFORMATION_EXTENSIONS
    return IntegrityCheckResult(
        "format_not_disallowed",
        not disallowed,
        f"extension {suffix!r} is a disallowed transformation format"
        if disallowed
        else "",
    )


def open_source_text(path: Path, source_format: str) -> str:
    """§6.2: "Format oder Archiv kann geöffnet werden".

    Only plain UTF-8 text is currently supported. Any other registered
    `source_format` must raise explicitly rather than be guessed at, per
    UnsupportedSourceFormatError's own docstring.
    """
    if source_format != "csv":
        raise UnsupportedSourceFormatError(
            f"source_format {source_format!r} is not yet supported by this "
            f"module; only 'csv' (plain UTF-8 delimited text) is implemented"
        )
    return path.read_text(encoding="utf-8")


def check_header_present(path: Path, source_format: str) -> IntegrityCheckResult:
    """§6.2: "Header ist vorhanden und parsebar"."""
    try:
        text = open_source_text(path, source_format)
    except (OSError, UnsupportedSourceFormatError) as exc:
        return IntegrityCheckResult("header_present", False, str(exc))
    first_line = text.splitlines()[0] if text.splitlines() else ""
    return IntegrityCheckResult("header_present", bool(first_line.strip()))


def compute_source_byte_sha256(path: Path) -> str:
    """§6.2: "lokale SHA-256-Checksumme wurde berechnet".

    Hashes the unmodified source bytes exactly (Data Pipeline §7.1:
    "Quellbytes werden nicht modifiziert.").
    """
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_provider_checksum(
    local_sha256: str, provider_sha256: str | None
) -> IntegrityCheckResult:
    """§6.2: "angebotene Anbieterchecksumme stimmt, sofern verfügbar".

    Passes vacuously if the provider did not offer a checksum.
    """
    if provider_sha256 is None:
        return IntegrityCheckResult(
            "provider_checksum_match", True, "no provider checksum offered"
        )
    return IntegrityCheckResult(
        "provider_checksum_match", local_sha256 == provider_sha256
    )


def count_data_rows(path: Path, source_format: str) -> int:
    """Bare line count (excluding header), for truncation detection only.

    This is a structural file-integrity metric, not row-level semantic
    parsing (which is S1's responsibility per Data Pipeline §7.1/§7.2).
    """
    text = open_source_text(path, source_format)
    lines = text.splitlines()
    return max(len(lines) - 1, 0) if lines else 0


def check_spreadsheet_truncation_boundary(
    data_row_count: int, *, upstream_has_more_rows_or_longer_range: bool = False
) -> TruncationFinding | None:
    """§6.3: Spreadsheet-Grenzprüfung.

    Returns None if `data_row_count` does not match a known suspicious
    boundary. `upstream_has_more_rows_or_longer_range` corresponds exactly to
    §6.3's own conditional: "Bei einer vorgelagerten Datei mit mehr Zeilen
    oder einem erwarteten längeren Zeitbereich ist dieser Befund `CRITICAL`."
    — the caller must supply this comparison; it is not computed here.
    """
    if data_row_count not in SUSPECTED_ROW_LIMIT_TRUNCATION_BOUNDARIES:
        return None
    severity = (
        Severity.CRITICAL.name
        if upstream_has_more_rows_or_longer_range
        else REASON_CODE_SEVERITY[DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION].name
    )
    return TruncationFinding(
        reason_code=DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION,
        data_row_count=data_row_count,
        boundary=data_row_count,
        severity=severity,
    )
