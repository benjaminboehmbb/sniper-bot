#!/usr/bin/env python3
# live_l1/io/valid.py
# RuntimeConfig validation for L1 loop.
# ASCII-only.

from __future__ import annotations

import os


def validate_runtime_config(cfg) -> None:
    required_attrs = [
        "repo_root",
        "log_path",
        "state_dir",
        "symbol",
        "gate_mode",
        "fee_roundtrip",
        "decision_tick_seconds",
        "trades_window_hours",
        "test_force_intents",
        "test_force_buy_every",
        "test_force_sell_every",
        "test_force_warmup_ticks",
        "market_csv_path",
        "seeds_5m_csv",
        "thresh_5m",
        "timing_v2_shadow",
        "timing_v2_history_len",
    ]

    for name in required_attrs:
        if not hasattr(cfg, name):
            raise TypeError(f"RuntimeConfig missing required attribute: {name}")

    repo_root = str(cfg.repo_root).strip()
    log_path = str(cfg.log_path).strip()
    state_dir = str(cfg.state_dir).strip()
    symbol = str(cfg.symbol).strip()
    gate_mode = str(cfg.gate_mode).strip().lower()
    market_csv_path = str(cfg.market_csv_path).strip()
    seeds_5m_csv = str(cfg.seeds_5m_csv).strip()

    if not repo_root:
        raise ValueError("repo_root must not be empty")
    if not log_path:
        raise ValueError("log_path must not be empty")
    if not state_dir:
        raise ValueError("state_dir must not be empty")
    if not symbol:
        raise ValueError("symbol must not be empty")
    if not market_csv_path:
        raise ValueError("market_csv_path must not be empty")
    if not seeds_5m_csv:
        raise ValueError("seeds_5m_csv must not be empty")

    if not os.path.isdir(repo_root):
        raise ValueError(f"repo_root does not exist or is not a directory: {repo_root}")

    log_dir = os.path.dirname(log_path) or "."
    if not os.path.isdir(log_dir):
        raise ValueError(f"log directory does not exist: {log_dir}")

    if not os.path.isdir(state_dir):
        raise ValueError(f"state_dir does not exist: {state_dir}")

    if os.path.isabs(market_csv_path):
        market_path = market_csv_path
    else:
        market_path = os.path.join(repo_root, market_csv_path)

    if not os.path.isfile(market_path):
        raise ValueError(f"market_csv_path not found: {market_path}")

    if os.path.isabs(seeds_5m_csv):
        seeds_path = seeds_5m_csv
    else:
        seeds_path = os.path.join(repo_root, seeds_5m_csv)

    if not os.path.isfile(seeds_path):
        raise ValueError(f"seeds_5m_csv not found: {seeds_path}")

    allowed_gate_modes = {"auto", "open", "closed"}
    if gate_mode not in allowed_gate_modes:
        raise ValueError(f"gate_mode must be one of {sorted(allowed_gate_modes)}, got: {cfg.gate_mode}")

    fee_roundtrip = float(cfg.fee_roundtrip)
    if fee_roundtrip < 0.0 or fee_roundtrip > 1.0:
        raise ValueError("fee_roundtrip must be in [0.0, 1.0]")

    decision_tick_seconds = float(cfg.decision_tick_seconds)
    if decision_tick_seconds < 0.0:
        raise ValueError("decision_tick_seconds must be >= 0")

    trades_window_hours = int(cfg.trades_window_hours)
    if trades_window_hours < 1:
        raise ValueError("trades_window_hours must be >= 1")

    thresh_5m = float(cfg.thresh_5m)
    if thresh_5m < 0.0 or thresh_5m > 1.0:
        raise ValueError("thresh_5m must be in [0.0, 1.0]")

    test_force_buy_every = int(cfg.test_force_buy_every)
    if test_force_buy_every < 0:
        raise ValueError("test_force_buy_every must be >= 0")

    test_force_sell_every = int(cfg.test_force_sell_every)
    if test_force_sell_every < 0:
        raise ValueError("test_force_sell_every must be >= 0")

    test_force_warmup_ticks = int(cfg.test_force_warmup_ticks)
    if test_force_warmup_ticks < 0:
        raise ValueError("test_force_warmup_ticks must be >= 0")

    timing_v2_history_len = int(cfg.timing_v2_history_len)
    if timing_v2_history_len < 1:
        raise ValueError("timing_v2_history_len must be >= 1")