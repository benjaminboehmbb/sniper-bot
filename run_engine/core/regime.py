import numpy as np
from collections import deque, Counter


class RegimeClassifier:

    def __init__(
        self,
        window_size=50,
        smooth_window=10,
        volatility_threshold_high=0.75,
        volatility_threshold_low=0.25,
    ):

        self.window_size = window_size
        self.smooth_window = smooth_window

        self.market_window = deque(maxlen=window_size)
        self.regime_history = deque(maxlen=smooth_window)

        self.current_regime = "UNKNOWN"
        self.last_stable_regime = "UNKNOWN"

        self.vol_high = volatility_threshold_high
        self.vol_low = volatility_threshold_low

    def classify(self, state):

        features = state.get("features", {}) if isinstance(state, dict) else {}

        price = self._safe_float(
            features.get("price", state.get("price", 0.0) if isinstance(state, dict) else 0.0)
        )

        volatility = features.get("volatility")
        if volatility is None:
            volatility = self._deterministic_volatility(price)

        momentum = features.get("momentum")
        if momentum is None:
            momentum = self._deterministic_momentum(price)

        self.market_window.append({
            "price": price,
            "volatility": self._safe_float(volatility),
            "momentum": self._safe_float(momentum),
        })

        raw_regime = self._detect_raw_regime()

        self.regime_history.append(raw_regime)

        smoothed = self._smooth_regime()

        final = self._apply_hysteresis(smoothed)

        self.current_regime = final

        return final

    def _detect_raw_regime(self):

        if len(self.market_window) < 10:
            return "UNKNOWN"

        avg_vol = np.mean([x["volatility"] for x in self.market_window])
        avg_mom = np.mean([x["momentum"] for x in self.market_window])
        last_price = self.market_window[-1]["price"]
        first_price = self.market_window[0]["price"]

        price_delta = last_price - first_price

        if avg_vol > self.vol_high:
            return "HIGH_VOLATILITY"

        if price_delta > 0.6 and avg_mom > 0:
            return "TREND_UP"

        if price_delta < -0.6 and avg_mom < 0:
            return "TREND_DOWN"

        if avg_vol < self.vol_low:
            return "LOW_VOLATILITY"

        return "CHOP"

    def _smooth_regime(self):

        if len(self.regime_history) < 5:
            return self.current_regime

        counts = Counter(self.regime_history)

        return counts.most_common(1)[0][0]

    def _apply_hysteresis(self, candidate):

        if candidate == self.current_regime:
            return self.current_regime

        if self.current_regime == "UNKNOWN":
            self.last_stable_regime = candidate
            return candidate

        if candidate != self.last_stable_regime:
            self.last_stable_regime = candidate
            return self.current_regime

        return candidate

    @staticmethod
    def _deterministic_volatility(price):
        normalized = abs(float(price)) % 100.0
        return normalized / 100.0

    @staticmethod
    def _deterministic_momentum(price):
        normalized = (float(price) % 200.0) - 100.0
        return normalized / 100.0

    @staticmethod
    def _safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
