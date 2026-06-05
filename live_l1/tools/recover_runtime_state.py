#!/usr/bin/env python3
# live_l1/tools/recover_runtime_state.py
# Startup recovery helper for Live L1 runtime state.
# ASCII-only.

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from live_l1.tools.replay_execution_state import replay_execution_state


@dataclass(frozen=True)
class RecoveredRuntimeState:
    position: str
    side: str
    entry_price: float | None
    entry_timestamp_utc: str
    pause_entries_remaining: int
    execution_events_read: int
    execution_bad_json_lines: int
    loss_cluster_state_loaded: int


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _load_pause_entries_remaining(path: str | Path) -> tuple[int, int]:
    p = Path(path)

    if not p.exists():
        return 0, 0

    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return 0, 0

    if not isinstance(obj, dict):
        return 0, 0

    pause = max(0, _safe_int(obj.get("pause_entries_remaining"), 0))
    return pause, 1


def recover_runtime_state(
    *,
    audit_log_path: str | Path = "live_logs/execution_audit.jsonl",
    loss_cluster_state_path: str | Path = "live_state/loss_cluster_state.json",
) -> RecoveredRuntimeState:
    execution = replay_execution_state(audit_log_path)
    pause_entries_remaining, loaded = _load_pause_entries_remaining(loss_cluster_state_path)

    return RecoveredRuntimeState(
        position=execution.position,
        side=execution.side,
        entry_price=execution.entry_price,
        entry_timestamp_utc=execution.entry_timestamp_utc,
        pause_entries_remaining=int(pause_entries_remaining),
        execution_events_read=int(execution.events_read),
        execution_bad_json_lines=int(execution.bad_json_lines),
        loss_cluster_state_loaded=int(loaded),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audit-log-path",
        default="live_logs/execution_audit.jsonl",
    )
    parser.add_argument(
        "--loss-cluster-state-path",
        default="live_state/loss_cluster_state.json",
    )
    args = parser.parse_args()

    state = recover_runtime_state(
        audit_log_path=args.audit_log_path,
        loss_cluster_state_path=args.loss_cluster_state_path,
    )

    print("position:", state.position)
    print("side:", state.side)
    print("entry_price:", "" if state.entry_price is None else state.entry_price)
    print("entry_timestamp_utc:", state.entry_timestamp_utc)
    print("pause_entries_remaining:", state.pause_entries_remaining)
    print("execution_events_read:", state.execution_events_read)
    print("execution_bad_json_lines:", state.execution_bad_json_lines)
    print("loss_cluster_state_loaded:", state.loss_cluster_state_loaded)

    return 0 if state.execution_bad_json_lines == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
