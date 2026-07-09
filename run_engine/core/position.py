# run_engine/core/position.py

from typing import Any, Dict, Optional


class PositionEngine:
    def __init__(self):
        self.position = "FLAT"
        self.side = None
        self.entry_price = 0.0
        self.quantity = 0.0
        self.last_price = 0.0

    def project(self, lifecycle_position: Optional[Dict[str, Any]], state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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

    def update_post_trade(
        self,
        execution: Dict[str, Any],
        state: Dict[str, Any],
        lifecycle_position: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        price = self._extract_price(state)

        if lifecycle_position is None:
            return self._set_flat(price)

        projected_position = lifecycle_position.get("position", "FLAT")
        projected_quantity = self._safe_float(lifecycle_position.get("quantity", 0.0))

        if projected_position == "FLAT":
            return self._set_flat(price)

        if self.position == projected_position and projected_position in {"LONG", "SHORT"}:
            if projected_quantity > self.quantity:
                execution_quantity = self._safe_float(
                    execution.get("quantity", projected_quantity - self.quantity)
                )
                self.entry_price = self._weighted_average_entry_price(
                    current_entry_price=self.entry_price,
                    current_quantity=self.quantity,
                    execution_price=price,
                    execution_quantity=execution_quantity,
                )

            self.position = projected_position
            self.side = lifecycle_position.get("side") or projected_position
            self.quantity = projected_quantity
            self.last_price = price
            return self.snapshot()

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
    def _weighted_average_entry_price(current_entry_price: float, current_quantity: float, execution_price: float, execution_quantity: float) -> float:
        total_quantity = current_quantity + execution_quantity
        if total_quantity <= 0.0:
            return 0.0
        return ((current_entry_price * current_quantity) + (execution_price * execution_quantity)) / total_quantity

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
