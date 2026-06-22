from __future__ import annotations

from dataclasses import dataclass

from tools.ssi.common.scientific_object import ScientificObject


REQUIRED_STATE_KEY_COLUMNS = [
    "side",
    "progress",
    "compatibility",
    "stability",
    "confidence",
]


@dataclass(frozen=True, slots=True)
class StateKey(ScientificObject):
    """
    Immutable scientific representation of a single TSV state.

    The StateKey represents semantic state meaning.
    Its deterministic_id is a stable textual identity for storage,
    grouping and later graph construction.
    """

    side: str
    progress: str
    compatibility: str
    stability: str
    confidence: str

    def deterministic_id(self) -> str:
        return "|".join(
            (
                self.side,
                self.progress,
                self.compatibility,
                self.stability,
                self.confidence,
            )
        )

    def state_id(self) -> str:
        return self.deterministic_id()


def _require(row: dict[str, str], column: str) -> str:
    if column not in row:
        raise KeyError(f"Missing required column: {column}")

    value = row[column]

    if value is None:
        return ""

    return str(value).strip()


def build_state_key(row: dict[str, str]) -> StateKey:
    """
    Construct a StateKey from a TSV row.

    No normalization is performed here.

    The Builder is the single source of truth for normalized values.
    """

    return StateKey(
        side=_require(row, "side"),
        progress=_require(row, "progress"),
        compatibility=_require(row, "compatibility"),
        stability=_require(row, "stability"),
        confidence=_require(row, "confidence"),
    )