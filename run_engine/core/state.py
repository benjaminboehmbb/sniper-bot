class StateEngine:

    def __init__(self):
        self.last_state = None

    # ----------------------------

    def update(self, tick):

        # NORMALIZE INPUT

        if isinstance(tick, dict):
            price = tick.get("price", None)
        else:
            price = None

        if price is None:
            price = self._extract_price_fallback(tick)

        # BUILD STATE

        state = {
            "tick": tick.get("tick") if isinstance(tick, dict) else None,
            "price": float(price),
            "raw": tick
        }

        self.last_state = state
        return state

    # ----------------------------

    def _extract_price_fallback(self, tick):

        # safety fallback (never 0.0 unless broken input)

        if isinstance(tick, dict):
            if "last_price" in tick:
                return tick["last_price"]

            if "close" in tick:
                return tick["close"]

            if "value" in tick:
                return tick["value"]

        return 1.0  # hard safety floor to avoid zero-state collapse