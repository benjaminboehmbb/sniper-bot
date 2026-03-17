# live_l1/core/execution.py
#
# L1 Execution Attempt Stub (Step 5/8)
# - Garantiert: keine Order wird gesendet
# - Erzeugt saubere L5-Logs
# - Keine Retries, kein Network, keine Nebenwirkungen
#
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from live_l1.core.intent import Intent


@dataclass(frozen=True)
class ExecutionResult:
    sent: bool
    reason: str  # why not sent (stub)


def attempt_execution(intent: Intent) -> ExecutionResult:
    # Absichtlich defensiv: Paper Trading L1 sendet nie Orders
    return ExecutionResult(sent=False, reason="paper_trading_stub_no_execution")
