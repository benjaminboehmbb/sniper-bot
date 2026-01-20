#!/usr/bin/env python3
# live_l1/core/loop.py
#
# L1 core loop with 5m timing vote fusion + optional forced 1m intents for L1-C validation.
# L1-D: optional v2 shadow timing (compare logging only; no behavior change).
# ASCII-only.

from __future__ import annotations

import os
import time
import uuid
import csv
import ast
from dataclasses import dataclass
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional, Deque, Tuple, List, Dict, Any

from live_l1.logs.logger import L1Logger
from live_l1.io.market import DummyMarketFeed, MarketSnapshot
from live_l1.io.validate import validate_snapshot, ValidationResult
from live_l1.core.intent import make_hold_intent, Intent
from live_l1.core.intent_fusion import (
    merge_intent_with_5m_vote,
    format_timing_compare_log,
    TimingVote as FusionTimingVote,
)
from live_l1.core.execution import attempt_execution, ExecutionResult
from live_l1.state.models import PositionStateS2, RiskStateS4
from live_l1.state.persist import _atomic_append_jsonl
from live_l1.guards.cost_guards import GuardMetrics, evaluate_cost_guards


@dataclass(frozen=True)
class RuntimeConfig:
    repo_root: str
    decision_tick_seconds: float
    log_path: str
    symbol: str
    invalid_every: int

    state_path_s2: str
    state_path_s4: str

    gate_mode: str
    fee_roundtrip: float
    trades_window_hours: int

    # 5m vote config (v1 seeds)
    seeds_5m_csv: str
    thresh_5m: float

    # L1-D shadow (v2)
    timing_v2_shadow: bool
    timing_v2_history_len: int

    # L1-C test mode
    test_force_intents: bool
    test_force_buy_every: int
    test_force_sell_every: int
    test_force_warmup_ticks: int


@dataclass
class LiveState:
    system_state_id: str
    kill_level: str
    is_running: bool
    data_valid: bool

    guard_last_reason: str
    guard_disable_until_utc: str

    trades_today: int
    trades_6h: int
    net_pnl_today_est: float
    last_trade_ts_utc: str

    day_utc_yyyy_mm_dd: str


def _env_float(name: str, default: float) -> float:
    v = os.environ.get(name, "")
    try:
        return float(v) if v else float(default)
    except Exception:
        return float(default)


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name, "")
    try:
        return int(v) if v else int(default)
    except Exception:
        return int(default)


def _env_str(name: str, default: str) -> str:
    v = os.environ.get(name, "")
    return v if v else default


def _env_bool01(name: str, default: int = 0) -> bool:
    v = os.environ.get(name, "")
    if v == "":
        return bool(default)
    return v.strip() == "1"


def load_runtime_config(repo_root: str) -> RuntimeConfig:
    tick = _env_float("L1_DECISION_TICK_SECONDS", 1.0)
    log_path = _env_str("L1_LOG_PATH", os.path.join(repo_root, "live_logs", "l1_paper.log"))
    symbol = _env_str("L1_SYMBOL", "BTCUSDT")
    invalid_every = _env_int("L1_DUMMY_INVALID_EVERY", 0)

    gate_mode = _env_str("L1_GATE_MODE", "auto").strip().lower()
    fee_roundtrip = _env_float("L1_FEE_ROUNDTRIP", 0.0004)
    trades_window_hours = _env_int("L1_TRADES_WINDOW_HOURS", 6)

    # Seeds: allow both names; CLI will set SEEDS_5M_CSV
    seeds_5m_csv = _env_str(
        "SEEDS_5M_CSV",
        _env_str("L1_5M_SEEDS_CSV", "seeds/5m/btcusdt_5m_long_timing_core_v1.csv"),
    )

    # Threshold: allow both names; CLI will set THRESH_5M
    thresh_5m = _env_float("THRESH_5M", _env_float("L1_5M_THRESH", 0.60))

    # L1-D shadow timing v2
    timing_v2_shadow = _env_bool01("L1_TIMING_V2_SHADOW", 1)
    timing_v2_history_len = _env_int("L1_TIMING_V2_HISTORY_LEN", 3)

    # Test forcing
    test_force_intents = _env_bool01("L1_TEST_FORCE_INTENTS", 0)
    test_force_buy_every = _env_int("L1_TEST_FORCE_BUY_EVERY", 10)
    test_force_sell_every = _env_int("L1_TEST_FORCE_SELL_EVERY", 15)
    test_force_warmup_ticks = _env_int("L1_TEST_FORCE_WARMUP_TICKS", 0)

    return RuntimeConfig(
        repo_root=repo_root,
        decision_tick_seconds=tick,
        log_path=log_path,
        symbol=symbol,
        invalid_every=invalid_every,
        state_path_s2=os.path.join(repo_root, "live_state", "s2_position.jsonl"),
        state_path_s4=os.path.join(repo_root, "live_state", "s4_risk.jsonl"),
        gate_mode=gate_mode,
        fee_roundtrip=fee_roundtrip,
        trades_window_hours=trades_window_hours,
        seeds_5m_csv=seeds_5m_csv,
        thresh_5m=thresh_5m,
        timing_v2_shadow=timing_v2_shadow,
        timing_v2_history_len=timing_v2_history_len,
        test_force_intents=test_force_intents,
        test_force_buy_every=test_force_buy_every,
        test_force_sell_every=test_force_sell_every,
        test_force_warmup_ticks=test_force_warmup_ticks,
    )


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _utc_day_str(ts: datetime) -> str:
    d = ts.date()
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"


def _parse_iso_utc(ts: str) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _safe_intent_kind(intent: Intent) -> str:
    for attr in ("intent_type", "type", "action", "kind", "name"):
        if hasattr(intent, attr):
            try:
                v = getattr(intent, attr)
                return str(v) if v is not None else ""
            except Exception:
                return ""
    return intent.__class__.__name__


def _is_trade_executed(er: ExecutionResult) -> bool:
    for attr in ("executed", "filled", "is_filled", "did_execute", "success"):
        if hasattr(er, attr):
            try:
                v = getattr(er, attr)
                if isinstance(v, bool):
                    return v
            except Exception:
                pass

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

    return False


def _roll_trades_window(trade_ts: Deque[datetime], now: datetime, window_hours: int) -> int:
    cutoff = now - timedelta(hours=window_hours)
    while trade_ts and trade_ts[0] < cutoff:
        trade_ts.popleft()
    return len(trade_ts)


def _compute_forced_intent_1m_raw(cfg: RuntimeConfig, tick_id: int) -> Tuple[str, int]:
    if not cfg.test_force_intents:
        return "HOLD", 0
    if tick_id <= cfg.test_force_warmup_ticks:
        return "HOLD", 0

    sell_every = max(1, int(cfg.test_force_sell_every))
    buy_every = max(1, int(cfg.test_force_buy_every))

    # priority: SELL then BUY
    if tick_id % sell_every == 0:
        return "SELL", 1
    if tick_id % buy_every == 0:
        return "BUY", 1
    return "HOLD", 0


def _infer_default_dir_from_path(path_csv: str) -> str:
    p = (path_csv or "").lower()
    if "short" in p:
        return "short"
    if "long" in p:
        return "long"
    return "long"


def _load_v2_seeds_from_csv(path_csv: str) -> List[Any]:
    """
    Load v1-style seed CSV (seed_id, comb_json) into timing_5m_v2.GSSpec list.

    v2 expects direction per seed. We support:
      - comb_json contains 'dir' (preferred)
      - if missing, infer default from filename (long/short) and use that
    """
    seeds: List[Any] = []
    try:
        from live_l1.core.timing_5m_v2 import GSSpec
    except Exception:
        return seeds

    default_dir = _infer_default_dir_from_path(path_csv)

    try:
        with open(path_csv, "r", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                seed_id = str(row.get("seed_id", "")).strip()
                comb_raw = row.get("comb_json", "")
                if not seed_id or not comb_raw:
                    continue

                try:
                    comb = ast.literal_eval(comb_raw)
                except Exception:
                    continue

                if not isinstance(comb, dict):
                    continue

                d = str(comb.get("dir", "")).strip().lower()
                if d not in ("long", "short"):
                    d = default_dir

                weights: Dict[str, float] = {}
                for k, v in comb.items():
                    if k == "dir":
                        continue
                    try:
                        weights[str(k)] = float(v)
                    except Exception:
                        continue

                seeds.append(GSSpec(seed_id=seed_id, direction=d, weights=weights))
    except Exception:
        return []

    return seeds


def _build_5m_candles_from_prices(prices_1m: Deque[float], candles_5m: Deque[Any]) -> None:
    """
    Deterministic dummy aggregation:
      - every 5 ticks -> one 5m candle
      - volume is synthetic (count of points)
    """
    if len(prices_1m) < 5:
        return

    try:
        from live_l1.core.timing_5m_v2 import Candle5m
    except Exception:
        return

    chunk: List[float] = []
    for _ in range(5):
        if prices_1m:
            chunk.append(prices_1m.popleft())

    if len(chunk) != 5:
        return

    o = chunk[0]
    c = chunk[-1]
    h = max(chunk)
    l = min(chunk)
    vol = float(len(chunk))
    ts_open_utc = _now_utc().isoformat()

    candles_5m.append(Candle5m(ts_open_utc=ts_open_utc, open=o, high=h, low=l, close=c, volume=vol))


def run_l1_loop_step1234567(repo_root: str, max_ticks: int = 6) -> int:
    system_state_id = f"L1P-{uuid.uuid4().hex[:11]}"
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

    trade_ts_window: Deque[datetime] = deque()
    feed = DummyMarketFeed(symbol=cfg.symbol, invalid_every=cfg.invalid_every)

    # Shadow v2 state
    v2_seeds: List[Any] = []
    prices_1m_buf: Deque[float] = deque()
    candles_5m_buf: Deque[Any] = deque(maxlen=64)

    if cfg.timing_v2_shadow:
        v2_seeds = _load_v2_seeds_from_csv(cfg.seeds_5m_csv)
        log.log(
            category="L1",
            event="timing_v2_shadow_init",
            severity=("INFO" if len(v2_seeds) > 0 else "WARN"),
            system_state_id=state.system_state_id,
            fields={
                "enabled": 1,
                "seeds_csv": cfg.seeds_5m_csv,
                "num_seeds_loaded": len(v2_seeds),
                "history_len": cfg.timing_v2_history_len,
                "default_dir": _infer_default_dir_from_path(cfg.seeds_5m_csv),
            },
        )

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
            "seeds_5m_csv": cfg.seeds_5m_csv,
            "thresh_5m": cfg.thresh_5m,
            "timing_v2_shadow": int(cfg.timing_v2_shadow),
            "timing_v2_history_len": cfg.timing_v2_history_len,
            "test_force_intents": int(cfg.test_force_intents),
            "test_force_buy_every": cfg.test_force_buy_every,
            "test_force_sell_every": cfg.test_force_sell_every,
            "test_force_warmup_ticks": cfg.test_force_warmup_ticks,
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

            # Shadow aggregation buffer
            try:
                prices_1m_buf.append(float(snap.price))
            except Exception:
                pass

            # Every 5 ticks build a synthetic 5m candle
            if cfg.timing_v2_shadow and len(prices_1m_buf) >= 5:
                _build_5m_candles_from_prices(prices_1m_buf, candles_5m_buf)

            vr: ValidationResult = validate_snapshot(snap)
            state.data_valid = bool(vr.data_valid)
            log.log(
                category="L2",
                event=("data_valid" if state.data_valid else "data_invalid"),
                severity=("INFO" if state.data_valid else "WARN"),
                system_state_id=state.system_state_id,
                fields={"snapshot_id": snap.snapshot_id},
            )

            intent: Optional[Intent] = None
            fusion = None

            if state.data_valid:
                intent = make_hold_intent()
                log.log(
                    category="L3",
                    event="intent_created",
                    severity="INFO",
                    system_state_id=state.system_state_id,
                    intent_id=getattr(intent, "intent_id", ""),
                    fields={"snapshot_id": snap.snapshot_id, "intent_kind": _safe_intent_kind(intent)},
                )

                # Derive raw intent (default HOLD)
                kind = _safe_intent_kind(intent).upper()
                if "BUY" in kind:
                    intent_1m_raw = "BUY"
                elif "SELL" in kind:
                    intent_1m_raw = "SELL"
                else:
                    intent_1m_raw = "HOLD"

                # Forced intent override for L1-C validation
                forced_intent, is_forced = _compute_forced_intent_1m_raw(cfg, ticks)
                if is_forced:
                    intent_1m_raw = forced_intent

                # 5m vote v1 (authoritative)
                from live_l1.core.timing_5m import compute_5m_timing_vote

                timing_vote_v1 = compute_5m_timing_vote(
                    repo_root=cfg.repo_root,
                    symbol=cfg.symbol,
                    seeds_csv=cfg.seeds_5m_csv,
                    now_utc=now.isoformat(),
                )

                # 5m vote v2 (shadow only)
                shadow_vote: Optional[FusionTimingVote] = None
                if (
                    cfg.timing_v2_shadow
                    and len(v2_seeds) > 0
                    and len(candles_5m_buf) >= max(1, cfg.timing_v2_history_len)
                ):
                    try:
                        from live_l1.core.timing_5m_v2 import compute_5m_timing_vote_v2
                        v2_vote = compute_5m_timing_vote_v2(
                            repo_root=cfg.repo_root,
                            symbol=cfg.symbol,
                            now_utc=now.isoformat(),
                            candles_5m=list(candles_5m_buf),
                            seeds=v2_seeds,
                            thresh=cfg.thresh_5m,
                            history_len=cfg.timing_v2_history_len,
                            dynamic_thresh=True,
                        )
                        shadow_vote = FusionTimingVote(
                            direction=v2_vote.direction,
                            strength=float(v2_vote.strength),
                            seed_id=v2_vote.seed_id,
                        )
                    except Exception:
                        shadow_vote = None

                # Fusion (v1 authoritative; v2 shadow only)
                fusion = merge_intent_with_5m_vote(
                    intent_1m_raw=intent_1m_raw,
                    vote=timing_vote_v1,
                    allow_long=1,
                    allow_short=1,
                    thresh=cfg.thresh_5m,
                    shadow_vote=shadow_vote,
                    shadow_tag="v2",
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
                        "test_forced_intent": is_forced,
                        "timing_v2_shadow": int(cfg.timing_v2_shadow),
                    },
                )

                # Shadow compare log event (no behavior impact)
                if cfg.timing_v2_shadow and shadow_vote is not None:
                    compare_line = format_timing_compare_log(fusion)
                    log.log(
                        category="L3",
                        event="timing_compare",
                        severity="INFO",
                        system_state_id=state.system_state_id,
                        intent_id=getattr(intent, "intent_id", ""),
                        fields={
                            "compare": compare_line,
                            "v1_dir": fusion.vote_5m_direction,
                            "v1_strength": fusion.vote_5m_strength,
                            "v1_seed_id": fusion.vote_5m_seed_id,
                            "v2_dir": fusion.shadow_vote_direction,
                            "v2_strength": fusion.shadow_vote_strength,
                            "v2_seed_id": fusion.shadow_vote_seed_id,
                            "v2_history_len": cfg.timing_v2_history_len,
                            "candles_5m_buf_len": len(candles_5m_buf),
                        },
                    )

            # Rolling trades window
            state.trades_6h = _roll_trades_window(trade_ts_window, now, cfg.trades_window_hours)

            # Guards
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
                    severity=("ERROR" if gd.reason in ("FEE_CONFIG_MISMATCH", "GATE_MODE_NOT_AUTO") else "WARN" if gd.reason != "OK" else "INFO"),
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

            # Execution attempt (still stub)
            if gd.allow_entry and intent is not None and fusion is not None:
                er: ExecutionResult = attempt_execution(intent)
                executed = _is_trade_executed(er)

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
                    state.trades_today += 1
                    trade_ts_window.append(now)
                    state.trades_6h = _roll_trades_window(trade_ts_window, now, cfg.trades_window_hours)
                    state.last_trade_ts_utc = now.isoformat()

                    for attr in ("pnl_net", "pnl", "net_pnl", "pnl_est"):
                        if hasattr(er, attr):
                            try:
                                v = float(getattr(er, attr))
                                state.net_pnl_today_est += v
                                break
                            except Exception:
                                pass

            # State update + persist
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

            _atomic_append_jsonl(
                cfg.state_path_s2,
                {"system_state_id": system_state_id, "symbol": s2.symbol, "position": s2.position, "size": s2.size},
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

            # Delay
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















