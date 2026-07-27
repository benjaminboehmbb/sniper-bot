"""Unit tests for rcc002.s3.formulas — hand-verifiable cases per §27.1/§27.2."""

import math
import unittest

from rcc002.s3 import formulas


class SmaSeriesTests(unittest.TestCase):
    def test_first_valid_at_n_minus_1(self) -> None:
        values = [1.0] * 5
        result = formulas.sma_series(values, 5)
        self.assertIsNone(result[3])
        self.assertEqual(result[4], 1.0)

    def test_constant_series_sma_equals_constant(self) -> None:
        values = [7.0] * 10
        result = formulas.sma_series(values, 5)
        self.assertEqual(result[9], 7.0)

    def test_known_arithmetic_series(self) -> None:
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = formulas.sma_series(values, 3)
        self.assertEqual(result[2], 2.0)  # mean(1,2,3)
        self.assertEqual(result[4], 4.0)  # mean(3,4,5)


class EmaSeriesTests(unittest.TestCase):
    def test_seed_is_sma(self) -> None:
        values = [2.0, 4.0, 6.0, 8.0]
        result = formulas.ema_series(values, 4)
        self.assertEqual(result[3], 5.0)  # mean(2,4,6,8)

    def test_recursion_matches_manual_computation(self) -> None:
        values = [2.0, 4.0, 6.0, 8.0, 10.0]
        result = formulas.ema_series(values, 4)
        alpha = 2 / 5
        expected_seed = 5.0
        expected_next = alpha * 10.0 + (1 - alpha) * expected_seed
        self.assertAlmostEqual(result[4], expected_next, places=12)

    def test_constant_series_stays_constant(self) -> None:
        values = [3.0] * 10
        result = formulas.ema_series(values, 5)
        self.assertEqual(result[9], 3.0)

    def test_none_before_seed(self) -> None:
        values = [1.0, 2.0, 3.0]
        result = formulas.ema_series(values, 5)
        self.assertEqual(result, [None, None, None])


class RsiWilderTests(unittest.TestCase):
    def test_strictly_increasing_series_yields_rsi_100(self) -> None:
        values = [float(i) for i in range(20)]  # constant +1 delta throughout
        rsi, flags = formulas.rsi_wilder_14(values)
        self.assertEqual(rsi[14], 100.0)
        self.assertEqual(rsi[15], 100.0)

    def test_strictly_decreasing_series_yields_rsi_0(self) -> None:
        values = [float(20 - i) for i in range(20)]
        rsi, flags = formulas.rsi_wilder_14(values)
        self.assertEqual(rsi[14], 0.0)

    def test_flat_series_yields_rsi_50(self) -> None:
        values = [5.0] * 20
        rsi, flags = formulas.rsi_wilder_14(values)
        self.assertEqual(rsi[14], 50.0)

    def test_none_before_first_valid_index(self) -> None:
        values = [float(i) for i in range(14)]
        rsi, flags = formulas.rsi_wilder_14(values)
        self.assertIsNone(rsi[13])

    def test_seed_and_two_recursion_steps_hand_verified(self) -> None:
        # gains/losses alternate 2, 0 for deltas 1..16: delta pattern +2,-2,+2,-2,...
        close = [10.0]
        for i in range(16):
            close.append(close[-1] + (2.0 if i % 2 == 0 else -2.0))
        rsi, flags = formulas.rsi_wilder_14(close)
        # Seed at t=14: gains at odd deltas (1,3,5,7,9,11,13) = 2 each (7 gains),
        # losses at even deltas (2,4,...,14) = 2 each (7 losses).
        # avg_gain_14 = (7*2)/14 = 1.0 ; avg_loss_14 = (7*2)/14 = 1.0
        avg_gain_14 = 1.0
        avg_loss_14 = 1.0
        rs_14 = avg_gain_14 / avg_loss_14
        expected_rsi_14 = 100 - 100 / (1 + rs_14)
        self.assertAlmostEqual(rsi[14], expected_rsi_14, places=12)
        # Recursion step at t=15: delta_15 = close[15]-close[14] = +2 (gain=2, loss=0)
        # (t=15 is odd -> "+2" per the construction loop's i-even/t-odd parity)
        gain_15, loss_15 = 2.0, 0.0
        avg_gain_15 = ((13 * avg_gain_14) + gain_15) / 14
        avg_loss_15 = ((13 * avg_loss_14) + loss_15) / 14
        expected_rsi_15 = 100 - 100 / (1 + avg_gain_15 / avg_loss_15)
        self.assertAlmostEqual(rsi[15], expected_rsi_15, places=12)
        # Recursion step at t=16: delta_16 = close[16]-close[15] = -2 (loss=2, gain=0)
        gain_16, loss_16 = 0.0, 2.0
        avg_gain_16 = ((13 * avg_gain_15) + gain_16) / 14
        avg_loss_16 = ((13 * avg_loss_15) + loss_16) / 14
        expected_rsi_16 = 100 - 100 / (1 + avg_gain_16 / avg_loss_16)
        self.assertAlmostEqual(rsi[16], expected_rsi_16, places=12)


class MacdTests(unittest.TestCase):
    def test_first_valid_index_is_25(self) -> None:
        close = [float(100 + i) for i in range(26)]
        macd_line, signal, hist = formulas.macd(close)
        self.assertIsNotNone(macd_line[25])
        self.assertIsNone(macd_line[24])

    def test_signal_first_valid_at_33(self) -> None:
        close = [float(100 + i) for i in range(34)]
        macd_line, signal, hist = formulas.macd(close)
        self.assertIsNotNone(signal[33])
        self.assertIsNone(signal[32])
        self.assertIsNotNone(hist[33])

    def test_constant_series_macd_is_zero(self) -> None:
        close = [50.0] * 40
        macd_line, signal, hist = formulas.macd(close)
        self.assertAlmostEqual(macd_line[30], 0.0, places=12)
        self.assertAlmostEqual(hist[35], 0.0, places=12)


class BollingerBandsTests(unittest.TestCase):
    def test_constant_series_zero_width(self) -> None:
        close = [10.0] * 25
        mid, upper, lower, width = formulas.bollinger_bands(close)
        self.assertEqual(mid[19], 10.0)
        self.assertEqual(upper[19], 10.0)
        self.assertEqual(lower[19], 10.0)
        self.assertEqual(width[19], 0.0)

    def test_upper_gte_mid_gte_lower(self) -> None:
        close = [10.0 + (i % 3) for i in range(25)]
        mid, upper, lower, width = formulas.bollinger_bands(close)
        for t in range(19, 25):
            self.assertGreaterEqual(upper[t], mid[t])
            self.assertGreaterEqual(mid[t], lower[t])

    def test_first_valid_index_19(self) -> None:
        close = [10.0] * 20
        mid, upper, lower, width = formulas.bollinger_bands(close)
        self.assertIsNone(mid[18])
        self.assertIsNotNone(mid[19])


class StochasticKTests(unittest.TestCase):
    def test_flat_window_yields_50_and_flag(self) -> None:
        high = [10.0] * 20
        low = [10.0] * 20
        close = [10.0] * 20
        result, flags = formulas.stochastic_k_14(high, low, close)
        self.assertEqual(result[13], 50.0)
        self.assertIn("IND_STOCH_FLAT_WINDOW", flags[13])

    def test_close_at_high_yields_100(self) -> None:
        high = [10.0 + i for i in range(20)]
        low = [0.0] * 20
        close = list(high)
        result, flags = formulas.stochastic_k_14(high, low, close)
        self.assertAlmostEqual(result[13], 100.0, places=12)
        self.assertEqual(flags[13], frozenset())


class TrueRangeAtrTests(unittest.TestCase):
    def test_first_index_is_high_minus_low(self) -> None:
        high = [10.0, 12.0]
        low = [8.0, 9.0]
        close = [9.0, 11.0]
        tr = formulas.true_range_series(high, low, close)
        self.assertEqual(tr[0], 2.0)

    def test_atr_seed_is_mean_of_first_14_true_ranges(self) -> None:
        high = [10.0] * 20
        low = [8.0] * 20
        close = [9.0] * 20
        tr = formulas.true_range_series(high, low, close)
        atr = formulas.atr_wilder_14(tr)
        self.assertAlmostEqual(atr[13], 2.0, places=12)

    def test_atr_nonnegative(self) -> None:
        high = [10.0 + (i % 4) for i in range(20)]
        low = [5.0 + (i % 3) for i in range(20)]
        close = [7.0 + (i % 2) for i in range(20)]
        tr = formulas.true_range_series(high, low, close)
        atr = formulas.atr_wilder_14(tr)
        for v in atr:
            if v is not None:
                self.assertGreaterEqual(v, 0.0)


class RocTests(unittest.TestCase):
    def test_known_percentage_change(self) -> None:
        close = [100.0] * 13
        close[12] = 110.0
        roc = formulas.roc_close_12_pct(close)
        self.assertAlmostEqual(roc[12], 10.0, places=12)

    def test_none_before_index_12(self) -> None:
        close = [100.0] * 12
        roc = formulas.roc_close_12_pct(close)
        self.assertIsNone(roc[11])


class ObvTests(unittest.TestCase):
    def test_seed_is_zero(self) -> None:
        close = [10.0]
        volume = [100.0]
        obv = formulas.obv_series(close, volume)
        self.assertEqual(obv[0], 0.0)

    def test_up_day_adds_volume(self) -> None:
        close = [10.0, 11.0]
        volume = [100.0, 50.0]
        obv = formulas.obv_series(close, volume)
        self.assertEqual(obv[1], 50.0)

    def test_down_day_subtracts_volume(self) -> None:
        close = [10.0, 9.0]
        volume = [100.0, 50.0]
        obv = formulas.obv_series(close, volume)
        self.assertEqual(obv[1], -50.0)

    def test_flat_day_unchanged(self) -> None:
        close = [10.0, 10.0]
        volume = [100.0, 50.0]
        obv = formulas.obv_series(close, volume)
        self.assertEqual(obv[1], 0.0)


class CciTests(unittest.TestCase):
    def test_flat_series_zero_mad_flag(self) -> None:
        high = [10.0] * 20
        low = [10.0] * 20
        close = [10.0] * 20
        tp = formulas.typical_price_series(high, low, close)
        cci, flags = formulas.cci_20(tp)
        self.assertEqual(cci[19], 0.0)
        self.assertIn("IND_CCI_ZERO_MAD", flags[19])


class MfiTests(unittest.TestCase):
    def test_all_up_yields_100(self) -> None:
        n = 16
        high = [10.0 + i for i in range(n)]
        low = [9.0 + i for i in range(n)]
        close = [9.5 + i for i in range(n)]
        volume = [100.0] * n
        tp = formulas.typical_price_series(high, low, close)
        mfi = formulas.mfi_14(tp, volume)
        self.assertEqual(mfi[14], 100.0)

    def test_all_down_yields_0(self) -> None:
        n = 16
        high = [30.0 - i for i in range(n)]
        low = [29.0 - i for i in range(n)]
        close = [29.5 - i for i in range(n)]
        volume = [100.0] * n
        tp = formulas.typical_price_series(high, low, close)
        mfi = formulas.mfi_14(tp, volume)
        self.assertEqual(mfi[14], 0.0)


class AdxSuiteTests(unittest.TestCase):
    def test_zero_tr_flagged(self) -> None:
        n = 20
        high = [10.0] * n
        low = [10.0] * n
        close = [10.0] * n
        plus_di, minus_di, dx, adx, flags = formulas.adx_suite(high, low, close)
        self.assertEqual(plus_di[14], 0.0)
        self.assertEqual(minus_di[14], 0.0)
        self.assertIn("IND_ADX_ZERO_TR", flags[14])

    def test_di_and_dx_first_valid_at_14(self) -> None:
        n = 20
        high = [10.0 + i for i in range(n)]
        low = [5.0 + i for i in range(n)]
        close = [7.0 + i for i in range(n)]
        plus_di, minus_di, dx, adx, flags = formulas.adx_suite(high, low, close)
        self.assertIsNotNone(plus_di[14])
        self.assertIsNone(plus_di[13])
        self.assertIsNotNone(dx[14])

    def test_adx_first_valid_at_27(self) -> None:
        n = 30
        high = [10.0 + i for i in range(n)]
        low = [5.0 + i for i in range(n)]
        close = [7.0 + i for i in range(n)]
        plus_di, minus_di, dx, adx, flags = formulas.adx_suite(high, low, close)
        self.assertIsNotNone(adx[27])
        self.assertIsNone(adx[26])

    def test_strict_uptrend_plus_di_dominates(self) -> None:
        n = 30
        high = [10.0 + i for i in range(n)]
        low = [5.0 + i for i in range(n)]
        close = [7.0 + i for i in range(n)]
        plus_di, minus_di, dx, adx, flags = formulas.adx_suite(high, low, close)
        self.assertGreater(plus_di[20], minus_di[20])


if __name__ == "__main__":
    unittest.main()
