# P25B CANDIDATE CONTENT INSPECTION

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## live_l1/io/validate.py

exists: True

line_count: 47

classification: ARCHIVE_CANDIDATE_STRONG

functions:

- validate_snapshot

classes:

- ValidationResult

imports:

- __future__
- dataclasses
- live_l1.io.market
- typing

preview:

```text
# live_l1/io/validate.py
#
# L1 Data Validation (Step 2/8)
# - Setzt data_valid True/False
# - Keine Heuristik, nur harte Kriterien
# - Deterministisch, explainable, loggable
#
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from live_l1.io.market import MarketSnapshot


@dataclass(frozen=True)
class ValidationResult:
    data_valid: bool
    reasons: List[str]


def validate_snapshot(s: MarketSnapshot) -> ValidationResult:
    reasons: List[str] = []
```

## live_l1/core/gate_builder.py

exists: True

line_count: 31

classification: CONTENT_PRESENT_REVIEW_REQUIRED

functions:

- build_online_gates

classes:

- GateDecision

imports:

- __future__
- dataclasses

preview:

```text
#!/usr/bin/env python3
# live_l1/core/gate_builder.py
# Online allow gate builder for Live L1.
# Source of Truth from data/l1_full_run.csv:
# allow_long  = (regime_v1 == 1)
# allow_short = (regime_v1 == -1)
# ASCII-only.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateDecision:
    allow_long: int
    allow_short: int
    regime_v1: int


def build_online_gates(regime_v1: int) -> GateDecision:
    r = int(regime_v1)

    allow_long = int(r == 1)
    allow_short = int(r == -1)
```

## live_l1/core/regime_builder.py

exists: True

line_count: 50

classification: CONTENT_PRESENT_REVIEW_REQUIRED

functions:

- build_online_regime
- build_regime_frame

classes:

- none

imports:

- __future__
- pandas

preview:

```text
#!/usr/bin/env python3
# live_l1/core/regime_builder.py
# Online regime_v1 builder for Live L1.
# ASCII-only.

from __future__ import annotations

import pandas as pd

MIN_ROWS = 1640


def build_regime_frame(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required = ["close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError("Missing required columns: " + ",".join(missing))

    if len(df) < MIN_ROWS:
        raise ValueError(f"Need at least {MIN_ROWS} rows, got {len(df)}")

    out = df.copy()
```

## live_l1/core/regime_v2_builder.py

exists: True

line_count: 68

classification: CONTENT_PRESENT_REVIEW_REQUIRED

functions:

- build_regime_v2

classes:

- none

imports:

- __future__
- numpy

preview:

```text
#!/usr/bin/env python3
# live_l1/core/regime_v2_builder.py
# Source of Truth:
# tools/build_regime_v2_from_v1.py

from __future__ import annotations

import numpy as np


DEFAULT_MIN_STATE_BARS = 720


def build_regime_v2(
    regime_v1,
    min_state_bars: int = DEFAULT_MIN_STATE_BARS,
    no_direct_flip: bool = False,
):
    v1 = np.asarray(regime_v1, dtype=float)

    if v1.size == 0:
        return np.array([], dtype=np.int8)

    vv = np.where(v1 > 0, 1, np.where(v1 < 0, -1, 0)).astype(np.int8)

```

## live_l1/core/signal_builder.py

exists: True

line_count: 217

classification: CONTENT_PRESENT_REVIEW_REQUIRED

functions:

- _adx
- _atr
- _bollinger_z
- _cci
- _macd_hist
- _mfi
- _obv
- _roc
- _rsi
- _safe_ewm
- _stoch_k
- _to_live_int
- _to_signal_score
- _validate_input
- build_online_signals
- build_signal_frame

classes:

- none

imports:

- __future__
- numpy
- pandas

preview:

```text
#!/usr/bin/env python3
# live_l1/core/signal_builder.py
# Online GS-compatible 1m signal builder for Live L1.
# ASCII-only.

from __future__ import annotations

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["timestamp_utc", "open", "high", "low", "close", "volume"]

SIGNAL_COLUMNS = [
    "rsi_signal",
    "macd_signal",
    "bollinger_signal",
    "ma200_signal",
    "stoch_signal",
    "atr_signal",
    "ema50_signal",
    "adx_signal",
    "cci_signal",
    "mfi_signal",
    "obv_signal",
```

## live_l1/guards/cost_guards.py

exists: True

line_count: 196

classification: CONTENT_PRESENT_REVIEW_REQUIRED

functions:

- _next_utc_midnight
- evaluate_cost_guards

classes:

- GuardDecision
- GuardMetrics

imports:

- dataclasses
- datetime
- typing

preview:

```text
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
```

## live_l1/core/timing_5m_v2.py

exists: True

line_count: 286

classification: KEEP_FUTURE_OR_EXPERIMENTAL_REVIEW

functions:

- _clamp01
- _compute_effective_thresh
- _evaluate_seed_on_window
- compute_5m_timing_vote_v2

classes:

- Candle5m
- GSSpec
- TimingVote

imports:

- __future__
- dataclasses
- typing

preview:

```text
# live_l1/core/timing_5m_v2.py
#
# L1-D: 5m Timing Core v2
# Step 6: Dynamic (volatility-aware) threshold on last N candles.
#
# No execution.
# No side effects.
# Deterministic.

from __future__ import annotations

from typing import List, Optional, Literal, Dict
from dataclasses import dataclass


VoteDir = Literal["long", "short", "none"]


@dataclass(frozen=True)
class TimingVote:
    direction: VoteDir
    strength: float
    seed_id: Optional[str] = None


```

## tools/test_timing_5m_v2_minimal.py

exists: True

line_count: 108

classification: KEEP_WITH_TIMING_5M_V2_OR_ARCHIVE_TOGETHER

functions:

- make_dummy_candle
- test_long_wins_on_bull_candle
- test_none_when_flat_candle
- test_short_wins_on_bear_candle

classes:

- none

imports:

- live_l1.core.timing_5m_v2
- os
- sys

preview:

```text
# tools/test_timing_5m_v2_minimal.py
#
# Minimal isolated test for timing_5m_v2.py
# With explicit sys.path fix for repo-root imports.
# ASCII-only.

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from live_l1.core.timing_5m_v2 import (
    compute_5m_timing_vote_v2,
    Candle5m,
    GSSpec,
)


def make_dummy_candle(open_p: float, close_p: float) -> Candle5m:
    return Candle5m(
        ts_open_utc="2026-01-20T12:00:00Z",
        open=float(open_p),
        high=max(float(open_p), float(close_p)),
```

