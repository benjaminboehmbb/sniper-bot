"""S3 indicator computation orchestration.

Ties together segment formation, the pure formulas, and the `x_valid`/
`x_warmup_complete`/`x_reason_codes` derivation, per Indicator Specification
§20 (Gültigkeits- und Qualitätsfelder) and §21 (Datenlücken und
Segmentierung).

Scope notes (deliberate, disclosed — not silent gaps):

- Full serial (non-incremental) builds only. `rcc002.s3.state`'s snapshot
  contract is implemented, but §22.4's incremental-continuation safety-check
  flow is not wired in here; `IND_STATE_MISSING`, `IND_STATE_MISMATCH`,
  `IND_PROFILE_MISMATCH`, `IND_SCHEMA_MISMATCH` are registered but not
  reachable from this entry point yet.
- `IND_SYNTHETIC_INPUT_DISALLOWED`: not reachable. The optional synthetic
  continuity view (Data Validation §11.4) is not implemented anywhere in
  this codebase (see `rcc002.s2.validate`'s own scope notes), so no
  synthetic input can ever reach this function.
- `IND_WINDOW_CROSSES_MARKET_SEGMENT`/`IND_WINDOW_CROSSES_INDICATOR_SEGMENT`:
  not reachable by construction. Every formula in `rcc002.s3.formulas`
  operates only on one already-correctly-bounded segment's own local array;
  no window can ever see data from another segment.
- `quality_gate_pass=False` rows (§20.1): produce exactly the certified
  field values (`x=null`, `x_valid=false`, `x_warmup_complete=false`) and
  leave `x_reason_codes` empty unless a genuine indicator-specific reason
  code is independently triggered. §20.1 states these three field values
  unconditionally but names no reason code for this case, and `quality_
  gate_pass=false` does not necessarily imply an invalid indicator input —
  a row can fail the S2 gate solely for reasons unrelated to the
  mathematical validity of its OHLCV values (e.g. an unresolved source
  conflict, or another upstream governance/publication decision), so
  `IND_INPUT_INVALID` ("mindestens ein feldspezifischer Pflichtinput ist
  ungültig") is not automatically attached (reviewed 2026-07-27; previously
  attached unconditionally, corrected per explicit instruction).
"""

from __future__ import annotations

import dataclasses
import math
from typing import Callable

from rcc002.s2.schema import S2Row
from rcc002.s3.constants import (
    INDICATOR_FIELD_ALLOWLIST,
    INDICATOR_PROFILE_ID,
    INDICATOR_PROFILE_VERSION,
    INDICATOR_SCHEMA_ID,
    INDICATOR_SCHEMA_REF,
    INDICATOR_SCHEMA_VERSION,
)
from rcc002.s3.formulas import (
    Series,
    adx_suite,
    atr_wilder_14,
    bollinger_bands,
    cci_20,
    ema_close_50,
    macd,
    mfi_14,
    obv_series,
    roc_close_12_pct,
    rsi_wilder_14,
    sma_close_200,
    stochastic_k_14,
    true_range_series,
    typical_price_series,
)
from rcc002.s3.reason_codes import sort_indicator_reason_codes
from rcc002.s3.schema import IndicatorField, S3Row
from rcc002.s3.segment import split_into_indicator_segments

# §20.4 single-field range invariants.
_RANGE_CHECKS: dict[str, Callable[[float], bool]] = {
    "rsi_wilder_14": lambda v: 0 <= v <= 100,
    "stoch_k_14": lambda v: 0 <= v <= 100,
    "atr_wilder_14": lambda v: v >= 0,
    "mfi_14": lambda v: 0 <= v <= 100,
    "plus_di_14": lambda v: 0 <= v <= 100,
    "minus_di_14": lambda v: 0 <= v <= 100,
    "dx_14": lambda v: 0 <= v <= 100,
    "adx_wilder_14": lambda v: 0 <= v <= 100,
    "bb_width_20_2": lambda v: v >= 0,
}


@dataclasses.dataclass(frozen=True)
class S3Result:
    rows: tuple[S3Row, ...]


def _finalize_field(
    raw_value: float | None, special_flags: frozenset[str], range_ok: bool
) -> IndicatorField:
    if raw_value is None:
        return IndicatorField(None, False, False, ("IND_WARMUP_INCOMPLETE",))

    reason_codes: set[str] = set(special_flags)
    if not math.isfinite(raw_value):
        reason_codes.add("IND_NONFINITE_RESULT")
        return IndicatorField(None, False, True, tuple(sort_indicator_reason_codes(reason_codes)))
    if not range_ok:
        reason_codes.add("IND_RANGE_INVARIANT_FAILED")
        return IndicatorField(None, False, True, tuple(sort_indicator_reason_codes(reason_codes)))
    return IndicatorField(raw_value, True, True, tuple(sort_indicator_reason_codes(reason_codes)))


def _compute_segment_fields(
    local_close: list[float], local_high: list[float], local_low: list[float], local_volume: list[float]
) -> dict[str, tuple[Series, list[frozenset[str]]]]:
    sma200 = sma_close_200(local_close)
    ema50 = ema_close_50(local_close)
    rsi, rsi_flags = rsi_wilder_14(local_close)
    macd_line, macd_signal, macd_hist = macd(local_close)
    bb_mid, bb_upper, bb_lower, bb_width = bollinger_bands(local_close)
    stoch_k, stoch_flags = stochastic_k_14(local_high, local_low, local_close)
    tr = true_range_series(local_high, local_low, local_close)
    atr = atr_wilder_14(tr)
    roc = roc_close_12_pct(local_close)
    obv = obv_series(local_close, local_volume)
    tp = typical_price_series(local_high, local_low, local_close)
    cci, cci_flags = cci_20(tp)
    mfi = mfi_14(tp, local_volume)
    plus_di, minus_di, dx, adx, adx_flags = adx_suite(local_high, local_low, local_close)

    n = len(local_close)
    empty_flags = [frozenset() for _ in range(n)]

    return {
        "sma_close_200": (sma200, empty_flags),
        "ema_close_50": (ema50, empty_flags),
        "rsi_wilder_14": (rsi, rsi_flags),
        "macd_line_12_26": (macd_line, empty_flags),
        "macd_signal_line_12_26_9": (macd_signal, empty_flags),
        "macd_hist_12_26_9": (macd_hist, empty_flags),
        "bb_mid_20": (bb_mid, empty_flags),
        "bb_upper_20_2": (bb_upper, empty_flags),
        "bb_lower_20_2": (bb_lower, empty_flags),
        "bb_width_20_2": (bb_width, empty_flags),
        "stoch_k_14": (stoch_k, stoch_flags),
        "true_range": (tr, empty_flags),
        "atr_wilder_14": (atr, empty_flags),
        "roc_close_12_pct": (roc, empty_flags),
        "obv": (obv, empty_flags),
        "typical_price": (tp, empty_flags),
        "cci_20": (cci, cci_flags),
        "mfi_14": (mfi, empty_flags),
        "plus_di_14": (plus_di, adx_flags),
        "minus_di_14": (minus_di, adx_flags),
        "dx_14": (dx, empty_flags),
        "adx_wilder_14": (adx, empty_flags),
    }


def compute_indicators(s2_rows: list[S2Row]) -> S3Result:
    """Compute all 22 canonical S3 indicator fields for one already-sorted,
    single-series list of S2 rows. `S3_rows = len(s2_rows)` always holds
    (§4.5/§26.2): no row is ever added, removed, or reordered.
    """
    n = len(s2_rows)
    if n == 0:
        return S3Result(rows=())

    market_segment_ids = [r.market_segment_id for r in s2_rows]
    quality_gate_passes = [r.quality_gate_pass for r in s2_rows]
    open_times = [r.open_time for r in s2_rows]

    segments = split_into_indicator_segments(market_segment_ids, quality_gate_passes, open_times)

    indicator_values: dict[str, list[IndicatorField | None]] = {
        name: [None] * n for name in INDICATOR_FIELD_ALLOWLIST
    }
    segment_id_per_row: list[str] = [""] * n

    for segment in segments:
        idxs = segment.row_indices
        for i in idxs:
            segment_id_per_row[i] = segment.indicator_segment_id

        if not segment.quality_gate_pass:
            # §20.1: exactly these three field values, unconditionally. No
            # reason code is certified-mandated for this case (see module
            # docstring); `quality_gate_pass=false` does not necessarily mean
            # any indicator input is itself invalid.
            for name in INDICATOR_FIELD_ALLOWLIST:
                for i in idxs:
                    indicator_values[name][i] = IndicatorField(None, False, False, ())
            continue

        local_close = [s2_rows[i].close for i in idxs]
        local_high = [s2_rows[i].high for i in idxs]
        local_low = [s2_rows[i].low for i in idxs]
        local_volume = [s2_rows[i].volume for i in idxs]

        field_series = _compute_segment_fields(local_close, local_high, local_low, local_volume)

        for name, (series, flags) in field_series.items():
            range_check = _RANGE_CHECKS.get(name)
            for local_i, global_i in enumerate(idxs):
                raw_value = series[local_i]
                range_ok = True
                if raw_value is not None and range_check is not None and math.isfinite(raw_value):
                    range_ok = range_check(raw_value)
                indicator_values[name][global_i] = _finalize_field(raw_value, flags[local_i], range_ok)

        # Bollinger inter-field invariant (§20.4): bb_upper >= bb_mid >= bb_lower.
        for local_i, global_i in enumerate(idxs):
            mid_f = indicator_values["bb_mid_20"][global_i]
            upper_f = indicator_values["bb_upper_20_2"][global_i]
            lower_f = indicator_values["bb_lower_20_2"][global_i]
            if mid_f and upper_f and lower_f and mid_f.valid and upper_f.valid and lower_f.valid:
                if not (upper_f.value >= mid_f.value >= lower_f.value):  # type: ignore[operator]
                    codes = ("IND_RANGE_INVARIANT_FAILED",)
                    indicator_values["bb_mid_20"][global_i] = IndicatorField(None, False, True, codes)
                    indicator_values["bb_upper_20_2"][global_i] = IndicatorField(None, False, True, codes)
                    indicator_values["bb_lower_20_2"][global_i] = IndicatorField(None, False, True, codes)

    rows: list[S3Row] = []
    for i, s2row in enumerate(s2_rows):
        indicators = {name: indicator_values[name][i] for name in INDICATOR_FIELD_ALLOWLIST}
        rows.append(
            S3Row(
                source_snapshot_id=s2row.source_snapshot_id,
                source_row_id=s2row.source_row_id,
                source_file_ordinal=s2row.source_file_ordinal,
                original_record_index=s2row.original_record_index,
                provider=s2row.provider,
                market_type=s2row.market_type,
                symbol=s2row.symbol,
                interval=s2row.interval,
                open_time=s2row.open_time,
                close_time=s2row.close_time,
                open=s2row.open,
                high=s2row.high,
                low=s2row.low,
                close=s2row.close,
                volume=s2row.volume,
                market_segment_id=s2row.market_segment_id,
                quality_is_observed=s2row.quality_is_observed,
                quality_is_synthetic=s2row.quality_is_synthetic,
                quality_has_source_conflict=s2row.quality_has_source_conflict,
                quality_gap_before=s2row.quality_gap_before,
                quality_gap_after=s2row.quality_gap_after,
                quality_timestamp_valid=s2row.quality_timestamp_valid,
                quality_ohlc_valid=s2row.quality_ohlc_valid,
                quality_volume_valid=s2row.quality_volume_valid,
                quality_market_values_valid=s2row.quality_market_values_valid,
                quality_status=s2row.quality_status,
                quality_reason_codes=s2row.quality_reason_codes,
                quality_rule_version=s2row.quality_rule_version,
                quality_gate_pass=s2row.quality_gate_pass,
                indicator_profile_id=INDICATOR_PROFILE_ID,
                indicator_profile_version=INDICATOR_PROFILE_VERSION,
                indicator_schema_id=INDICATOR_SCHEMA_ID,
                indicator_schema_version=INDICATOR_SCHEMA_VERSION,
                indicator_schema_ref=INDICATOR_SCHEMA_REF,
                indicator_segment_id=segment_id_per_row[i],
                indicators=indicators,
            )
        )

    return S3Result(rows=tuple(rows))
