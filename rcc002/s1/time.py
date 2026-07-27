"""S1 time semantics.

Transcribed from RCC_002_DATA_VALIDATION_2026-07-23.md §8 (Zeitsemantik).

Interval-duration registry: the certified specification family only ever
concretely exercises `1m` (Data Validation §8.3: "Für BTCUSDT `1m` gilt").
Data Pipeline's own scope statement anticipates further intervals being
registered later ("und spätere weitere Assets/Zeitebenen"), so this registry
is intentionally minimal rather than guessing durations for intervals the
certified bundle never states.

Stage-ownership correction (2026-07-27, part of DVSEV-001 Step 4 grounding):
this module previously exposed `check_interval_alignment`, which raised
`IntervalAlignmentError` and was called from S1's `normalize_rows` to abort
normalization on a misaligned `open_time`. That was incorrect: Data Pipeline
§7.3 lists "Intervallausrichtung" as one of S2's checks, not S1's, and
DVSEV-001's §16.3 registers `DV_TIME_MISALIGNED` as a row-level `CRITICAL`
reason code that must be able to reach S2 (a build-aborting S1 can never
produce a row for S2 to flag). Unlike an unparseable numeric/timestamp value
(for which no valid S1 row can be constructed at all under the certified,
non-nullable S1 schema — a genuine structural impossibility justifying
abort), a misaligned-but-parseable `open_time` is fully representable in
S1's schema. Per Data Pipeline §5.8 (Row Preservation), a deviation from row
preservation is permitted only via an explicitly normed build abort — no
certified text authorizes S1 to abort specifically for misalignment. This
module now exposes `is_interval_aligned` as a pure predicate for S2's use;
S1 no longer enforces or rejects on it.
"""

from __future__ import annotations

INTERVAL_DURATION_MS: dict[str, int] = {
    "1m": 60_000,
}

# Data Pipeline §7.2: "Für 1-Minuten-Bars gilt: close_time = open_time + 60
# Sekunden - 1 Millisekunde, sofern die Quellsemantik dieselbe geschlossene
# Kerzenkonvention verwendet." This formula is only specified for 1m; per
# Data Validation §8.3 ("eine abweichende Endzeitkonvention wird
# normalisiert, aber nicht geraten"), it must not be generalized by guessing.
_ONE_MINUTE_CLOSE_TIME_OFFSET_MS = 60_000 - 1


class UnregisteredIntervalError(NotImplementedError):
    """Raised for an interval with no registered duration.

    Per this module's own docstring: new intervals must be explicitly
    registered, not guessed.
    """


class UnknownCloseTimeConventionError(NotImplementedError):
    """Raised when close_time is not supplied and cannot be derived.

    Data Pipeline §7.2's closed-candle formula is only specified for `1m`.
    For any other interval, close_time must be supplied directly (already
    normalized from the documented provider semantics) rather than guessed.
    """


def require_interval_duration_ms(interval: str) -> int:
    """Look up the registered duration for `interval`, in milliseconds."""
    try:
        return INTERVAL_DURATION_MS[interval]
    except KeyError as exc:
        raise UnregisteredIntervalError(
            f"interval {interval!r} has no registered duration; only "
            f"{sorted(INTERVAL_DURATION_MS)} are registered"
        ) from exc


def is_interval_aligned(open_time_ms: int, interval: str) -> bool:
    """§8.3: "open_time % interval_duration == 0" — a pure predicate.

    Owned and enforced by S2 (`rcc002.s2`), not S1: this function has no
    side effect and never raises for a misaligned value; it only reports
    whether the value satisfies the rule, per Data Pipeline §7.3's
    assignment of "Intervallausrichtung" to S2.
    """
    duration_ms = require_interval_duration_ms(interval)
    return open_time_ms % duration_ms == 0


def resolve_close_time_ms(
    open_time_ms: int, interval: str, *, source_close_time_ms: int | None
) -> int:
    """Resolve close_time per Data Pipeline §7.2 / Data Validation §8.3.

    If the source already provides a close_time, it is normalized (passed
    through as-is; this module performs no unit/format conversion beyond
    accepting an already-canonical UTC-millisecond integer) rather than
    recomputed — per §8.3, a differing end-time convention is normalized,
    not guessed. If no source close_time is given, the closed-candle
    formula is applied, but only for the one interval it is specified for.
    """
    if source_close_time_ms is not None:
        return source_close_time_ms
    if interval == "1m":
        return open_time_ms + _ONE_MINUTE_CLOSE_TIME_OFFSET_MS
    raise UnknownCloseTimeConventionError(
        f"no close_time was supplied for interval {interval!r}, and Data "
        f"Pipeline §7.2's closed-candle formula is only specified for '1m'"
    )
