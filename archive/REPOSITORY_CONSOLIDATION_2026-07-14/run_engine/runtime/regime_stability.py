from collections import deque


class RegimeStabilityLayer:

    def __init__(self):

        # last raw regimes
        self.history = deque(maxlen=20)

        # smoothed regime state
        self.current_regime = "UNKNOWN"

        # confidence tracking
        self.regime_counts = {}

        # stability parameters
        self.min_stable_ticks = 3
        self.switch_threshold = 0.6

    def update(self, raw_regime: str):

        self.history.append(raw_regime)

        # count occurrences in window
        counts = {}
        for r in self.history:
            counts[r] = counts.get(r, 0) + 1

        total = len(self.history)

        # compute dominant regime
        dominant, dominant_count = max(counts.items(), key=lambda x: x[1])

        dominance_ratio = dominant_count / total

        # initialize current regime
        if self.current_regime not in counts:
            self.current_regime = dominant

        # stability check
        if dominance_ratio >= self.switch_threshold:

            if dominant != self.current_regime:

                # switch only if stable enough
                if counts[dominant] >= self.min_stable_ticks:
                    self.current_regime = dominant

        return self.current_regime

    def get(self):

        return self.current_regime