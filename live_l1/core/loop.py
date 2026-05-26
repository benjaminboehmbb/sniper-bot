#!/usr/bin/env python3
# live_l1/core/loop.py
# CLEAN VERSION (TEST_BYPASS REMOVED)
# ASCII-only.

from __future__ import annotations

import csv
import os
import time
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass

from live_l1.logs.logger import L1Logger
from live_l1.io.market import CSVMarketFeed
from live_l1.io.valid import validate_runtime_config
from live_l1.state.state_store import load_or_init_state, persist_state
from live_l1.state.state_validation import validate_loaded_state
from live_l1.guards.guards import evaluate_guards
from live_l1.core.clock import TickClock
from live_l1.core.feature_snapshot import build_feature_snapshot
from live_l1.core.regime_detector import detect_regime
from live_l1.core.intent import compute_1m_intent_raw
from live_l1.core.timing_5m import compute_5m_timing_vote
from live_l1.core.intent_fusion import fuse_intent_with_5m_timing
from live_l1.core.execution import apply_paper_execution
from live_l1.meta_state.meta_state_shadow import build_meta_state_shadow


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

def _safe_float_lifecycle(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except Exception:
        return default


def _parse_lifecycle_ts(value: object) -> datetime | None:
    s = "" if value is None else str(value).strip()
    if s == "":
        return None
    s = s.replace("_", " ")
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s[:-1] + "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
    a = _parse_lifecycle_ts(entry_ts)
    b = _parse_lifecycle_ts(current_ts)
    if a is None or b is None:
        return 0.0
    out = (b - a).total_seconds()
    return float(out) if out > 0.0 else 0.0




def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
    side_l = str(side).strip().lower()
    regime_l = str(regime).strip().lower()
    atr_l = str(atr_quality).strip().lower()

    reasons = []

    risk = 0

    if side_l == "long" and regime_l == "bear":
        risk = max(risk, 2)
        reasons.append("long_bear_incompatibility")

    if side_l == "short" and regime_l == "bull":
        risk = max(risk, 2)
        reasons.append("short_bull_incompatibility")

    if side_l == "short" and regime_l == "bear":
        risk = max(risk, 0)
        reasons.append("short_bear_compatible")

    if side_l == "long" and regime_l == "bull":
        risk = max(risk, 0)
        reasons.append("long_bull_compatible")

    if atr_l == "bad_atr":
        risk = max(risk, 1)
        reasons.append("bad_atr")

    if side_l == "long" and current_score <= -3:
        risk = max(risk, 2)
        reasons.append("long_adverse_score")

    if side_l == "short" and current_score >= 3:
        risk = max(risk, 2)
        reasons.append("short_adverse_score")

    if risk >= 3:
        name = "COLLAPSE_RISK"
    elif risk == 2:
        name = "TOXIC"
    elif risk == 1:
        name = "WARNING"
    else:
        name = "SAFE"

    return risk, name, "|".join(reasons)


def _append_passive_shadow_risk_snapshot(
    repo_root: str,
    tick_id: int,
    timestamp_utc: str,
    snapshot_id: str,
    state,
    features,
    regime: str,
) -> None:
    position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()

    if position not in ("LONG", "SHORT"):
        return

    side = position.lower()

    current_score = int(
        features.signal("rsi_signal")
        + features.signal("bollinger_signal")
        + features.signal("stoch_signal")
        + features.signal("cci_signal")
    )

    atr_sig = int(features.signal("atr_signal"))
    atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"

    regime_label = str(getattr(regime, "label", regime)).strip().lower()

    risk_level, risk_name, reason = _passive_shadow_risk_from_context(
        side=side,
        regime=regime_label,
        atr_quality=atr_quality,
        current_score=current_score,
    )

    out_path = os.path.join(repo_root, "live_logs", "passive_shadow_risk_snapshots.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fieldnames = [
        "tick_id",
        "timestamp_utc",
        "snapshot_id",
        "entry_timestamp_utc",
        "side",
        "position",
        "price",
        "current_score",
        "market_regime",
        "atr_quality",
        "shadow_risk_level",
        "shadow_risk_name",
        "shadow_risk_reason",
        "meta_state_score",
        "meta_state_bucket",
        "position_multiplier",
        "meta_state_enabled",
    ]

    exists = os.path.exists(out_path)

    with open(out_path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)

        if not exists:
            writer.writeheader()

        writer.writerow(
            {
                "tick_id": int(tick_id),
                "timestamp_utc": str(timestamp_utc),
                "snapshot_id": str(snapshot_id),
                "entry_timestamp_utc": str(getattr(state.s2_position, "entry_timestamp_utc", "")),
                "side": side,
                "position": position,
                "price": float(getattr(features, "price", 0.0)),
                "current_score": int(current_score),
                "market_regime": regime_label,
                "atr_quality": atr_quality,
                "shadow_risk_level": int(risk_level),
                "shadow_risk_name": str(risk_name),
                "shadow_risk_reason": str(reason),
                "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
                "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
                "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
                "meta_state_enabled": 0,
            }
        )

def _append_trade_lifecycle_snapshot(
    *,
    repo_root: str,
    tick_id: int,
    timestamp_utc: str,
    snapshot_id: str,
    state,
    features,
    regime,
) -> None:
    if not hasattr(state, "s2_position"):
        return

    pos = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
    if pos not in ("LONG", "SHORT"):
        return

    side = str(getattr(state.s2_position, "side", "")).strip().lower()
    entry_price = _safe_float_lifecycle(getattr(state.s2_position, "entry_price", None), 0.0)
    size = _safe_float_lifecycle(
        getattr(
            state.s2_position,
            "position_size",
            getattr(state.s2_position, "size", 0.0),
        ),
        0.0,
    )
    entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()

    if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
        return

    duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)

    if duration_sec < 900.0:
        return

    if int(duration_sec) % 300 != 0:
        return

    current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
    if side == "long":
        unrealized_pnl = (current_price - entry_price) * size
    else:
        unrealized_pnl = (entry_price - current_price) * size

    out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fieldnames = [
        "timestamp_utc",
        "tick",
        "snapshot_id",
        "side",
        "duration_sec",
        "entry_timestamp_utc",
        "entry_price",
        "current_price",
        "position_size",
        "unrealized_pnl",
        "current_score",
        "market_regime",
        "atr_quality",
        "ma200_signal",
        "atr_signal",
        "mfi_signal",
    ]

    write_header = not os.path.isfile(out_path)

    with open(out_path, "a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp_utc": timestamp_utc,
                "tick": int(tick_id),
                "snapshot_id": snapshot_id,
                "side": side,
                "duration_sec": float(duration_sec),
                "entry_timestamp_utc": entry_ts,
                "entry_price": float(entry_price),
                "current_price": float(current_price),
                "position_size": float(size),
                "unrealized_pnl": float(unrealized_pnl),
                "current_score": int(getattr(regime, "score", 0)),
                "market_regime": str(getattr(regime, "label", "")),
                "atr_quality": str(getattr(regime, "risk_label", "")),
                "ma200_signal": int(getattr(regime, "ma200_signal", 0)),
                "atr_signal": int(getattr(regime, "atr_signal", 0)),
                "mfi_signal": int(getattr(regime, "mfi_signal", 0)),
            }
        )



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
            regime = detect_regime(features)

            current_position = "FLAT"
            if hasattr(state, "s2_position") and hasattr(state.s2_position, "position"):
                current_position = str(state.s2_position.position).strip().upper()

            intent_1m_raw, forced = compute_1m_intent_raw(
                cfg=cfg,
                tick_id=tick.tick_id,
                features=features,
                current_position=current_position,
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
                current_position=current_position,
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
                category="REGIME",
                event="regime_snapshot",
                severity="INFO",
                system_state_id=state.system_state_id,
                fields={
                    "tick": tick.tick_id,
                    "snapshot_id": features.snapshot_id,
                    "timestamp_utc": features.timestamp_utc,
                    "regime_label": regime.label,
                    "risk_label": regime.risk_label,
                    "ma200_signal": regime.ma200_signal,
                    "atr_signal": regime.atr_signal,
                    "mfi_signal": regime.mfi_signal,
                    "entry_score": regime.score,
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
                    "current_position": fused.current_position,
                    "test_forced_intent": int(forced),
                    "thresh": cfg.thresh_5m,
                    "vote_5m_direction": vote_v1.direction,
                    "vote_5m_seed_id": str(vote_v1.seed_id),
                    "vote_5m_strength": float(vote_v1.strength),
                },
            )

            _append_trade_lifecycle_snapshot(
                repo_root=repo_root,
                tick_id=tick.tick_id,
                timestamp_utc=str(features.timestamp_utc),
                snapshot_id=str(features.snapshot_id),
                state=state,
                features=features,
                regime=regime,
            )

            _append_passive_shadow_risk_snapshot(
                repo_root=repo_root,
                tick_id=tick.tick_id,
                timestamp_utc=str(features.timestamp_utc),
                snapshot_id=str(features.snapshot_id),
                state=state,
                features=features,
                regime=regime,
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