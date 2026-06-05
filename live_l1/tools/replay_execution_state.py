#!/usr/bin/env python3
# live_l1/tools/replay_execution_state.py
# Deterministic replay of Live L1 execution state from execution_audit.jsonl.
# ASCII-only.

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecoveredExecutionState:
    position: str
    side: str
    entry_price: float | None
    entry_timestamp_utc: str
    events_read: int
    bad_json_lines: int


def _safe_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _safe_float_or_none(value: object) -> float | None:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    try:
        return float(s)
    except Exception:
        return None


def replay_execution_state(audit_log_path: str | Path) -> RecoveredExecutionState:
    path = Path(audit_log_path)

    position = "FLAT"
    side = ""
    entry_price: float | None = None
    entry_timestamp_utc = ""

    events_read = 0
    bad_json_lines = 0

    if not path.exists():
        return RecoveredExecutionState(
            position=position,
            side=side,
            entry_price=entry_price,
            entry_timestamp_utc=entry_timestamp_utc,
            events_read=events_read,
            bad_json_lines=bad_json_lines,
        )

    with path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if line == "":
                continue

            try:
                obj = json.loads(line)
            except Exception:
                bad_json_lines += 1
                continue

            if not isinstance(obj, dict):
                bad_json_lines += 1
                continue

            events_read += 1
            event = _safe_text(obj.get("event"), "")

            if event == "ENTRY_ACCEPTED":
                event_side = _safe_text(obj.get("side"), "").lower()
                event_price = _safe_float_or_none(obj.get("price"))
                event_ts = _safe_text(obj.get("timestamp_utc"), "")

                if event_side == "long":
                    position = "LONG"
                    side = "long"
                    entry_price = event_price
                    entry_timestamp_utc = event_ts
                elif event_side == "short":
                    position = "SHORT"
                    side = "short"
                    entry_price = event_price
                    entry_timestamp_utc = event_ts

            elif event == "EXIT_EXECUTED":
                position = "FLAT"
                side = ""
                entry_price = None
                entry_timestamp_utc = ""

            elif event == "ENTRY_BLOCKED":
                continue

            elif event.startswith("LOSS_CLUSTER_"):
                continue

    return RecoveredExecutionState(
        position=position,
        side=side,
        entry_price=entry_price,
        entry_timestamp_utc=entry_timestamp_utc,
        events_read=events_read,
        bad_json_lines=bad_json_lines,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audit-log-path",
        default="live_logs/execution_audit.jsonl",
    )
    args = parser.parse_args()

    state = replay_execution_state(args.audit_log_path)

    print("position:", state.position)
    print("side:", state.side)
    print("entry_price:", "" if state.entry_price is None else state.entry_price)
    print("entry_timestamp_utc:", state.entry_timestamp_utc)
    print("events_read:", state.events_read)
    print("bad_json_lines:", state.bad_json_lines)

    return 0 if state.bad_json_lines == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
