# run_engine/core/position.py

from typing import Any, Dict, Optional


class PositionEngine:
    def __init__(self):
        self.position = "FLAT"
        self.side = None
        self.entry_price = 0.0
        self.quantity = 0.0
        self.last_price = 0.0

    def project(
        self,
        lifecycle_position: Optional[Dict[str, Any]],
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        price = self._extract_price(state)

        if lifecycle_position is None:
            return self._set_flat(price)

        position = lifecycle_position.get("position", "FLAT")
        side = lifecycle_position.get("side")
        entry_price = self._safe_float(lifecycle_position.get("entry_price", 0.0))
        quantity = self._safe_float(lifecycle_position.get("quantity", 0.0))

        if position not in {"LONG", "SHORT"}:
            return self._set_flat(price)

        self.position = position
        self.side = side or position
        self.entry_price = entry_price
        self.quantity = quantity
        self.last_price = price

        return self.snapshot()

    def update_pre_trade(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.last_price = self._extract_price(state)
        return self.snapshot()

    def update_post_trade(
        self,
        execution: Dict[str, Any],
        state: Dict[str, Any],
        lifecycle_position: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.project(lifecycle_position, state)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "side": self.side,
            "entry_price": self.entry_price,
            "quantity": self.quantity,
            "last_price": self.last_price,
        }

    def _set_flat(self, price: float) -> Dict[str, Any]:
        self.position = "FLAT"
        self.side = None
        self.entry_price = 0.0
        self.quantity = 0.0
        self.last_price = price
        return self.snapshot()

    @staticmethod
    def _extract_price(state: Optional[Dict[str, Any]]) -> float:
        if not isinstance(state, dict):
            return 0.0
        return PositionEngine._safe_float(state.get("price", 0.0))

    @staticmethod
    def _safe_float(value: Any) -> float:
        if value is None:
            return 0.0
        return float(value)
