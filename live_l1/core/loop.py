#!/usr/bin/env python3
# live_l1/core/loop.py
# L1 core loop with CSV 1m market feed + 5m timing vote fusion.
# L1-D adds state validation before loop start and CSV resume support.
# L1-F adds minimal paper execution logging/state transitions.
# ASCII-only.

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass

from live_l1.logs.logger import L1Logger
from live_l1.io.market import CSVMarketFeed
from live_l1.io.valid import validate_runtime_config
from live_l1.state.state_store import load_or_init_state, persist_state
from live_l1.state.state_validation import validate_loaded_state
from live_l1.guards.guards import evaluate_guards
from live_l1.core.clock import TickClock
from live_l1.core.feature_snapshot import build_feature_snapshot
from live_l1.core.intent import compute_1m_intent_raw
from live_l1.core.timing_5m import compute_5m_timing_vote
from live_l1.core.intent_fusion import fuse_intent_with_5m_timing
from live_l1.core.execution import apply_paper_execution


@dataclass(frozen=True)
class RuntimeConfig:
    repo_root: str
    log_path: str
    state_dir: str
    symbol: str
    gate_mode: str
    fee_roundtrip: float
    decision_tick_seconds: float
    trades_window_hours: int
    test_force_intents: bool
    test_force_buy_every: int
    test_force_sell_every: int
    test_force_warmup_ticks: int
    market_csv_path: str
    seeds_5m_csv: str
    thresh_5m: float
    timing_v2_shadow: bool
    timing_v2_history_len: int


def _env_bool(key: str, default: bool = False) -> bool:
    v = os.environ.get(key)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


def _env_int(key: str, default: int) -> int:
    v = os.environ.get(key)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v)
    except Exception:
        return default


def _env_float(key: str, default: float) -> float:
    v = os.environ.get(key)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v)
    except Exception:
        return default


def load_runtime_config(repo_root: str) -> RuntimeConfig:
    log_path = os.environ.get(
        "L1_LOG_PATH",
        os.path.join(repo_root, "live_logs", "l1_paper.log"),
    )

    cfg = RuntimeConfig(
        repo_root=repo_root,
        log_path=log_path,
        state_dir=os.path.join(repo_root, "live_state"),
        symbol=os.environ.get("L1_SYMBOL", "BTCUSDT"),
        gate_mode=os.environ.get("L1_GATE_MODE", "auto"),
        fee_roundtrip=_env_float("L1_FEE_ROUNDTRIP", 0.0004),
        decision_tick_seconds=_env_float("L1_DECISION_TICK_SECONDS", 1.0),
        trades_window_hours=_env_int("L1_TRADES_WINDOW_HOURS", 6),
        test_force_intents=_env_bool("L1_TEST_FORCE_INTENTS", False),
        test_force_buy_every=_env_int("L1_TEST_FORCE_BUY_EVERY", 10),
        test_force_sell_every=_env_int("L1_TEST_FORCE_SELL_EVERY", 15),
        test_force_warmup_ticks=_env_int("L1_TEST_FORCE_WARMUP_TICKS", 0),
        market_csv_path=os.environ.get(
            "L1_MARKET_CSV_PATH",
            "data/l1_paper_short_gate_test.csv",
        ),
        seeds_5m_csv=os.environ.get(
            "SEEDS_5M_CSV",
            "seeds/5m/btcusdt_5m_long_timing_core_v1.csv",
        ),
        thresh_5m=_env_float("THRESH_5M", 0.60),
        timing_v2_shadow=_env_bool("L1_TIMING_V2_SHADOW", False),
        timing_v2_history_len=_env_int("L1_TIMING_V2_HISTORY_LEN", 3),
    )

    validate_runtime_config(cfg)
    return cfg


def _warnings_to_text(warnings: list[str]) -> str:
    if not warnings:
        return ""
    return ",".join(str(w).strip() for w in warnings if str(w).strip() != "")


def run_l1_loop_step1234567(
    repo_root: str,
    max_ticks: int = 6,
    max_run_seconds: float | None = None,
) -> int:
    system_state_id = f"L1P-{uuid.uuid4().hex[:11]}"

    cfg = load_runtime_config(repo_root)
    log = L1Logger(cfg.log_path)

    state = load_or_init_state(cfg.state_dir, system_state_id=system_state_id)
    validation = validate_loaded_state(state)

    market = CSVMarketFeed(
        csv_path=os.path.join(repo_root, cfg.market_csv_path),
        symbol=cfg.symbol,
        resume_after_snapshot_id=getattr(state, "last_snapshot_id", ""),
    )

    clock = TickClock(decision_tick_seconds=cfg.decision_tick_seconds)

    deadline_monotonic: float | None = None
    if max_run_seconds is not None and max_run_seconds > 0:
        deadline_monotonic = time.monotonic() + float(max_run_seconds)

    try:
        clock.start()

        log.log(
            category="L1",
            event="recovery_checked",
            severity="INFO" if validation.is_valid else "WARNING",
            system_state_id=getattr(state, "system_state_id", system_state_id),
            fields={
                "recovery_mode": validation.recovery_mode,
                "state_valid": int(validation.is_valid),
                "warnings": _warnings_to_text(validation.warnings),
            },
        )

        log.log(
            category="L1",
            event="system_start",
            severity="INFO",
            system_state_id=state.system_state_id,
            fields={
                "symbol": cfg.symbol,
                "gate_mode": cfg.gate_mode,
                "decision_tick_seconds": cfg.decision_tick_seconds,
                "fee_roundtrip": cfg.fee_roundtrip,
                "market_csv_path": cfg.market_csv_path,
                "seeds_5m_csv": cfg.seeds_5m_csv,
                "thresh_5m": cfg.thresh_5m,
                "test_force_intents": int(cfg.test_force_intents),
                "test_force_buy_every": cfg.test_force_buy_every,
                "test_force_sell_every": cfg.test_force_sell_every,
                "test_force_warmup_ticks": cfg.test_force_warmup_ticks,
                "max_run_seconds": max_run_seconds,
                "recovery_mode": validation.recovery_mode,
                "resume_after_snapshot_id": str(getattr(state, "last_snapshot_id", "")),
            },
        )

        while state.is_running and clock.tick_id < max_ticks:
            if deadline_monotonic is not None and time.monotonic() >= deadline_monotonic:
                log.log(
                    category="L1",
                    event="system_stop",
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    fields={"reason": "max_run_seconds_reached", "tick": clock.tick_id},
                )
                return 0

            tick = clock.next_tick()

            try:
                snapshot = market.next_snapshot()
            except StopIteration:
                log.log(
                    category="L1",
                    event="system_stop",
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    fields={"reason": "market_feed_exhausted", "tick": tick.tick_id},
                )
                return 0

            features = build_feature_snapshot(snapshot)

            intent_1m_raw, forced = compute_1m_intent_raw(
                cfg=cfg,
                tick_id=tick.tick_id,
                features=features,
            )

            vote_v1 = compute_5m_timing_vote(
                seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
                thresh=cfg.thresh_5m,
                symbol=cfg.symbol,
                now_utc=tick.tick_started_utc,
            )

            fused = fuse_intent_with_5m_timing(
                intent_1m_raw=intent_1m_raw,
                vote_5m_direction=vote_v1.direction,
                vote_5m_strength=vote_v1.strength,
                vote_5m_seed_id=vote_v1.seed_id,
                thresh=cfg.thresh_5m,
                allow_long=int(features.allow_long),
                allow_short=int(features.allow_short),
            )

            log.log(
                category="L1",
                event="clock_tick",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={
                    "tick": tick.tick_id,
                    "tick_started_utc": tick.tick_started_utc,
                    "decision_tick_seconds": cfg.decision_tick_seconds,
                },
            )

            log.log(
                category="L2",
                event="market_snapshot",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={
                    "tick": tick.tick_id,
                    "snapshot_id": features.snapshot_id,
                    "timestamp_utc": features.timestamp_utc,
                    "symbol": features.symbol,
                    "price": float(features.price),
                    "allow_long": int(features.allow_long),
                    "allow_short": int(features.allow_short),
                    "regime_v2": int(features.regime_v2),
                },
            )

            log.log(
                category="L3",
                event="intent_fused",
                severity="INFO",
                system_state_id=state.system_state_id,
                intent_id=fused.intent_id,
                fields={
                    "tick": tick.tick_id,
                    "allow_long": int(features.allow_long),
                    "allow_short": int(features.allow_short),
                    "intent_1m_raw": intent_1m_raw,
                    "intent_final": fused.intent_final,
                    "reason_code": fused.reason_code,
                    "test_forced_intent": int(forced),
                    "thresh": cfg.thresh_5m,
                    "vote_5m_direction": vote_v1.direction,
                    "vote_5m_seed_id": str(vote_v1.seed_id),
                    "vote_5m_strength": float(vote_v1.strength),
                },
            )

            exec_decision = apply_paper_execution(
                state=state,
                intent_final=fused.intent_final,
                price=float(features.price),
                timestamp_utc=str(features.timestamp_utc),
                position_size=1.0,
            )

            log.log(
                category="L5",
                event="execution",
                severity="INFO",
                system_state_id=state.system_state_id,
                intent_id=fused.intent_id,
                fields={
                    "tick": tick.tick_id,
                    "action": exec_decision.action,
                    "executed": int(exec_decision.executed),
                    "position_before": exec_decision.position_before,
                    "position_after": exec_decision.position_after,
                    "side_after": exec_decision.side_after,
                    "entry_price": "" if exec_decision.entry_price is None else float(exec_decision.entry_price),
                    "entry_timestamp_utc": exec_decision.entry_timestamp_utc,
                    "reason": exec_decision.reason,
                },
            )

            guard_reason, s4_kill_level = evaluate_guards(cfg=cfg, state=state)
            state.s4_risk.kill_level = s4_kill_level

            state.last_snapshot_id = str(features.snapshot_id)
            state.last_timestamp_utc = str(features.timestamp_utc)
            state.last_tick_id = int(tick.tick_id)

            if hasattr(state, "s2_position"):
                if hasattr(state.s2_position, "snapshot_id"):
                    state.s2_position.snapshot_id = str(features.snapshot_id)
                if hasattr(state.s2_position, "last_intent_id"):
                    state.s2_position.last_intent_id = str(fused.intent_id)

            if hasattr(state, "s4_risk"):
                if hasattr(state.s4_risk, "trades_6h") and getattr(state.s4_risk, "trades_6h", None) is None:
                    state.s4_risk.trades_6h = 0
                if hasattr(state.s4_risk, "trades_today") and getattr(state.s4_risk, "trades_today", None) is None:
                    state.s4_risk.trades_today = 0

            log.log(
                category="L6",
                event="state_update",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={
                    "tick": tick.tick_id,
                    "guard_reason": guard_reason,
                    "s2": state.s2_position.position,
                    "s4_kill_level": state.s4_risk.kill_level,
                    "trades_6h": int(getattr(state.s4_risk, "trades_6h", 0)),
                    "trades_today": int(getattr(state.s4_risk, "trades_today", 0)),
                    "last_snapshot_id": str(getattr(state, "last_snapshot_id", "")),
                    "last_timestamp_utc": str(getattr(state, "last_timestamp_utc", "")),
                },
            )

            persist_state(cfg.state_dir, state)

            log.log(
                category="L6",
                event="state_persisted",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={
                    "tick": tick.tick_id,
                    "paths": "s2_position.jsonl,s4_risk.jsonl",
                },
            )

        log.log(
            category="L1",
            event="system_stop",
            severity="INFO",
            system_state_id=state.system_state_id,
            fields={"reason": "max_ticks_reached", "tick": clock.tick_id},
        )
        return 0

    finally:
        try:
            market.close()
        except Exception:
            pass
        log.close()
