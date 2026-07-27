"""Pure S3 indicator formulas, operating on one gap-free, quality-homogeneous
`indicator_segment_id` sequence at a time (local index 0 = segment start),
per Indicator Specification §6 (Gemeinsame Hilfsdefinitionen) and §7-§18.

Every function returns a list the same length as its input, with `None`
at any local index where the value is not yet mathematically defined
(warm-up incomplete). No function looks beyond its own segment: callers
MUST pass only the values of one already-correctly-bounded segment, never
a cross-segment concatenation (§6.5).
"""

from __future__ import annotations

import math
from typing import Sequence

Series = list[float | None]


def sma_series(values: Sequence[float], n: int) -> Series:
    """§6.1. First valid at local index n-1."""
    result: Series = [None] * len(values)
    for t in range(n - 1, len(values)):
        result[t] = sum(values[t - n + 1 : t + 1]) / n
    return result


def ema_series(values: Sequence[float], n: int) -> Series:
    """§6.2. Seed EMA_n(n-1) = SMA_n(n-1); recursion for t >= n."""
    result: Series = [None] * len(values)
    if len(values) < n:
        return result
    alpha = 2.0 / (n + 1)
    seed = sum(values[0:n]) / n
    result[n - 1] = seed
    prev = seed
    for t in range(n, len(values)):
        prev = alpha * values[t] + (1 - alpha) * prev
        result[t] = prev
    return result


def wilder_average_series(values: Sequence[float], n: int, seed_end_index: int) -> Series:
    """§6.3. Seed = mean of the n values ending at `seed_end_index`
    (inclusive); recursion thereafter. `seed_end_index` is fixed by the
    caller per that indicator's own seed rule (RSI/MFI/ADX seed on a
    derived series that itself starts at local index 1, so their
    `seed_end_index` differs from ATR's, which starts at local index 0).
    """
    result: Series = [None] * len(values)
    start = seed_end_index - n + 1
    if start < 0 or seed_end_index >= len(values):
        return result
    seed = sum(values[start : seed_end_index + 1]) / n
    result[seed_end_index] = seed
    prev = seed
    for t in range(seed_end_index + 1, len(values)):
        prev = ((n - 1) * prev + values[t]) / n
        result[t] = prev
    return result


def wilder_sum_series(values: Sequence[float], n: int, seed_end_index: int) -> Series:
    """§6.4. Seed = sum of the n values ending at `seed_end_index`;
    recursion: prev - prev/n + current."""
    result: Series = [None] * len(values)
    start = seed_end_index - n + 1
    if start < 0 or seed_end_index >= len(values):
        return result
    seed = sum(values[start : seed_end_index + 1])
    result[seed_end_index] = seed
    prev = seed
    for t in range(seed_end_index + 1, len(values)):
        prev = prev - prev / n + values[t]
        result[t] = prev
    return result


# --- §7 SMA 200 -----------------------------------------------------------


def sma_close_200(close: Sequence[float]) -> Series:
    return sma_series(close, 200)


# --- §8 EMA 50 -------------------------------------------------------------


def ema_close_50(close: Sequence[float]) -> Series:
    return ema_series(close, 50)


# --- §9 RSI 14 (Wilder) ------------------------------------------------------


def rsi_wilder_14(close: Sequence[float]) -> tuple[Series, list[frozenset[str]]]:
    """§9. Returns (rsi_series, special_case_flags_per_index) — flags are
    always empty here (RSI has no §20.3 special case of its own)."""
    n = len(close)
    result: Series = [None] * n
    flags: list[frozenset[str]] = [frozenset() for _ in range(n)]
    if n < 2:
        return result, flags
    gain = [0.0] * n
    loss = [0.0] * n
    for t in range(1, n):
        delta = close[t] - close[t - 1]
        gain[t] = max(delta, 0.0)
        loss[t] = max(-delta, 0.0)
    # §9.2: seed uses deltas 1..14 -> local index 14 is the seed end.
    avg_gain = wilder_average_series(gain, 14, 14)
    avg_loss = wilder_average_series(loss, 14, 14)
    for t in range(14, n):
        ag = avg_gain[t]
        al = avg_loss[t]
        if ag is None or al is None:
            continue
        if ag > 0 and al > 0:
            rs = ag / al
            result[t] = 100 - 100 / (1 + rs)
        elif ag == 0 and al == 0:
            result[t] = 50.0
        elif ag > 0 and al == 0:
            result[t] = 100.0
        else:  # ag == 0 and al > 0
            result[t] = 0.0
    return result, flags


# --- §10 MACD 12/26/9 --------------------------------------------------------


def macd(close: Sequence[float]) -> tuple[Series, Series, Series]:
    """§10. Returns (macd_line, signal_line, histogram)."""
    n = len(close)
    ema_fast = ema_series(close, 12)
    ema_slow = ema_series(close, 26)
    macd_line: Series = [None] * n
    for t in range(n):
        if ema_fast[t] is not None and ema_slow[t] is not None:
            macd_line[t] = ema_fast[t] - ema_slow[t]  # type: ignore[operator]

    # §10.3: signal seed = mean(macd_line[25..33]) at local index 33.
    signal: Series = [None] * n
    if n > 33 and all(macd_line[i] is not None for i in range(25, 34)):
        seed = sum(macd_line[i] for i in range(25, 34)) / 9  # type: ignore[misc]
        signal[33] = seed
        alpha_signal = 2.0 / 10
        prev = seed
        for t in range(34, n):
            if macd_line[t] is None:
                break
            prev = alpha_signal * macd_line[t] + (1 - alpha_signal) * prev  # type: ignore[operator]
            signal[t] = prev

    hist: Series = [None] * n
    for t in range(n):
        if macd_line[t] is not None and signal[t] is not None:
            hist[t] = macd_line[t] - signal[t]  # type: ignore[operator]
    return macd_line, signal, hist


# --- §11 Bollinger Bands 20/2 -------------------------------------------------


def bollinger_bands(close: Sequence[float]) -> tuple[Series, Series, Series, Series]:
    """§11. Returns (mid, upper, lower, width). ddof=0 (population std)."""
    n = len(close)
    mid = sma_series(close, 20)
    upper: Series = [None] * n
    lower: Series = [None] * n
    width: Series = [None] * n
    for t in range(19, n):
        m = mid[t]
        if m is None:
            continue
        window = close[t - 19 : t + 1]
        variance = sum((c - m) ** 2 for c in window) / 20
        std_pop = math.sqrt(variance)
        upper[t] = m + 2 * std_pop
        lower[t] = m - 2 * std_pop
        if m > 0:
            width[t] = (upper[t] - lower[t]) / m  # type: ignore[operator]
    return mid, upper, lower, width


# --- §12 Stochastic %K 14 ----------------------------------------------------


def stochastic_k_14(
    high: Sequence[float], low: Sequence[float], close: Sequence[float]
) -> tuple[Series, list[frozenset[str]]]:
    """§12. Flat-window case: stoch_k=50, IND_STOCH_FLAT_WINDOW (INFO)."""
    n = len(close)
    result: Series = [None] * n
    flags: list[frozenset[str]] = [frozenset() for _ in range(n)]
    for t in range(13, n):
        window_high = max(high[t - 13 : t + 1])
        window_low = min(low[t - 13 : t + 1])
        if window_high > window_low:
            result[t] = 100 * (close[t] - window_low) / (window_high - window_low)
        else:
            result[t] = 50.0
            flags[t] = frozenset({"IND_STOCH_FLAT_WINDOW"})
    return result, flags


# --- §13 True Range / ATR 14 (Wilder) ----------------------------------------


def true_range_series(high: Sequence[float], low: Sequence[float], close: Sequence[float]) -> Series:
    """§13.1. First index of a gap-free sequence: H_0 - L_0 (no prior close)."""
    n = len(high)
    result: Series = [None] * n
    if n == 0:
        return result
    result[0] = high[0] - low[0]
    for t in range(1, n):
        result[t] = max(
            high[t] - low[t],
            abs(high[t] - close[t - 1]),
            abs(low[t] - close[t - 1]),
        )
    return result


def atr_wilder_14(true_range: Series) -> Series:
    """§13.2/§13.3. Seed at local index 13 = mean(true_range[0..13])."""
    values = [v if v is not None else 0.0 for v in true_range]  # true_range is always defined from index 0
    return wilder_average_series(values, 14, 13)


# --- §14 Rate of Change 12 ---------------------------------------------------


def roc_close_12_pct(close: Sequence[float]) -> Series:
    n = len(close)
    result: Series = [None] * n
    for t in range(12, n):
        result[t] = 100 * (close[t] / close[t - 12] - 1)
    return result


# --- §15 On-Balance Volume ----------------------------------------------------


def obv_series(close: Sequence[float], volume: Sequence[float]) -> Series:
    n = len(close)
    result: Series = [None] * n
    if n == 0:
        return result
    result[0] = 0.0
    for t in range(1, n):
        prev = result[t - 1]
        if close[t] > close[t - 1]:
            result[t] = prev + volume[t]  # type: ignore[operator]
        elif close[t] < close[t - 1]:
            result[t] = prev - volume[t]  # type: ignore[operator]
        else:
            result[t] = prev
    return result


# --- §16 Commodity Channel Index 20 -------------------------------------------


def typical_price_series(high: Sequence[float], low: Sequence[float], close: Sequence[float]) -> Series:
    return [(h + l + c) / 3 for h, l, c in zip(high, low, close)]


def cci_20(typical_price: Series) -> tuple[Series, list[frozenset[str]]]:
    """§16. Flat-MAD case: cci=0, IND_CCI_ZERO_MAD (INFO)."""
    n = len(typical_price)
    result: Series = [None] * n
    flags: list[frozenset[str]] = [frozenset() for _ in range(n)]
    for t in range(19, n):
        window = typical_price[t - 19 : t + 1]
        tp_sma = sum(window) / 20  # type: ignore[misc]
        tp_mad = sum(abs(v - tp_sma) for v in window) / 20  # type: ignore[misc,operator]
        if tp_mad > 0:
            result[t] = (typical_price[t] - tp_sma) / (0.015 * tp_mad)  # type: ignore[operator]
        else:
            result[t] = 0.0
            flags[t] = frozenset({"IND_CCI_ZERO_MAD"})
    return result, flags


# --- §17 Money Flow Index 14 ---------------------------------------------------


def mfi_14(
    typical_price: Series, volume: Sequence[float]
) -> Series:
    n = len(typical_price)
    result: Series = [None] * n
    if n == 0:
        return result
    positive_flow = [0.0] * n
    negative_flow = [0.0] * n
    for t in range(1, n):
        raw_mf = typical_price[t] * volume[t]  # type: ignore[operator]
        if typical_price[t] > typical_price[t - 1]:  # type: ignore[operator]
            positive_flow[t] = raw_mf
        elif typical_price[t] < typical_price[t - 1]:  # type: ignore[operator]
            negative_flow[t] = raw_mf
    for t in range(14, n):
        positive_sum = sum(positive_flow[t - 13 : t + 1])
        negative_sum = sum(negative_flow[t - 13 : t + 1])
        if positive_sum > 0 and negative_sum > 0:
            ratio = positive_sum / negative_sum
            result[t] = 100 - 100 / (1 + ratio)
        elif positive_sum == 0 and negative_sum == 0:
            result[t] = 50.0
        elif positive_sum > 0 and negative_sum == 0:
            result[t] = 100.0
        else:
            result[t] = 0.0
    return result


# --- §18 Average Directional Index 14 (Wilder) ---------------------------------


def adx_suite(
    high: Sequence[float], low: Sequence[float], close: Sequence[float]
) -> tuple[Series, Series, Series, Series, list[frozenset[str]]]:
    """§18. Returns (plus_di, minus_di, dx, adx, flags). Zero-TR case:
    plus_di=minus_di=0, IND_ADX_ZERO_TR (INFO); dx and adx follow their own
    rules from the resulting 0/0 inputs (§18.5: dx=0 when the DI sum is 0)."""
    n = len(high)
    plus_di: Series = [None] * n
    minus_di: Series = [None] * n
    dx: Series = [None] * n
    adx: Series = [None] * n
    flags: list[frozenset[str]] = [frozenset() for _ in range(n)]

    if n < 2:
        return plus_di, minus_di, dx, adx, flags

    tr = [0.0] * n
    plus_dm = [0.0] * n
    minus_dm = [0.0] * n
    for t in range(1, n):
        tr[t] = max(high[t] - low[t], abs(high[t] - close[t - 1]), abs(low[t] - close[t - 1]))
        up_move = high[t] - high[t - 1]
        down_move = low[t - 1] - low[t]
        if up_move > down_move and up_move > 0:
            plus_dm[t] = up_move
        elif down_move > up_move and down_move > 0:
            minus_dm[t] = down_move

    if n <= 14:
        return plus_di, minus_di, dx, adx, flags

    tr_sum = wilder_sum_series(tr, 14, 14)
    plus_dm_sum = wilder_sum_series(plus_dm, 14, 14)
    minus_dm_sum = wilder_sum_series(minus_dm, 14, 14)

    for t in range(14, n):
        trs = tr_sum[t]
        pds = plus_dm_sum[t]
        mds = minus_dm_sum[t]
        if trs is None or pds is None or mds is None:
            continue
        if trs > 0:
            plus_di[t] = 100 * pds / trs
            minus_di[t] = 100 * mds / trs
        else:
            plus_di[t] = 0.0
            minus_di[t] = 0.0
            flags[t] = frozenset({"IND_ADX_ZERO_TR"})
        pdi = plus_di[t]
        mdi = minus_di[t]
        di_sum = pdi + mdi  # type: ignore[operator]
        if di_sum > 0:
            dx[t] = 100 * abs(pdi - mdi) / di_sum  # type: ignore[operator]
        else:
            dx[t] = 0.0

    # §18.6: ADX seed = mean(dx[14..27]) at local index 27.
    if n > 27 and all(dx[i] is not None for i in range(14, 28)):
        seed = sum(dx[i] for i in range(14, 28)) / 14  # type: ignore[misc]
        adx[27] = seed
        prev = seed
        for t in range(28, n):
            if dx[t] is None:
                break
            prev = ((13 * prev) + dx[t]) / 14  # type: ignore[operator]
            adx[t] = prev

    return plus_di, minus_di, dx, adx, flags
