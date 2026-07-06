import numpy as np
from collections import deque, Counter


class RegimeClassifier:

    def __init__(self,
                 window_size=50,
                 smooth_window=10,
                 volatility_threshold_high=0.75,
                 volatility_threshold_low=0.25):

        # rolling market memory
        self.window_size = window_size
        self.smooth_window = smooth_window

        self.market_window = deque(maxlen=window_size)
        self.regime_history = deque(maxlen=smooth_window)

        # hysteresis state
        self.current_regime = "UNKNOWN"
        self.last_stable_regime = "UNKNOWN"

        # thresholds
        self.vol_high = volatility_threshold_high
        self.vol_low = volatility_threshold_low

    # ----------------------------

    def classify(self, state):

        features = state.get("features", {})

        price = features.get("price", None)
        volatility = features.get("volatility", None)
        momentum = features.get("momentum", None)
        trend = features.get("trend", None)

        # fallback if missing
        if volatility is None:
            volatility = np.random.random()

        if momentum is None:
            momentum = np.random.random()

        if price is None:
            price = np.random.random()

        # store window
        self.market_window.append({
            "price": price,
            "volatility": volatility,
            "momentum": momentum
        })

        raw_regime = self._detect_raw_regime()

        self.regime_history.append(raw_regime)

        smoothed = self._smooth_regime()

        final = self._apply_hysteresis(smoothed)

        self.current_regime = final

        return final

    # ----------------------------

    def _detect_raw_regime(self):

        if len(self.market_window) < 10:
            return "UNKNOWN"

        avg_vol = np.mean([x["volatility"] for x in self.market_window])
        avg_mom = np.mean([x["momentum"] for x in self.market_window])
        last_price = self.market_window[-1]["price"]
        first_price = self.market_window[0]["price"]

        price_delta = last_price - first_price

        # volatility regime
        if avg_vol > self.vol_high:
            return "HIGH_VOLATILITY"

        # trend detection
        if price_delta > 0.6 and avg_mom > 0:
            return "TREND_UP"

        if price_delta < -0.6 and avg_mom < 0:
            return "TREND_DOWN"

        # neutral compression
        if avg_vol < self.vol_low:
            return "LOW_VOLATILITY"

        return "CHOP"

    # ----------------------------

    def _smooth_regime(self):

        if len(self.regime_history) < 5:
            return self.current_regime

        counts = Counter(self.regime_history)

        return counts.most_common(1)[0][0]

    # ----------------------------

    def _apply_hysteresis(self, candidate):

        # no change
        if candidate == self.current_regime:
            return self.current_regime

        # initial state
        if self.current_regime == "UNKNOWN":
            self.last_stable_regime = candidate
            return candidate

        recent = list(self.regime_history)[-5:]

        # confirmation requirement
        if recent.count(candidate) >= 3:
            self.last_stable_regime = candidate
            return candidate

        return self.current_regime

    # ----------------------------

    def get_state(self):

        return {
            "current": self.current_regime,
            "last_stable": self.last_stable_regime,
            "window_size": len(self.market_window),
            "history_size": len(self.regime_history)
        }