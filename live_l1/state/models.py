#!/usr/bin/env python3
# live_l1/state/models.py
#
# Verbindliche State-Modelle fuer L1
# - NUR S2 (Position) und S4 (Risk)
# - Minimal, invariant
#
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Optional


@dataclass
class PositionStateS2:
    symbol: str
    position: str  # FLAT/LONG/SHORT (L1: FLAT only)
    size: float    # 0.0 in L1
    entry_price: Optional[float]


@dataclass
class RiskStateS4:
    kill_level: str  # NONE/SOFT/HARD/EMERGENCY
    cooldown_until_utc: Optional[str]


@dataclass(frozen=True)
class LegacyRiskStateS4ProjectionV1:
    """Complete, lossless Legacy S4 view used only by offline IU4 projection.

    This additive model deliberately does not replace ``RiskStateS4``.  It
    rejects the permissive/defaulting behavior that the Schema-1 state store
    must retain for compatibility.
    """

    kill_level: str
    cooldown_until_utc: str
    trades_today: int
    loss_today: str
    anomaly_counter: int
    trades_6h: int
    last_trade_timestamp_utc: str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.kill_level) is not str or self.kill_level not in {
            "NONE", "SOFT", "HARD", "EMERGENCY"
        }:
            raise ValueError("invalid projected Legacy kill level")
        for name in ("cooldown_until_utc", "loss_today", "last_trade_timestamp_utc"):
            if type(getattr(self, name)) is not str or not getattr(self, name):
                raise ValueError(f"invalid projected Legacy {name}")
        for name in ("cooldown_until_utc", "last_trade_timestamp_utc"):
            value = getattr(self, name)
            if value != "NONE":
                try:
                    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError as exc:
                    raise ValueError(f"invalid projected Legacy {name}") from exc
                if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
                    raise ValueError(f"noncanonical projected Legacy {name}")
        try:
            loss = Decimal(self.loss_today)
        except InvalidOperation as exc:
            raise ValueError("invalid projected Legacy loss_today") from exc
        canonical_loss = format(loss, "f").rstrip("0").rstrip(".") if "." in format(loss, "f") else format(loss, "f")
        if canonical_loss in {"", "-0"}:
            canonical_loss = "0"
        if not loss.is_finite() or canonical_loss != self.loss_today:
            raise ValueError("noncanonical projected Legacy loss_today")
        for name in ("trades_today", "anomaly_counter", "trades_6h"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"invalid projected Legacy {name}")
        if type(self.reason_codes) is not tuple:
            raise ValueError("projected Legacy reason_codes must be an exact tuple")
        if any(
            type(value) is not str
            or not value
            or value != value.strip()
            or not value.isascii()
            for value in self.reason_codes
        ):
            raise ValueError("invalid projected Legacy reason code")
        if len(set(self.reason_codes)) != len(self.reason_codes):
            raise ValueError("duplicate projected Legacy reason code")

    def to_record(self) -> dict[str, Any]:
        return {
            "kill_level": self.kill_level,
            "cooldown_until_utc": self.cooldown_until_utc,
            "trades_today": self.trades_today,
            "loss_today": self.loss_today,
            "anomaly_counter": self.anomaly_counter,
            "trades_6h": self.trades_6h,
            "last_trade_timestamp_utc": self.last_trade_timestamp_utc,
            "reason_codes": list(self.reason_codes),
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "LegacyRiskStateS4ProjectionV1":
        fields = set(cls.__dataclass_fields__)
        if type(record) is not dict or set(record) != fields:
            raise ValueError("projected Legacy S4 fields are missing or unknown")
        reasons = record.get("reason_codes")
        if type(reasons) is not list:
            raise ValueError("projected Legacy reason_codes must serialize as a list")
        value = cls(
            kill_level=record.get("kill_level"),
            cooldown_until_utc=record.get("cooldown_until_utc"),
            trades_today=record.get("trades_today"),
            loss_today=record.get("loss_today"),
            anomaly_counter=record.get("anomaly_counter"),
            trades_6h=record.get("trades_6h"),
            last_trade_timestamp_utc=record.get("last_trade_timestamp_utc"),
            reason_codes=tuple(reasons),
        )
        if record != value.to_record():
            raise ValueError("projected Legacy S4 record is not canonical")
        return value
