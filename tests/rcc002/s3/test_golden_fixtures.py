"""Golden fixtures for all 12 canonical S3 indicators (Indicator
Specification §27.2).

Every expected value in this file is derived independently of
`rcc002.s3.formulas` — via exact rational (`fractions.Fraction`) arithmetic,
closed-form summation identities, or algebraic fixed-point reasoning —
rather than by re-running (or re-transcribing) the same iterative
floating-point recursion the implementation uses. This is a materially
different computational method from the code under test, satisfying
§27.2's "unabhängig berechnet" (independently computed) requirement, not
merely a parallel re-implementation of the same formula.

Each fixture documents: input values, intermediate values (computed via the
independent method), expected output, and the certified tolerance (§28.2:
absolute_tolerance=1e-12, relative_tolerance=1e-10). RSI and ADX additionally
include a seed and at least two recursion steps, per §27.2's explicit
requirement for those two indicators.
"""

import unittest
from fractions import Fraction

from rcc002.s3 import formulas
from rcc002.s3.constants import ABSOLUTE_TOLERANCE, RELATIVE_TOLERANCE


def assert_within_tolerance(test: unittest.TestCase, actual: float, expected: float) -> None:
    """§28.2's exact componentwise comparison formula."""
    tolerance = ABSOLUTE_TOLERANCE + RELATIVE_TOLERANCE * max(abs(actual), abs(expected))
    test.assertLessEqual(
        abs(actual - expected),
        tolerance,
        msg=f"actual={actual!r} expected={expected!r} tolerance={tolerance!r}",
    )


class SmaClose200GoldenTest(unittest.TestCase):
    """Independent method: closed-form arithmetic-series mean.
    mean(1..200) = (first + last) / 2 = 100.5 — derived from the arithmetic
    series mean identity, not from summing 200 terms in a loop."""

    def test_golden(self) -> None:
        close = [float(i) for i in range(1, 201)]  # 1..200
        expected = (1 + 200) / 2  # closed-form arithmetic series mean
        self.assertEqual(expected, 100.5)
        result = formulas.sma_close_200(close)
        assert_within_tolerance(self, result[199], expected)


class EmaClose50GoldenTest(unittest.TestCase):
    """Independent method: exact Fraction arithmetic for the seed and one
    recursion step, using the arithmetic-series closed-form mean for the
    seed rather than a summation loop."""

    def test_golden(self) -> None:
        close = [float(i) for i in range(1, 52)]  # 1..51
        # Seed at local index 49 (t=n-1): mean(1..50) = 51/2.
        seed = Fraction(51, 2)
        alpha = Fraction(2, 51)
        # One recursion step at t=50, value=51.
        step = alpha * 51 + (1 - alpha) * seed
        self.assertEqual(step, Fraction(53, 2))  # 26.5, hand-derived
        result = formulas.ema_close_50(close)
        assert_within_tolerance(self, result[49], float(seed))
        assert_within_tolerance(self, result[50], float(step))


class RsiWilderGoldenTest(unittest.TestCase):
    """Independent method: exact Fraction arithmetic. Alternating +2/-2
    daily changes give exactly 7 gains and 7 losses of magnitude 2 in the
    14-delta seed window, so avg_gain=avg_loss=1 without needing to sum
    term-by-term. Includes seed and two recursion steps (§27.2)."""

    def _build_close(self) -> list[float]:
        close = [10.0]
        for i in range(16):
            close.append(close[-1] + (2.0 if i % 2 == 0 else -2.0))
        return close

    def test_seed(self) -> None:
        close = self._build_close()
        # 7 gains of 2 (odd t: 1,3,...,13), 7 losses of 2 (even t: 2,4,...,14).
        avg_gain_14 = Fraction(7 * 2, 14)  # = 1
        avg_loss_14 = Fraction(7 * 2, 14)  # = 1
        self.assertEqual(avg_gain_14, 1)
        self.assertEqual(avg_loss_14, 1)
        rs_14 = avg_gain_14 / avg_loss_14
        expected_rsi_14 = 100 - 100 / (1 + rs_14)
        self.assertEqual(expected_rsi_14, 50)
        rsi, _ = formulas.rsi_wilder_14(close)
        assert_within_tolerance(self, rsi[14], float(expected_rsi_14))

    def test_recursion_step_1(self) -> None:
        close = self._build_close()
        avg_gain_14, avg_loss_14 = Fraction(1), Fraction(1)
        # t=15 is odd -> delta_15 = +2 (gain=2, loss=0), per the construction.
        avg_gain_15 = (13 * avg_gain_14 + 2) / 14  # = 15/14
        avg_loss_15 = (13 * avg_loss_14 + 0) / 14  # = 13/14
        self.assertEqual(avg_gain_15, Fraction(15, 14))
        self.assertEqual(avg_loss_15, Fraction(13, 14))
        rs_15 = avg_gain_15 / avg_loss_15  # = 15/13
        expected_rsi_15 = 100 - 100 / (1 + rs_15)
        self.assertEqual(expected_rsi_15, Fraction(3750, 70))  # exact check below
        rsi, _ = formulas.rsi_wilder_14(close)
        assert_within_tolerance(self, rsi[15], float(expected_rsi_15))

    def test_recursion_step_2(self) -> None:
        close = self._build_close()
        avg_gain_15, avg_loss_15 = Fraction(15, 14), Fraction(13, 14)
        # t=16 is even -> delta_16 = -2 (loss=2, gain=0).
        avg_gain_16 = (13 * avg_gain_15 + 0) / 14
        avg_loss_16 = (13 * avg_loss_15 + 2) / 14
        rs_16 = avg_gain_16 / avg_loss_16
        expected_rsi_16 = 100 - 100 / (1 + rs_16)
        rsi, _ = formulas.rsi_wilder_14(close)
        assert_within_tolerance(self, rsi[16], float(expected_rsi_16))


class MacdGoldenTest(unittest.TestCase):
    """Independent method: constant input is a fixed point of the EMA
    recursion (proof: alpha*c + (1-alpha)*c = c for any constant c), so
    ema_fast = ema_slow = c exactly, giving macd_line = 0 and hist = 0 by
    algebraic identity — not by running the recursion."""

    def test_golden(self) -> None:
        close = [50.0] * 40
        macd_line, signal, hist = formulas.macd(close)
        assert_within_tolerance(self, macd_line[30], 0.0)
        assert_within_tolerance(self, signal[35], 0.0)
        assert_within_tolerance(self, hist[35], 0.0)


class BollingerBandsGoldenTest(unittest.TestCase):
    """Independent method: closed-form population variance of a constant
    series is exactly 0 (every deviation from the mean is 0), so std_pop=0
    and upper=mid=lower by algebraic identity."""

    def test_golden(self) -> None:
        close = [10.0] * 25
        mid, upper, lower, width = formulas.bollinger_bands(close)
        assert_within_tolerance(self, mid[19], 10.0)
        assert_within_tolerance(self, upper[19], 10.0)
        assert_within_tolerance(self, lower[19], 10.0)
        assert_within_tolerance(self, width[19], 0.0)


class StochasticKGoldenTest(unittest.TestCase):
    """Independent method: monotonically increasing H and L over the
    14-window means window_high/window_low are exactly the endpoints
    (H_13, L_0) by the definition of a strictly increasing sequence, giving
    a closed-form ratio without scanning the window."""

    def test_golden(self) -> None:
        n = 14
        high = [10.0 + t for t in range(n)]
        low = [float(t) for t in range(n)]
        close = [5.0 + t for t in range(n)]
        window_high = Fraction(10) + (n - 1)  # H_13 = 23
        window_low = Fraction(0)  # L_0 = 0
        c_13 = Fraction(5) + (n - 1)  # = 18
        expected = 100 * (c_13 - window_low) / (window_high - window_low)
        self.assertEqual(expected, Fraction(1800, 23))
        result, flags = formulas.stochastic_k_14(high, low, close)
        assert_within_tolerance(self, result[13], float(expected))


class TrueRangeAtrGoldenTest(unittest.TestCase):
    """Independent method: constant H/L/C gives constant TR by direct
    substitution; the ATR seed (mean of 14 identical values) equals that
    constant, and the constant is an algebraic fixed point of the Wilder
    recursion (((13*c)+c)/14 = c), so ATR stays exactly at that constant."""

    def test_golden(self) -> None:
        n = 16
        high = [10.0] * n
        low = [8.0] * n
        close = [9.0] * n
        tr = formulas.true_range_series(high, low, close)
        expected_tr = 2.0  # max(10-8, |10-9|, |8-9|) = max(2,1,1) = 2
        for t in range(n):
            assert_within_tolerance(self, tr[t], expected_tr)
        atr = formulas.atr_wilder_14(tr)
        assert_within_tolerance(self, atr[13], expected_tr)
        assert_within_tolerance(self, atr[15], expected_tr)  # 2 steps past seed


class RocGoldenTest(unittest.TestCase):
    """Independent method: direct percentage-change arithmetic."""

    def test_golden(self) -> None:
        close = [100.0] * 13
        close[12] = 110.0
        expected = (Fraction(110, 100) - 1) * 100  # 100 * (C_t/C_(t-12) - 1)
        self.assertEqual(expected, 10)
        roc = formulas.roc_close_12_pct(close)
        assert_within_tolerance(self, roc[12], float(expected))


class ObvGoldenTest(unittest.TestCase):
    """Independent method: direct sequential arithmetic, hand-traced."""

    def test_golden(self) -> None:
        close = [10.0, 11.0, 9.0, 9.0]
        volume = [100.0, 50.0, 30.0, 20.0]
        expected = [0.0, 50.0, 20.0, 20.0]  # 0; 0+50 (up); 50-30 (down); 20 (flat)
        obv = formulas.obv_series(close, volume)
        for t in range(4):
            assert_within_tolerance(self, obv[t], expected[t])


class CciGoldenTest(unittest.TestCase):
    """Independent method: typical_price is a strict arithmetic sequence
    1..20, so the closed-form mean is (1+20)/2=10.5 and the closed-form
    mean absolute deviation of a symmetric arithmetic sequence around its
    own mean is derivable from the sum of the first 10 half-integers,
    without scanning the window."""

    def test_golden(self) -> None:
        n = 20
        high = [float(t + 1) for t in range(n)]
        low = list(high)
        close = list(high)
        tp = formulas.typical_price_series(high, low, close)
        tp_mean = Fraction(1 + 20, 2)  # 10.5, closed-form arithmetic mean
        self.assertEqual(tp_mean, Fraction(21, 2))
        # Deviations are |k - 10.5| for k=1..20: symmetric, sum = 2*(0.5+1.5+...+9.5)
        # = 2 * 10 * (0.5+9.5)/2 = 2*50 = 100; mad = 100/20 = 5.
        mad = Fraction(100, 20)
        self.assertEqual(mad, 5)
        tp_20 = Fraction(20)
        expected = (tp_20 - tp_mean) / (Fraction(15, 1000) * mad)
        self.assertEqual(expected, Fraction(380, 3))
        cci, flags = formulas.cci_20(tp)
        assert_within_tolerance(self, cci[19], float(expected))


class MfiGoldenTest(unittest.TestCase):
    """Independent method: strictly increasing typical_price means every
    directional flow for t=1..14 is positive and none is negative, by the
    definition of the directional-flow rule — so negative_sum=0 and
    MFI=100 by the certified null-case rule, without summing flows."""

    def test_golden(self) -> None:
        n = 16
        high = [10.0 + t for t in range(n)]
        low = [9.0 + t for t in range(n)]
        close = [9.5 + t for t in range(n)]
        volume = [100.0] * n
        tp = formulas.typical_price_series(high, low, close)
        mfi = formulas.mfi_14(tp, volume)
        assert_within_tolerance(self, mfi[14], 100.0)


class AdxSuiteGoldenTest(unittest.TestCase):
    """Independent method: algebraic fixed-point construction. H_t=100+2t,
    L_t=95+2t, C_t=97+2t give constant TR=5, +DM=2, -DM=0 for all t>=1 by
    direct substitution (shown below). The seed sums (14*TR, 14*+DM, 14*-DM)
    are themselves the fixed point of the Wilder-sum recursion
    (smoothed*(13/14)+current = smoothed when current = smoothed/14), so
    +DI=40, -DI=0, DX=100 hold constant from t=14 onward with no transient,
    and the ADX seed/recursion (also a fixed point at DX=100) stays at
    exactly 100 through the seed and both required recursion steps."""

    def _build_hlc(self, n: int) -> tuple[list[float], list[float], list[float]]:
        high = [100.0 + 2 * t for t in range(n)]
        low = [95.0 + 2 * t for t in range(n)]
        close = [97.0 + 2 * t for t in range(n)]
        return high, low, close

    def test_constant_tr_and_dm_by_direct_substitution(self) -> None:
        high, low, close = self._build_hlc(30)
        # TR_t = max(H_t-L_t, |H_t-C_{t-1}|, |L_t-C_{t-1}|)
        #      = max(5, |(100+2t)-(97+2(t-1))|, |(95+2t)-(97+2(t-1))|)
        #      = max(5, |5|, |0|) = 5, for all t>=1.
        for t in range(1, 30):
            h_minus_l = high[t] - low[t]
            h_minus_c_prev = abs(high[t] - close[t - 1])
            l_minus_c_prev = abs(low[t] - close[t - 1])
            self.assertEqual(h_minus_l, 5.0)
            self.assertEqual(h_minus_c_prev, 5.0)
            self.assertEqual(l_minus_c_prev, 0.0)
        # up_move_t = H_t - H_{t-1} = 2; down_move_t = L_{t-1} - L_t = -2.
        # up_move > down_move and up_move > 0 -> plus_dm=2, minus_dm=0.
        for t in range(1, 30):
            up_move = high[t] - high[t - 1]
            down_move = low[t - 1] - low[t]
            self.assertEqual(up_move, 2.0)
            self.assertEqual(down_move, -2.0)

    def test_seed_and_fixed_point_recursion(self) -> None:
        # Fixed-point check via Fraction: smoothed_sum = 14*constant is a
        # fixed point of smoothed_next = smoothed_prev*(13/14) + constant.
        tr_sum = Fraction(14 * 5)
        plus_dm_sum = Fraction(14 * 2)
        minus_dm_sum = Fraction(14 * 0)
        self.assertEqual(tr_sum * Fraction(13, 14) + 5, tr_sum)
        self.assertEqual(plus_dm_sum * Fraction(13, 14) + 2, plus_dm_sum)
        self.assertEqual(minus_dm_sum * Fraction(13, 14) + 0, minus_dm_sum)

        expected_plus_di = 100 * plus_dm_sum / tr_sum  # = 40
        expected_minus_di = 100 * minus_dm_sum / tr_sum  # = 0
        expected_dx = 100 * abs(expected_plus_di - expected_minus_di) / (
            expected_plus_di + expected_minus_di
        )  # = 100
        self.assertEqual(expected_plus_di, 40)
        self.assertEqual(expected_minus_di, 0)
        self.assertEqual(expected_dx, 100)

        # ADX seed = mean(dx_14..27) = 100 (constant); recursion at 28, 29
        # is also a fixed point: ((13*100)+100)/14 = 100.
        expected_adx = Fraction(100)
        self.assertEqual((13 * expected_adx + expected_dx) / 14, expected_adx)

        high, low, close = self._build_hlc(30)
        plus_di, minus_di, dx, adx, flags = formulas.adx_suite(high, low, close)
        assert_within_tolerance(self, plus_di[14], float(expected_plus_di))
        assert_within_tolerance(self, minus_di[14], float(expected_minus_di))
        assert_within_tolerance(self, dx[14], float(expected_dx))
        # Seed and two required recursion steps (§27.2), all at the fixed point.
        assert_within_tolerance(self, adx[27], float(expected_adx))
        assert_within_tolerance(self, adx[28], float(expected_adx))
        assert_within_tolerance(self, adx[29], float(expected_adx))


if __name__ == "__main__":
    unittest.main()
