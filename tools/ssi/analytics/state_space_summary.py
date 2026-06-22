from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from tools.ssi.analytics.load_tsv import parse_float
from tools.ssi.analytics.state_key import build_state_key
from tools.ssi.common.scientific_object import ScientificObject


DIMENSION_COLUMNS = [
    "side",
    "progress",
    "compatibility",
    "stability",
    "confidence",
    "market_regime",
    "atr_quality",
    "ma200_signal",
    "mfi_signal",
]

NUMERIC_COLUMNS = [
    "current_score",
    "unrealized_pnl",
    "duration_sec",
    "progress_raw",
    "compatibility_raw",
    "stability_raw",
    "confidence_raw",
]


@dataclass(frozen=True, slots=True)
class StateFrequency(ScientificObject):
    state_id: str
    count: int
    share: float


@dataclass(frozen=True, slots=True)
class DimensionFrequency(ScientificObject):
    dimension: str
    value: str
    count: int
    share: float


@dataclass(frozen=True, slots=True)
class SideSummary(ScientificObject):
    side: str
    count: int
    share: float
    avg_unrealized_pnl: float


@dataclass(frozen=True, slots=True)
class NumericSummary(ScientificObject):
    column: str
    count: int
    min_value: float
    max_value: float
    mean_value: float


@dataclass(frozen=True, slots=True)
class StateSpaceSummary(ScientificObject):
    row_count: int
    unique_state_count: int
    state_frequencies: list[StateFrequency]
    dimension_frequencies: list[DimensionFrequency]
    side_summary: list[SideSummary]
    numeric_summary: list[NumericSummary]


def _safe_value(value: str | None) -> str:
    if value is None:
        return "UNKNOWN"

    text = str(value).strip()
    if text == "":
        return "UNKNOWN"

    return text


def summarize_state_space(
    rows: list[dict[str, str]],
    header: list[str],
) -> StateSpaceSummary:
    if not rows:
        raise ValueError("Cannot summarize empty TSV rows")

    total = len(rows)

    state_counter: Counter[str] = Counter()
    dimension_counters: dict[str, Counter[str]] = {
        col: Counter() for col in DIMENSION_COLUMNS if col in header
    }

    side_counter: Counter[str] = Counter()
    side_pnl_values: dict[str, list[float]] = defaultdict(list)

    numeric_values: dict[str, list[float]] = {
        col: [] for col in NUMERIC_COLUMNS if col in header
    }

    for row in rows:
        state_id = build_state_key(row).deterministic_id()
        state_counter[state_id] += 1

        for col, counter in dimension_counters.items():
            counter[_safe_value(row.get(col))] += 1

        side = _safe_value(row.get("side"))
        side_counter[side] += 1

        pnl = parse_float(row.get("unrealized_pnl"))
        if pnl is not None:
            side_pnl_values[side].append(pnl)

        for col, values in numeric_values.items():
            parsed = parse_float(row.get(col))
            if parsed is not None:
                values.append(parsed)

    state_frequencies = [
        StateFrequency(
            state_id=state_id,
            count=count,
            share=count / total,
        )
        for state_id, count in state_counter.most_common()
    ]

    dimension_frequencies: list[DimensionFrequency] = []
    for dimension, counter in dimension_counters.items():
        for value, count in counter.most_common():
            dimension_frequencies.append(
                DimensionFrequency(
                    dimension=dimension,
                    value=value,
                    count=count,
                    share=count / total,
                )
            )

    side_summary = []
    for side, count in side_counter.most_common():
        pnl_values = side_pnl_values.get(side, [])
        avg_pnl = sum(pnl_values) / len(pnl_values) if pnl_values else 0.0
        side_summary.append(
            SideSummary(
                side=side,
                count=count,
                share=count / total,
                avg_unrealized_pnl=avg_pnl,
            )
        )

    numeric_summary = []
    for column, values in numeric_values.items():
        if not values:
            continue

        sorted_values = sorted(values)
        count = len(sorted_values)

        numeric_summary.append(
            NumericSummary(
                column=column,
                count=count,
                min_value=sorted_values[0],
                max_value=sorted_values[-1],
                mean_value=sum(sorted_values) / count,
            )
        )

    return StateSpaceSummary(
        row_count=total,
        unique_state_count=len(state_counter),
        state_frequencies=state_frequencies,
        dimension_frequencies=dimension_frequencies,
        side_summary=side_summary,
        numeric_summary=numeric_summary,
    )