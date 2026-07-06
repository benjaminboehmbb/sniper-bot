import math

class FeatureEngine:

    def __init__(self):
        self.prices = []

    def update(self, price):

        self.prices.append(price)

        if len(self.prices) > 100:
            self.prices.pop(0)

        return self.compute()

    def compute(self):

        if len(self.prices) < 5:
            return {
                "return": 0.0,
                "volatility": 0.0,
                "momentum": 0.0,
                "range": 0.0
            }

        # returns
        ret = (self.prices[-1] - self.prices[-2]) / (self.prices[-2] + 1e-9)

        # volatility (simple std proxy)
        mean = sum(self.prices) / len(self.prices)
        var = sum((p - mean) ** 2 for p in self.prices) / len(self.prices)
        vol = math.sqrt(var)

        # momentum (trend slope approx)
        momentum = self.prices[-1] - self.prices[-5]

        # range compression
        price_range = max(self.prices[-10:]) - min(self.prices[-10:])

        return {
            "return": ret,
            "volatility": vol,
            "momentum": momentum,
            "range": price_range
        }