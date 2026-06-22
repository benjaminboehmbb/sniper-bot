from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from tools.ssi.common.scientific_object import ScientificObject


class TradeRuntimeLoadError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RuntimeTrade(ScientificObject):
    trade_id: str
    system_state_id: str
    side: str
    entry_timestamp_utc: datetime
    exit_timestamp_utc: datetime
    entry_price: float
    exit_price: float
    duration_sec: float
    pnl: float
    pnl_net: float
    pnl_pct: float
    pnl_pct_net: float
    exit_reason: str
    schema_version: int

    def deterministic_id(self) -> str:
        return self.trade_id


REQUIRED_TRADE_FIELDS = [
    "trade_id",
    "system_state_id",
    "side",
    "entry_timestamp_utc",
    "exit_timestamp_utc",
    "entry_price",
    "exit_price",
    "duration_sec",
    "pnl",
    "pnl_net",
    "pnl_pct",
    "pnl_pct_net",
    "exit_reason",
    "schema_version",
]


def parse_runtime_datetime(value: str) -> datetime:
    text = str(value).strip()

    if text == "":
        raise TradeRuntimeLoadError("Empty datetime value")

    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _require(row: dict[str, Any], field: str) -> Any:
    if field not in row:
        raise TradeRuntimeLoadError(f"Missing required trade field: {field}")

    value = row[field]

    if value is None:
        raise TradeRuntimeLoadError(f"Null required trade field: {field}")

    if isinstance(value, str) and value.strip() == "":
        raise TradeRuntimeLoadError(f"Empty required trade field: {field}")

    return value


def _parse_float(row: dict[str, Any], field: str) -> float:
    value = _require(row, field)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise TradeRuntimeLoadError(f"Invalid float for field {field}: {value}") from exc


def _parse_int(row: dict[str, Any], field: str) -> int:
    value = _require(row, field)
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise TradeRuntimeLoadError(f"Invalid int for field {field}: {value}") from exc


def runtime_trade_from_row(row: dict[str, Any]) -> RuntimeTrade:
    for field in REQUIRED_TRADE_FIELDS:
        _require(row, field)

    entry_ts = parse_runtime_datetime(str(row["entry_timestamp_utc"]))
    exit_ts = parse_runtime_datetime(str(row["exit_timestamp_utc"]))

    if exit_ts < entry_ts:
        raise TradeRuntimeLoadError("Trade exit timestamp is before entry timestamp")

    return RuntimeTrade(
        trade_id=str(row["trade_id"]).strip(),
        system_state_id=str(row["system_state_id"]).strip(),
        side=str(row["side"]).strip().upper(),
        entry_timestamp_utc=entry_ts,
        exit_timestamp_utc=exit_ts,
        entry_price=_parse_float(row, "entry_price"),
        exit_price=_parse_float(row, "exit_price"),
        duration_sec=_parse_float(row, "duration_sec"),
        pnl=_parse_float(row, "pnl"),
        pnl_net=_parse_float(row, "pnl_net"),
        pnl_pct=_parse_float(row, "pnl_pct"),
        pnl_pct_net=_parse_float(row, "pnl_pct_net"),
        exit_reason=str(row["exit_reason"]).strip(),
        schema_version=_parse_int(row, "schema_version"),
    )


def load_runtime_trades(input_path: Path) -> list[RuntimeTrade]:
    if not input_path.exists():
        raise TradeRuntimeLoadError(f"Trade file does not exist: {input_path}")

    if not input_path.is_file():
        raise TradeRuntimeLoadError(f"Trade path is not a file: {input_path}")

    if input_path.stat().st_size <= 0:
        raise TradeRuntimeLoadError(f"Trade file is empty: {input_path}")

    trades: list[RuntimeTrade] = []

    with input_path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            text = line.strip()
            if text == "":
                continue

            try:
                row = json.loads(text)
            except json.JSONDecodeError as exc:
                raise TradeRuntimeLoadError(
                    f"Invalid JSON on line {line_number}"
                ) from exc

            trade = runtime_trade_from_row(row)
            trades.append(trade)

    if len(trades) == 0:
        raise TradeRuntimeLoadError("No runtime trades loaded")

    trade_ids = [trade.trade_id for trade in trades]
    if len(trade_ids) != len(set(trade_ids)):
        raise TradeRuntimeLoadError("Duplicate trade_id detected in runtime trades")

    return trades