#!/usr/bin/env python3
# live_l1/core/loop.py
#
# Minimaler L1 Paper Trading Loop Skeleton (neu erstellt, robust)
#
# Implementiert:
# - Schritt 1: Start
# - Schritt 2: Snapshot + Validation
# - Schritt 3: Intent (Stub)
# - Schritt 4: Cost/Overtrading Guards (cost_guards.py)
# - Schritt 5: Execution Attempt (Stub)
# - Schritt 6: State Update (S2/S4)
# - Schritt 7: Persistenz (S2/S4)
# - Schritt 8: Loop Delay
#
# ASCII-only. Deterministisch in der Control-Flow-Logik.
# Keine funktionale Aenderung an GS/Engine, nur L1-Guard-Permission Layer.

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from live_l1.logs.logger import L1Logger
from live_l1.io.market import DummyMarketFeed, MarketSnapshot
from live_l1.io.validate import validate_snapshot, ValidationResult
from live_l1.core.intent import make_hold_intent, Intent
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


@dataclass
class LiveState:
    system_state_id: str
    kill_level: str
    is_running: bool
    data_valid: bool

    # Minimaler Guard-State
    guard_last_reason: str
    guard_disable_until_utc: str  # ISO string or ""

    # Minimaler Counter-State (TODO: spaeter real verdrahten)
    trades_today: int
    trades_6h: int
    net_pnl_today_est: float
    last_trade_ts_utc: str  # ISO string or ""


def load_runtime_config(repo_root: str) -> RuntimeConfig:
    tick = float(os.environ.get("L1_DECISION_TICK_SECONDS", "1.0"))
    log_path = os.environ.get("L1_LOG_PATH", os.path.join(repo_root, "live_logs", "l1_paper.log"))
    symbol = os.environ.get("L1_SYMBOL", "BTCUSDT")
    invalid_every = int(os.environ.get("L1_DUMMY_INVALID_EVERY", "0"))

    # Guard config (Integrity)
    gate_mode = os.environ.get("L1_GATE_MODE", "auto").strip().lower()
    fee_roundtrip = float(os.environ.get("L1_FEE_ROUNDTRIP", "0.0004"))

    return RuntimeConfig(
        decision_tick_seconds=tick,
        log_path=log_path,
        symbol=symbol,
        invalid_every=invalid_every,
        state_path_s2=os.path.join(repo_root, "live_state", "s2_position.jsonl"),
        state_path_s4=os.path.join(repo_root, "live_state", "s4_risk.jsonl"),
        gate_mode=gate_mode,
        fee_roundtrip=fee_roundtrip,
    )


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _safe_intent_kind(intent: Intent) -> str:
    """
    Intent models can evolve; avoid hard dependency on a specific attribute name.
    Return a best-effort string for logging.
    """
    # common candidates
    for attr in ("intent_type", "type", "action", "kind", "name"):
        if hasattr(intent, attr):
            try:
                v = getattr(intent, attr)
                return str(v) if v is not None else ""
            except Exception:
                return ""
    # fallback: class name
    return intent.__class__.__name__


def run_l1_loop_step1234567(repo_root: str, max_ticks: int = 6) -> int:
    system_state_id = f"L1P-{uuid.uuid4().hex[:12]}"
    cfg = load_runtime_config(repo_root)
    log = L1Logger(cfg.log_path)

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
    )
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
        },
    )

    ticks = 0
    try:
        while state.is_running and ticks < max_ticks:
            ticks += 1

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
            intent: Intent | None = None
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

            # Step 4: Cost/Overtrading Guards (entry gating)
            last_trade_dt = None
            if state.last_trade_ts_utc:
                try:
                    last_trade_dt = datetime.fromisoformat(state.last_trade_ts_utc.replace("Z", "+00:00"))
                except Exception:
                    last_trade_dt = None

            gm = GuardMetrics(
                now_utc=_now_utc(),
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

            # Step 5: Execution Attempt (Stub)
            if gd.allow_entry and intent is not None:
                er: ExecutionResult = attempt_execution(intent)
                log.log(
                    category="L5",
                    event="order_not_sent",
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    intent_id=getattr(intent, "intent_id", ""),
                    fields={"reason": er.reason},
                )
                # TODO: When real execution is implemented:
                # - if a trade actually happens, update:
                #   state.trades_today += 1
                #   state.trades_6h += 1 (or a rolling window counter)
                #   state.last_trade_ts_utc = _now_utc().isoformat()

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







