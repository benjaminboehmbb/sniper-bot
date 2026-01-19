#!/usr/bin/env python3
# live_l1/core/loop.py
#
# Minimaler L1 Paper Trading Loop Skeleton (robust, mit Counter-Verdrahtung)
#
# Implementiert:
# - Snapshot + Validation
# - Intent (Stub)
# - Cost/Overtrading Guards (cost_guards.py)
# - Execution Attempt (Stub)
# - State Persistenz (S2/S4)
#
# Counter wiring (minimal, kontrolliert):
# - trades_today
# - trades_6h (rolling 6h window)
# - last_trade_ts_utc
# - net_pnl_today_est (noch 0.0, bis echte PnL aus Execution kommt)
#
# ASCII-only. Deterministisch im Control-Flow.

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional, Deque

from live_l1.logs.logger import L1Logger
from live_l1.io.market import DummyMarketFeed, MarketSnapshot
from live_l1.io.validate import validate_snapshot, ValidationResult
from live_l1.core.intent import make_hold_intent, Intent
from live_l1.core.intent_fusion import TimingVote, merge_intent_with_5m_vote
from live_l1.core.execution import attempt_execution, ExecutionResult
from live_l1.state.models import PositionStateS2, RiskStateS4
from live_l1.state.persist import _atomic_append_jsonl

from live_l1.guards.cost_guards import GuardMetrics, evaluate_cost_guards


@dataclass(frozen=True)
class RuntimeConfig:
    decision_tick_seconds: float
    log_path: str
    symbol: str
    invalid_every: int
    state_path_s2: str
    state_path_s4: str

    # Guard-relevante config (Integrity)
    gate_mode: str
    fee_roundtrip: float

    # Rolling window
    trades_window_hours: int


@dataclass
class LiveState:
    system_state_id: str
    kill_level: str
    is_running: bool
    data_valid: bool

    # Guard-State
    guard_last_reason: str
    guard_disable_until_utc: str  # ISO string or ""

    # Counter-State
    trades_today: int
    trades_6h: int
    net_pnl_today_est: float
    last_trade_ts_utc: str  # ISO string or ""

    # For daily reset
    day_utc_yyyy_mm_dd: str


def load_runtime_config(repo_root: str) -> RuntimeConfig:
    tick = float(os.environ.get("L1_DECISION_TICK_SECONDS", "1.0"))
    log_path = os.environ.get("L1_LOG_PATH", os.path.join(repo_root, "live_logs", "l1_paper.log"))
    symbol = os.environ.get("L1_SYMBOL", "BTCUSDT")
    invalid_every = int(os.environ.get("L1_DUMMY_INVALID_EVERY", "0"))

    gate_mode = os.environ.get("L1_GATE_MODE", "auto").strip().lower()
    fee_roundtrip = float(os.environ.get("L1_FEE_ROUNDTRIP", "0.0004"))

    trades_window_hours = int(os.environ.get("L1_TRADES_WINDOW_HOURS", "6"))

    return RuntimeConfig(
        decision_tick_seconds=tick,
        log_path=log_path,
        symbol=symbol,
        invalid_every=invalid_every,
        state_path_s2=os.path.join(repo_root, "live_state", "s2_position.jsonl"),
        state_path_s4=os.path.join(repo_root, "live_state", "s4_risk.jsonl"),
        gate_mode=gate_mode,
        fee_roundtrip=fee_roundtrip,
        trades_window_hours=trades_window_hours,
    )


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _safe_intent_kind(intent: Intent) -> str:
    for attr in ("intent_type", "type", "action", "kind", "name"):
        if hasattr(intent, attr):
            try:
                v = getattr(intent, attr)
                return str(v) if v is not None else ""
            except Exception:
                return ""
    return intent.__class__.__name__


def _parse_iso_utc(ts: str) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _is_trade_executed(er: ExecutionResult) -> bool:
    """
    Robust heuristic: detect if execution result indicates a trade happened.
    We avoid hard dependency on ExecutionResult schema.
    """
    # Preferred: attribute 'executed' or 'filled' or similar.
    for attr in ("executed", "filled", "is_filled", "did_execute", "success"):
        if hasattr(er, attr):
            try:
                v = getattr(er, attr)
                if isinstance(v, bool):
                    return v
            except Exception:
                pass

    # Fallback: inspect reason string (stub uses 'paper_trading_stub_no_execution')
    reason = ""
    try:
        reason = str(getattr(er, "reason", "")).lower()
    except Exception:
        reason = ""

    if "no_execution" in reason:
        return False
    if "not_sent" in reason:
        return False
    if "executed" in reason or "filled" in reason or "fill" in reason:
        return True

    # Default conservative: assume not executed
    return False


def _roll_trades_window(trade_ts: Deque[datetime], now: datetime, window_hours: int) -> int:
    cutoff = now - timedelta(hours=window_hours)
    while trade_ts and trade_ts[0] < cutoff:
        trade_ts.popleft()
    return len(trade_ts)


def _utc_day_str(ts: datetime) -> str:
    d = ts.date()
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"


def run_l1_loop_step1234567(repo_root: str, max_ticks: int = 6) -> int:
    system_state_id = f"L1P-{uuid.uuid4().hex[:12]}"
    cfg = load_runtime_config(repo_root)
    log = L1Logger(cfg.log_path)

    now0 = _now_utc()
    state = LiveState(
        system_state_id=system_state_id,
        kill_level="NONE",
        is_running=True,
        data_valid=False,
        guard_last_reason="INIT",
        guard_disable_until_utc="",
        trades_today=0,
        trades_6h=0,
        net_pnl_today_est=0.0,
        last_trade_ts_utc="",
        day_utc_yyyy_mm_dd=_utc_day_str(now0),
    )

    # Rolling trade timestamps for trades_6h
    trade_ts_window: Deque[datetime] = deque()

    feed = DummyMarketFeed(symbol=cfg.symbol, invalid_every=cfg.invalid_every)

    log.log(
        category="L1",
        event="system_start",
        severity="INFO",
        system_state_id=state.system_state_id,
        fields={
            "repo_root": repo_root,
            "decision_tick_seconds": cfg.decision_tick_seconds,
            "symbol": cfg.symbol,
            "gate_mode": cfg.gate_mode,
            "fee_roundtrip": cfg.fee_roundtrip,
            "trades_window_hours": cfg.trades_window_hours,
        },
    )

    ticks = 0
    try:
        while state.is_running and ticks < max_ticks:
            ticks += 1
            now = _now_utc()

            # Daily reset
            day_str = _utc_day_str(now)
            if day_str != state.day_utc_yyyy_mm_dd:
                state.day_utc_yyyy_mm_dd = day_str
                state.trades_today = 0
                state.net_pnl_today_est = 0.0
                state.last_trade_ts_utc = ""
                # Keep rolling window timestamps, they are time-based anyway.
                log.log(
                    category="L6",
                    event="daily_reset",
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    fields={"day_utc": state.day_utc_yyyy_mm_dd},
                )

            # Step 2: Snapshot + Validation
            snap: MarketSnapshot = feed.next_snapshot()
            log.log(
                category="L2",
                event="snapshot_received",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={"snapshot_id": snap.snapshot_id, "price": snap.price},
            )
            vr: ValidationResult = validate_snapshot(snap)
            state.data_valid = bool(vr.data_valid)
            log.log(
                category="L2",
                event=("data_valid" if state.data_valid else "data_invalid"),
                severity=("INFO" if state.data_valid else "WARN"),
                system_state_id=state.system_state_id,
                fields={"snapshot_id": snap.snapshot_id},
            )

            # Step 3: Intent (Stub)
            intent: Optional[Intent] = None
            fusion = None  # set when data_valid and intent exists
            if state.data_valid:
                intent = make_hold_intent()
                log.log(
                    category="L3",
                    event="intent_created",
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    intent_id=getattr(intent, "intent_id", ""),
                    fields={
                        "snapshot_id": snap.snapshot_id,
                        "intent_kind": _safe_intent_kind(intent),
                    },
                )

                # Step 3b: Intent Fusion (LOG-ONLY, stubbed 5m vote)
                # - No dataflow/aggregation yet
                # - No execution change yet
                kind = _safe_intent_kind(intent)
                kind_u = kind.upper()
                if "BUY" in kind_u:
                    intent_1m_raw = "BUY"
                elif "SELL" in kind_u:
                    intent_1m_raw = "SELL"
                else:
                    intent_1m_raw = "HOLD"

                timing_vote = TimingVote(direction="none", strength=0.0, seed_id=None)
                fusion = merge_intent_with_5m_vote(
                    intent_1m_raw=intent_1m_raw,
                    vote=timing_vote,
                    allow_long=1,
                    allow_short=1,
                    thresh=0.60,
                )
                log.log(
                    category="L3",
                    event="intent_fused",
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    intent_id=getattr(intent, "intent_id", ""),
                    fields={
                        "intent_1m_raw": fusion.intent_1m_raw,
                        "intent_final": fusion.intent_final,
                        "reason_code": fusion.reason_code,
                        "vote_5m_direction": fusion.vote_5m_direction,
                        "vote_5m_strength": fusion.vote_5m_strength,
                        "vote_5m_seed_id": fusion.vote_5m_seed_id,
                        "allow_long": fusion.allow_long,
                        "allow_short": fusion.allow_short,
                        "thresh": fusion.thresh,
                    },
                )

            # Update rolling trades_6h before guard evaluation
            state.trades_6h = _roll_trades_window(trade_ts_window, now, cfg.trades_window_hours)

            # Step 4: Guards
            last_trade_dt = _parse_iso_utc(state.last_trade_ts_utc)
            gm = GuardMetrics(
                now_utc=now,
                trades_today=state.trades_today,
                trades_6h=state.trades_6h,
                net_pnl_today_est=state.net_pnl_today_est,
                last_trade_ts_utc=last_trade_dt,
                gate_mode=cfg.gate_mode,
                fee_roundtrip_configured=cfg.fee_roundtrip,
            )
            gd = evaluate_cost_guards(gm)

            if gd.reason != state.guard_last_reason:
                state.guard_last_reason = gd.reason
                state.guard_disable_until_utc = gd.disable_until.isoformat() if gd.disable_until else ""
                log.log(
                    category="L4",
                    event="guard_state_change",
                    severity=("ERROR" if gd.reason in ("FEE_CONFIG_MISMATCH", "GATE_MODE_NOT_AUTO") else "WARN"
                              if gd.reason != "OK" else "INFO"),
                    system_state_id=state.system_state_id,
                    fields={
                        "guard_reason": gd.reason,
                        "allow_entry": gd.allow_entry,
                        "disable_until_utc": state.guard_disable_until_utc,
                        "trades_today": state.trades_today,
                        "trades_6h": state.trades_6h,
                        "net_pnl_today_est": state.net_pnl_today_est,
                    },
                )

            # Step 5: Execution Attempt
            if gd.allow_entry and intent is not None and fusion is not None:
                er: ExecutionResult = attempt_execution(intent)
                executed = _is_trade_executed(er)

                # LOG-ONLY: execution context (fusion)
                log.log(
                    category="L5",
                    event="execution_context",
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    intent_id=getattr(intent, "intent_id", ""),
                    fields={
                        "intent_1m_raw": getattr(fusion, "intent_1m_raw", ""),
                        "intent_final": getattr(fusion, "intent_final", ""),
                        "reason_code": getattr(fusion, "reason_code", ""),
                    },
                )

                log.log(
                    category="L5",
                    event=("order_executed" if executed else "order_not_sent"),
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    intent_id=getattr(intent, "intent_id", ""),
                    fields={"reason": getattr(er, "reason", ""), "executed": executed},
                )

                if executed:
                    # Update counters
                    state.trades_today += 1
                    trade_ts_window.append(now)
                    state.trades_6h = _roll_trades_window(trade_ts_window, now, cfg.trades_window_hours)
                    state.last_trade_ts_utc = now.isoformat()

                    # net_pnl_today_est update only if ExecutionResult provides something explicit
                    for attr in ("pnl_net", "pnl", "net_pnl", "pnl_est"):
                        if hasattr(er, attr):
                            try:
                                v = float(getattr(er, attr))
                                state.net_pnl_today_est += v
                                break
                            except Exception:
                                pass

            # Step 6: State Update (S2/S4)
            s2 = PositionStateS2(symbol=cfg.symbol, position="FLAT", size=0.0, entry_price=None)
            s4 = RiskStateS4(kill_level=state.kill_level, cooldown_until_utc=None)

            log.log(
                category="L6",
                event="state_update",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={
                    "s2": "FLAT",
                    "s4_kill_level": state.kill_level,
                    "guard_reason": state.guard_last_reason,
                    "trades_today": state.trades_today,
                    "trades_6h": state.trades_6h,
                },
            )

            # Step 7: Persistenz
            _atomic_append_jsonl(
                cfg.state_path_s2,
                {
                    "system_state_id": system_state_id,
                    "symbol": s2.symbol,
                    "position": s2.position,
                    "size": s2.size,
                },
            )
            _atomic_append_jsonl(
                cfg.state_path_s4,
                {
                    "system_state_id": system_state_id,
                    "kill_level": s4.kill_level,
                    "guard_reason": state.guard_last_reason,
                    "guard_disable_until_utc": state.guard_disable_until_utc,
                    "trades_today": state.trades_today,
                    "trades_6h": state.trades_6h,
                    "net_pnl_today_est": state.net_pnl_today_est,
                    "last_trade_ts_utc": state.last_trade_ts_utc,
                    "day_utc": state.day_utc_yyyy_mm_dd,
                },
            )
            log.log(
                category="L6",
                event="state_persisted",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={"paths": "s2_position.jsonl,s4_risk.jsonl"},
            )

            # Step 8: Loop Delay
            log.log(
                category="L1",
                event="loop_delay",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={"tick": ticks, "sleep_s": cfg.decision_tick_seconds},
            )
            time.sleep(cfg.decision_tick_seconds)

        log.log(
            category="L1",
            event="system_stop",
            severity="INFO",
            system_state_id=state.system_state_id,
            fields={"reason": "max_ticks_reached"},
        )
        return 0

    finally:
        log.close()








