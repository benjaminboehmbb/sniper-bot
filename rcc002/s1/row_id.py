"""Versioned `source_row_id` canonicalization.

Data Pipeline §7.2: "`source_row_id` identifiziert die normalisierte Zeile
innerhalb des `source_snapshot_id` deterministisch. Seine Vorabbildung und
Kanonisierungsregel müssen versioniert sein." Data Validation §7.1:
"`source_row_id` muss deterministisch als UTF-8-String erzeugt werden. Eine
parallele typabhängige Darstellung als Integer ist unzulässig."

V2 is the mandatory profile for all new builds. Historical V1 identities are
read-only and are never silently rewritten.
"""

from __future__ import annotations

import re

SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID = "RCC002_S1_SOURCE_ROW_ID_V2"
SOURCE_ROW_ID_CANONICALIZATION_PROFILE_VERSION = "2.0.0"
LEGACY_SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID = (
    "RCC002_S1_SOURCE_ROW_ID_V1"
)

# Zero-padding width for the row-index component. Chosen generously (20
# digits comfortably exceeds any realistic single-source row count) so that
# lexicographic string ordering matches numeric ordering, which is useful
# for diagnostics; the specification does not require this property, but it
# does not forbid it either, and no canonical field name or type is
# affected by it (`source_row_id` remains an opaque UTF-8 string).
_SOURCE_FILE_ORDINAL_WIDTH = 8
_ROW_INDEX_WIDTH = 20
_SOURCE_SNAPSHOT_ID_PATTERN = re.compile(
    r"^source:sha256:[0-9a-f]{64}$"
)


class SourceRowIdError(ValueError):
    """Fail-closed Source Row ID V2 contract violation."""

    def __init__(self, reason_code: str, detail: str) -> None:
        self.reason_code = reason_code
        super().__init__(f"{reason_code}: {detail}")


def compute_source_row_id(
    source_snapshot_id: str,
    source_file_ordinal: int,
    original_record_index: int,
) -> str:
    """Deterministically derive `source_row_id` for one original source row.

    `original_record_index` MUST be the row's zero-based position in the
    *original, pre-sort* source file order (Data Validation §8.5: "die
    ursprüngliche Reihenfolge über `source_row_id` erhalten bleibt"), not
    its position after any deterministic S1 re-sort.
    """
    if not _SOURCE_SNAPSHOT_ID_PATTERN.fullmatch(source_snapshot_id):
        raise SourceRowIdError(
            "RCC_SOURCE_SNAPSHOT_ID_INVALID",
            "source_snapshot_id must match "
            "source:sha256:<lowercase digest>",
        )
    values = (
        ("source_file_ordinal", source_file_ordinal, _SOURCE_FILE_ORDINAL_WIDTH),
        ("original_record_index", original_record_index, _ROW_INDEX_WIDTH),
    )
    for name, value, width in values:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise SourceRowIdError(
                "RCC_SOURCE_ROW_ID_COMPONENT_INVALID",
                f"{name} must be a non-negative integer",
            )
        if value >= 10**width:
            raise SourceRowIdError(
                "RCC_SOURCE_ROW_ID_WIDTH_OVERFLOW",
                f"{name} exceeds its registered decimal width",
            )
    return (
        f"{SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID}:"
        f"{source_snapshot_id}:"
        f"{source_file_ordinal:0{_SOURCE_FILE_ORDINAL_WIDTH}d}:"
        f"{original_record_index:0{_ROW_INDEX_WIDTH}d}"
    )


def validate_source_row_id_coordinates(
    source_row_id: str,
    *,
    source_snapshot_id: str,
    source_file_ordinal: int,
    original_record_index: int,
) -> None:
    """Validate that a V2 row ID encodes the row's stored source coordinates.

    Historical V1 identities remain read-only compatible and are not
    reinterpreted under the V2 contract.
    """
    v2_prefix = f"{SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID}:"
    if not source_row_id.startswith(v2_prefix):
        return

    expected = compute_source_row_id(
        source_snapshot_id,
        source_file_ordinal,
        original_record_index,
    )
    if source_row_id == expected:
        return

    try:
        encoded_prefix, encoded_ordinal, encoded_index = (
            source_row_id.rsplit(":", 2)
        )
    except ValueError as exc:
        raise SourceRowIdError(
            "RCC_SOURCE_ROW_ID_COORDINATE_MISMATCH",
            "Source Row ID V2 is not canonically encoded",
        ) from exc

    if encoded_index != f"{original_record_index:0{_ROW_INDEX_WIDTH}d}":
        raise SourceRowIdError(
            "RCC_SOURCE_RECORD_INDEX_NOT_ORIGINAL",
            "Source Row ID V2 does not encode the stored original "
            "pre-sort record index",
        )
    if encoded_ordinal != (
        f"{source_file_ordinal:0{_SOURCE_FILE_ORDINAL_WIDTH}d}"
    ):
        raise SourceRowIdError(
            "RCC_SOURCE_FILE_ORDINAL_MISMATCH",
            "Source Row ID V2 does not encode the stored canonical "
            "source-file ordinal",
        )
    if encoded_prefix != f"{v2_prefix}{source_snapshot_id}":
        raise SourceRowIdError(
            "RCC_SOURCE_ROW_ID_COORDINATE_MISMATCH",
            "Source Row ID V2 does not encode the stored source snapshot",
        )
    raise SourceRowIdError(
        "RCC_SOURCE_ROW_ID_COORDINATE_MISMATCH",
        "Source Row ID V2 contradicts its stored source coordinates",
    )
