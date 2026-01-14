#!/usr/bin/env python3
# live_l1/guards/cost_guards.py
#
# Purpose:
#   Deterministic cost & overtrading guards for L1 paper/live trading.
#   Read-only with respect to GS engine. Guards act as a permission layer
#   BEFORE entry intents are created.
#
# Design principles:
#   - deterministic
#   - ASCII-only
#   - no side effects
#   - exits are ALWAYS allowed
#   - entries may be blocked
#
# Status:
#   L1-ready, baseline implementation

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict


# -------------------------
# Config (start conservative)
# -------------------------

FEE_ROUNDTRIP_ASSUMED = 0.0004

MAX_TRADES_PER_DAY = 400
MAX_TRADES_PER_6H = 140

COOLDOWN_MINUTES = 3

FEE_BUDGET_DAY = 0.12          # ROI-units (GS notation)
DAILY_NET_FLOOR = -0.20        # stop if worse than this
MIN_TRADES_FOR_NET_CHECK = 60


# -------------------------
# State snapshot (input)
# -------------------------

@dataclass(frozen=True)
class GuardMetrics:
    now_utc: datetime

    trades_today: int
    trades_6h: int

    net_pnl_today_est: float

    last_trade_ts_utc: Optional[datetime]

    gate_mode: str               # expected: "auto"
    fee_roundtrip_configured: float


# -------------------------
# Decision (output)
# -------------------------

@dataclass(frozen=True)
class GuardDecision:
    allow_entry: bool
    allow_exit: bool
    reason: str
    disable_until: Optional[datetime]


# -------------------------
# Guard evaluation
# -------------------------

def evaluate_cost_guards(m: GuardMetrics) -> GuardDecision:
    """
    Evaluate all cost / churn guards in deterministic priority order.
    """

    now = m.now_utc

    # -----------------
    # Guard E: Integrity
    # -----------------

    if abs(m.fee_roundtrip_configured - FEE_ROUNDTRIP_ASSUMED) > 0.00002:
        return GuardDecision(
            allow_entry=False,
            allow_exit=True,
            reason="FEE_CONFIG_MISMATCH",
            disable_until=None,
        )

    if m.gate_mode != "auto":
        return GuardDecision(
            allow_entry=False,
            allow_exit=True,
            reason="GATE_MODE_NOT_AUTO",
            disable_until=None,
        )

    # -----------------
    # Guard A1: Daily cap
    # -----------------

    if m.trades_today >= MAX_TRADES_PER_DAY:
        disable_until = _next_utc_midnight(now)
        return GuardDecision(
            allow_entry=False,
            allow_exit=True,
            reason="MAX_TRADES_PER_DAY_REACHED",
            disable_until=disable_until,
        )

    # -----------------
    # Guard C: Fee budget
    # -----------------

    fee_paid_today_est = m.trades_today * FEE_ROUNDTRIP_ASSUMED
    if fee_paid_today_est >= FEE_BUDGET_DAY:
        disable_until = _next_utc_midnight(now)
        return GuardDecision(
            allow_entry=False,
            allow_exit=True,
            reason="FEE_BUDGET_EXCEEDED",
            disable_until=disable_until,
        )

    # -----------------
    # Guard D: Net loss stop
    # -----------------

    if (
        m.trades_today >= MIN_TRADES_FOR_NET_CHECK
        and m.net_pnl_today_est <= DAILY_NET_FLOOR
    ):
        disable_until = _next_utc_midnight(now)
        return GuardDecision(
            allow_entry=False,
            allow_exit=True,
            reason="DAILY_NET_LOSS_EXCEEDED",
            disable_until=disable_until,
        )

    # -----------------
    # Guard A2: 6h rate cap
    # -----------------

    if m.trades_6h >= MAX_TRADES_PER_6H:
        disable_until = now + timedelta(minutes=60)
        return GuardDecision(
            allow_entry=False,
            allow_exit=True,
            reason="MAX_TRADES_6H_REACHED",
            disable_until=disable_until,
        )

    # -----------------
    # Guard B: Cooldown
    # -----------------

    if m.last_trade_ts_utc is not None:
        if now < m.last_trade_ts_utc + timedelta(minutes=COOLDOWN_MINUTES):
            return GuardDecision(
                allow_entry=False,
                allow_exit=True,
                reason="COOLDOWN_ACTIVE",
                disable_until=m.last_trade_ts_utc + timedelta(minutes=COOLDOWN_MINUTES),
            )

    # -----------------
    # All clear
    # -----------------

    return GuardDecision(
        allow_entry=True,
        allow_exit=True,
        reason="OK",
        disable_until=None,
    )


# -------------------------
# Helpers
# -------------------------

def _next_utc_midnight(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    next_day = ts.date() + timedelta(days=1)
    return datetime(
        year=next_day.year,
        month=next_day.month,
        day=next_day.day,
        tzinfo=timezone.utc,
    )
