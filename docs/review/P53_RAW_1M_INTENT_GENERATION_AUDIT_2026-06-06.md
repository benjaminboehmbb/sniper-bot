# P53 RAW 1M INTENT GENERATION AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Audit why post-fix runtime segments produced timing long/short/none votes while intent_1m_raw remained HOLD.

## Background

P51 showed post-fix timing votes in runtime:

- long: 38
- short: 29
- none: 133

But final intent remained HOLD for all 200 audited ticks.

P52 confirmed that intent fusion preserves HOLD_RAW when intent_1m_raw is HOLD.

## Target: live_l1/core/intent.py

exists: True

### Context 1

```text
6: from __future__ import annotations
7: 
8: import json
9: import os
10: from dataclasses import dataclass, field
11: from typing import Literal, Tuple
12: 
13: from live_l1.core.feature_snapshot import FeatureSnapshot
14: 
15: 
16: IntentAction = Literal["BUY", "SELL", "HOLD"]
17: Position = Literal["FLAT", "LONG", "SHORT"]
18: 
19: ENTRY_COOLDOWN_NORMAL_TICKS = 120
20: ENTRY_COOLDOWN_BAD_ATR_TICKS = 200
21: 
22: 
23: @dataclass(frozen=True)
24: class Intent:
25:     action: IntentAction
26: 
27: 
28: @dataclass
29: class _IntentState:
30:     recent_scores: list[int] = field(default_factory=list)
31:     last_tick_id: int | None = None
32:     last_position: Position = "FLAT"
33:     last_flat_after_position_tick: int | None = None
34: 
```

### Context 2

```text
20: ENTRY_COOLDOWN_BAD_ATR_TICKS = 200
21: 
22: 
23: @dataclass(frozen=True)
24: class Intent:
25:     action: IntentAction
26: 
27: 
28: @dataclass
29: class _IntentState:
30:     recent_scores: list[int] = field(default_factory=list)
31:     last_tick_id: int | None = None
32:     last_position: Position = "FLAT"
33:     last_flat_after_position_tick: int | None = None
34: 
35: 
36: _STATE = _IntentState()
37: 
38: 
39: def make_hold_intent() -> Intent:
40:     return Intent(action="HOLD")
41: 
42: 
43: def reset_intent_state() -> None:
44:     _STATE.recent_scores = []
45:     _STATE.last_tick_id = None
46:     _STATE.last_position = "FLAT"
47:     _STATE.last_flat_after_position_tick = None
48: 
```

### Context 3

```text
30:     recent_scores: list[int] = field(default_factory=list)
31:     last_tick_id: int | None = None
32:     last_position: Position = "FLAT"
33:     last_flat_after_position_tick: int | None = None
34: 
35: 
36: _STATE = _IntentState()
37: 
38: 
39: def make_hold_intent() -> Intent:
40:     return Intent(action="HOLD")
41: 
42: 
43: def reset_intent_state() -> None:
44:     _STATE.recent_scores = []
45:     _STATE.last_tick_id = None
46:     _STATE.last_position = "FLAT"
47:     _STATE.last_flat_after_position_tick = None
48: 
49: 
50: def _load_l1_signal_weights() -> dict[str, float] | None:
51:     path = os.environ.get("L1_SIGNAL_WEIGHTS_JSON", "").strip()
52:     if path == "":
53:         return None
54:     try:
55:         with open(path, "r", encoding="utf-8") as f:
56:             obj = json.load(f)
57:         if not isinstance(obj, dict):
58:             return None
```

### Context 4

```text
34: 
35: 
36: _STATE = _IntentState()
37: 
38: 
39: def make_hold_intent() -> Intent:
40:     return Intent(action="HOLD")
41: 
42: 
43: def reset_intent_state() -> None:
44:     _STATE.recent_scores = []
45:     _STATE.last_tick_id = None
46:     _STATE.last_position = "FLAT"
47:     _STATE.last_flat_after_position_tick = None
48: 
49: 
50: def _load_l1_signal_weights() -> dict[str, float] | None:
51:     path = os.environ.get("L1_SIGNAL_WEIGHTS_JSON", "").strip()
52:     if path == "":
53:         return None
54:     try:
55:         with open(path, "r", encoding="utf-8") as f:
56:             obj = json.load(f)
57:         if not isinstance(obj, dict):
58:             return None
59:         out: dict[str, float] = {}
60:         for k, v in obj.items():
61:             try:
62:                 out[str(k)] = float(v)
```

### Context 5

```text
43: def reset_intent_state() -> None:
44:     _STATE.recent_scores = []
45:     _STATE.last_tick_id = None
46:     _STATE.last_position = "FLAT"
47:     _STATE.last_flat_after_position_tick = None
48: 
49: 
50: def _load_l1_signal_weights() -> dict[str, float] | None:
51:     path = os.environ.get("L1_SIGNAL_WEIGHTS_JSON", "").strip()
52:     if path == "":
53:         return None
54:     try:
55:         with open(path, "r", encoding="utf-8") as f:
56:             obj = json.load(f)
57:         if not isinstance(obj, dict):
58:             return None
59:         out: dict[str, float] = {}
60:         for k, v in obj.items():
61:             try:
62:                 out[str(k)] = float(v)
63:             except Exception:
64:                 continue
65:         return out if out else None
66:     except Exception:
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
```

### Context 6

```text
48: 
49: 
50: def _load_l1_signal_weights() -> dict[str, float] | None:
51:     path = os.environ.get("L1_SIGNAL_WEIGHTS_JSON", "").strip()
52:     if path == "":
53:         return None
54:     try:
55:         with open(path, "r", encoding="utf-8") as f:
56:             obj = json.load(f)
57:         if not isinstance(obj, dict):
58:             return None
59:         out: dict[str, float] = {}
60:         for k, v in obj.items():
61:             try:
62:                 out[str(k)] = float(v)
63:             except Exception:
64:                 continue
65:         return out if out else None
66:     except Exception:
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
```

### Context 7

```text
55:         with open(path, "r", encoding="utf-8") as f:
56:             obj = json.load(f)
57:         if not isinstance(obj, dict):
58:             return None
59:         out: dict[str, float] = {}
60:         for k, v in obj.items():
61:             try:
62:                 out[str(k)] = float(v)
63:             except Exception:
64:                 continue
65:         return out if out else None
66:     except Exception:
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
```

### Context 8

```text
57:         if not isinstance(obj, dict):
58:             return None
59:         out: dict[str, float] = {}
60:         for k, v in obj.items():
61:             try:
62:                 out[str(k)] = float(v)
63:             except Exception:
64:                 continue
65:         return out if out else None
66:     except Exception:
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
```

### Context 9

```text
60:         for k, v in obj.items():
61:             try:
62:                 out[str(k)] = float(v)
63:             except Exception:
64:                 continue
65:         return out if out else None
66:     except Exception:
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
```

### Context 10

```text
64:                 continue
65:         return out if out else None
66:     except Exception:
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
```

### Context 11

```text
65:         return out if out else None
66:     except Exception:
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
```

### Context 12

```text
66:     except Exception:
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
```

### Context 13

```text
67:         return None
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
```

### Context 14

```text
68: 
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
```

### Context 15

```text
69: 
70: def _normalize_score(features: FeatureSnapshot) -> int:
71:     try:
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
```

### Context 16

```text
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
```

### Context 17

```text
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
```

### Context 18

```text
80:         )
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
```

### Context 19

```text
81:     except Exception:
82:         return 0
83: 
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
```

### Context 20

```text
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
```

### Context 21

```text
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
```

### Context 22

```text
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
```

### Context 23

```text
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
```

### Context 24

```text
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
```

### Context 25

```text
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
```

### Context 26

```text
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
```

### Context 27

```text
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
```

### Context 28

```text
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
```

### Context 29

```text
104:     if len(_STATE.recent_scores) > 6:
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
```

### Context 30

```text
105:         _STATE.recent_scores.pop(0)
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
```

### Context 31

```text
106: 
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
```

### Context 32

```text
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
```

### Context 33

```text
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
```

### Context 34

```text
112: 
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
139: 
140: 
```

### Context 35

```text
113: 
114: def _last_n_all_le(n: int, threshold: int) -> bool:
115:     if len(_STATE.recent_scores) < n:
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
139: 
140: 
141: def _debug_enabled() -> bool:
```

### Context 36

```text
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
139: 
140: 
141: def _debug_enabled() -> bool:
142:     v = os.environ.get("L1_INTENT_DEBUG", "")
143:     return v.strip().lower() in ("1", "true", "yes", "on")
144: 
```

### Context 37

```text
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
139: 
140: 
141: def _debug_enabled() -> bool:
142:     v = os.environ.get("L1_INTENT_DEBUG", "")
143:     return v.strip().lower() in ("1", "true", "yes", "on")
144: 
145: 
146: def _debug_log_line(
147:     *,
```

### Context 38

```text
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
139: 
140: 
141: def _debug_enabled() -> bool:
142:     v = os.environ.get("L1_INTENT_DEBUG", "")
143:     return v.strip().lower() in ("1", "true", "yes", "on")
144: 
145: 
146: def _debug_log_line(
147:     *,
148:     tick_id: int,
```

### Context 39

```text
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
139: 
140: 
141: def _debug_enabled() -> bool:
142:     v = os.environ.get("L1_INTENT_DEBUG", "")
143:     return v.strip().lower() in ("1", "true", "yes", "on")
144: 
145: 
146: def _debug_log_line(
147:     *,
148:     tick_id: int,
149:     current_position: Position,
```

### Context 40

```text
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
139: 
140: 
141: def _debug_enabled() -> bool:
142:     v = os.environ.get("L1_INTENT_DEBUG", "")
143:     return v.strip().lower() in ("1", "true", "yes", "on")
144: 
145: 
146: def _debug_log_line(
147:     *,
148:     tick_id: int,
149:     current_position: Position,
150:     score: int,
151:     intent: IntentAction,
152:     forced: bool,
153:     atr_sig: int = 0,
154: ) -> None:
155:     if not _debug_enabled():
156:         return
157: 
158:     try:
159:         log_dir = os.path.join(os.getcwd(), "live_logs")
160:         os.makedirs(log_dir, exist_ok=True)
161:         path = os.path.join(log_dir, "intent_debug.log")
```

### Context 41

```text
140: 
141: def _debug_enabled() -> bool:
142:     v = os.environ.get("L1_INTENT_DEBUG", "")
143:     return v.strip().lower() in ("1", "true", "yes", "on")
144: 
145: 
146: def _debug_log_line(
147:     *,
148:     tick_id: int,
149:     current_position: Position,
150:     score: int,
151:     intent: IntentAction,
152:     forced: bool,
153:     atr_sig: int = 0,
154: ) -> None:
155:     if not _debug_enabled():
156:         return
157: 
158:     try:
159:         log_dir = os.path.join(os.getcwd(), "live_logs")
160:         os.makedirs(log_dir, exist_ok=True)
161:         path = os.path.join(log_dir, "intent_debug.log")
162:         with open(path, "a", encoding="utf-8") as f:
163:             f.write(
164:                 "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced} cooldown={cooldown} cooldown_ticks={cooldown_ticks} cooldown_last={cooldown_last} atr_sig={atr_sig}\n".format(
165:                     tick=tick_id,
166:                     pos=current_position,
167:                     score=score,
168:                     recent=list(_STATE.recent_scores),
```

### Context 42

```text
146: def _debug_log_line(
147:     *,
148:     tick_id: int,
149:     current_position: Position,
150:     score: int,
151:     intent: IntentAction,
152:     forced: bool,
153:     atr_sig: int = 0,
154: ) -> None:
155:     if not _debug_enabled():
156:         return
157: 
158:     try:
159:         log_dir = os.path.join(os.getcwd(), "live_logs")
160:         os.makedirs(log_dir, exist_ok=True)
161:         path = os.path.join(log_dir, "intent_debug.log")
162:         with open(path, "a", encoding="utf-8") as f:
163:             f.write(
164:                 "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced} cooldown={cooldown} cooldown_ticks={cooldown_ticks} cooldown_last={cooldown_last} atr_sig={atr_sig}\n".format(
165:                     tick=tick_id,
166:                     pos=current_position,
167:                     score=score,
168:                     recent=list(_STATE.recent_scores),
169:                     intent=intent,
170:                     forced=int(forced),
171:                     cooldown=int(_in_entry_cooldown(tick_id, atr_sig)),
172:                     cooldown_ticks=_entry_cooldown_ticks(atr_sig),
173:                     cooldown_last=_STATE.last_flat_after_position_tick,
174:                     atr_sig=int(atr_sig),
```

### Context 43

```text
154: ) -> None:
155:     if not _debug_enabled():
156:         return
157: 
158:     try:
159:         log_dir = os.path.join(os.getcwd(), "live_logs")
160:         os.makedirs(log_dir, exist_ok=True)
161:         path = os.path.join(log_dir, "intent_debug.log")
162:         with open(path, "a", encoding="utf-8") as f:
163:             f.write(
164:                 "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced} cooldown={cooldown} cooldown_ticks={cooldown_ticks} cooldown_last={cooldown_last} atr_sig={atr_sig}\n".format(
165:                     tick=tick_id,
166:                     pos=current_position,
167:                     score=score,
168:                     recent=list(_STATE.recent_scores),
169:                     intent=intent,
170:                     forced=int(forced),
171:                     cooldown=int(_in_entry_cooldown(tick_id, atr_sig)),
172:                     cooldown_ticks=_entry_cooldown_ticks(atr_sig),
173:                     cooldown_last=_STATE.last_flat_after_position_tick,
174:                     atr_sig=int(atr_sig),
175:                 )
176:             )
177:     except Exception:
178:         pass
179: 
180: 
181: def compute_1m_intent_raw(
182:     *,
```

### Context 44

```text
157: 
158:     try:
159:         log_dir = os.path.join(os.getcwd(), "live_logs")
160:         os.makedirs(log_dir, exist_ok=True)
161:         path = os.path.join(log_dir, "intent_debug.log")
162:         with open(path, "a", encoding="utf-8") as f:
163:             f.write(
164:                 "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced} cooldown={cooldown} cooldown_ticks={cooldown_ticks} cooldown_last={cooldown_last} atr_sig={atr_sig}\n".format(
165:                     tick=tick_id,
166:                     pos=current_position,
167:                     score=score,
168:                     recent=list(_STATE.recent_scores),
169:                     intent=intent,
170:                     forced=int(forced),
171:                     cooldown=int(_in_entry_cooldown(tick_id, atr_sig)),
172:                     cooldown_ticks=_entry_cooldown_ticks(atr_sig),
173:                     cooldown_last=_STATE.last_flat_after_position_tick,
174:                     atr_sig=int(atr_sig),
175:                 )
176:             )
177:     except Exception:
178:         pass
179: 
180: 
181: def compute_1m_intent_raw(
182:     *,
183:     cfg,
184:     tick_id: int,
185:     features: FeatureSnapshot,
```

### Context 45

```text
158:     try:
159:         log_dir = os.path.join(os.getcwd(), "live_logs")
160:         os.makedirs(log_dir, exist_ok=True)
161:         path = os.path.join(log_dir, "intent_debug.log")
162:         with open(path, "a", encoding="utf-8") as f:
163:             f.write(
164:                 "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced} cooldown={cooldown} cooldown_ticks={cooldown_ticks} cooldown_last={cooldown_last} atr_sig={atr_sig}\n".format(
165:                     tick=tick_id,
166:                     pos=current_position,
167:                     score=score,
168:                     recent=list(_STATE.recent_scores),
169:                     intent=intent,
170:                     forced=int(forced),
171:                     cooldown=int(_in_entry_cooldown(tick_id, atr_sig)),
172:                     cooldown_ticks=_entry_cooldown_ticks(atr_sig),
173:                     cooldown_last=_STATE.last_flat_after_position_tick,
174:                     atr_sig=int(atr_sig),
175:                 )
176:             )
177:     except Exception:
178:         pass
179: 
180: 
181: def compute_1m_intent_raw(
182:     *,
183:     cfg,
184:     tick_id: int,
185:     features: FeatureSnapshot,
186:     current_position: str = "FLAT",
```

### Context 46

```text
161:         path = os.path.join(log_dir, "intent_debug.log")
162:         with open(path, "a", encoding="utf-8") as f:
163:             f.write(
164:                 "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced} cooldown={cooldown} cooldown_ticks={cooldown_ticks} cooldown_last={cooldown_last} atr_sig={atr_sig}\n".format(
165:                     tick=tick_id,
166:                     pos=current_position,
167:                     score=score,
168:                     recent=list(_STATE.recent_scores),
169:                     intent=intent,
170:                     forced=int(forced),
171:                     cooldown=int(_in_entry_cooldown(tick_id, atr_sig)),
172:                     cooldown_ticks=_entry_cooldown_ticks(atr_sig),
173:                     cooldown_last=_STATE.last_flat_after_position_tick,
174:                     atr_sig=int(atr_sig),
175:                 )
176:             )
177:     except Exception:
178:         pass
179: 
180: 
181: def compute_1m_intent_raw(
182:     *,
183:     cfg,
184:     tick_id: int,
185:     features: FeatureSnapshot,
186:     current_position: str = "FLAT",
187: ) -> Tuple[IntentAction, bool]:
188:     tick_id = int(tick_id)
189:     _maybe_reset_on_tick_reset(tick_id)
```

### Context 47

```text
162:         with open(path, "a", encoding="utf-8") as f:
163:             f.write(
164:                 "tick={tick} pos={pos} score={score} recent={recent} intent={intent} forced={forced} cooldown={cooldown} cooldown_ticks={cooldown_ticks} cooldown_last={cooldown_last} atr_sig={atr_sig}\n".format(
165:                     tick=tick_id,
166:                     pos=current_position,
167:                     score=score,
168:                     recent=list(_STATE.recent_scores),
169:                     intent=intent,
170:                     forced=int(forced),
171:                     cooldown=int(_in_entry_cooldown(tick_id, atr_sig)),
172:                     cooldown_ticks=_entry_cooldown_ticks(atr_sig),
173:                     cooldown_last=_STATE.last_flat_after_position_tick,
174:                     atr_sig=int(atr_sig),
175:                 )
176:             )
177:     except Exception:
178:         pass
179: 
180: 
181: def compute_1m_intent_raw(
182:     *,
183:     cfg,
184:     tick_id: int,
185:     features: FeatureSnapshot,
186:     current_position: str = "FLAT",
187: ) -> Tuple[IntentAction, bool]:
188:     tick_id = int(tick_id)
189:     _maybe_reset_on_tick_reset(tick_id)
190: 
```

### Context 48

```text
171:                     cooldown=int(_in_entry_cooldown(tick_id, atr_sig)),
172:                     cooldown_ticks=_entry_cooldown_ticks(atr_sig),
173:                     cooldown_last=_STATE.last_flat_after_position_tick,
174:                     atr_sig=int(atr_sig),
175:                 )
176:             )
177:     except Exception:
178:         pass
179: 
180: 
181: def compute_1m_intent_raw(
182:     *,
183:     cfg,
184:     tick_id: int,
185:     features: FeatureSnapshot,
186:     current_position: str = "FLAT",
187: ) -> Tuple[IntentAction, bool]:
188:     tick_id = int(tick_id)
189:     _maybe_reset_on_tick_reset(tick_id)
190: 
191:     warmup = int(getattr(cfg, "test_force_warmup_ticks", 0))
192:     if tick_id <= warmup:
193:         _STATE.last_tick_id = tick_id
194:         _STATE.recent_scores = []
195:         _STATE.last_position = "FLAT"
196:         _STATE.last_flat_after_position_tick = None
197:         _debug_log_line(
198:             tick_id=tick_id,
199:             current_position="FLAT",
```

### Context 49

```text
184:     tick_id: int,
185:     features: FeatureSnapshot,
186:     current_position: str = "FLAT",
187: ) -> Tuple[IntentAction, bool]:
188:     tick_id = int(tick_id)
189:     _maybe_reset_on_tick_reset(tick_id)
190: 
191:     warmup = int(getattr(cfg, "test_force_warmup_ticks", 0))
192:     if tick_id <= warmup:
193:         _STATE.last_tick_id = tick_id
194:         _STATE.recent_scores = []
195:         _STATE.last_position = "FLAT"
196:         _STATE.last_flat_after_position_tick = None
197:         _debug_log_line(
198:             tick_id=tick_id,
199:             current_position="FLAT",
200:             score=0,
201:             intent="HOLD",
202:             forced=False,
203:             atr_sig=0,
204:         )
205:         return ("HOLD", False)
206: 
207:     force_enabled = bool(getattr(cfg, "test_force_intents", False))
208:     if force_enabled:
209:         sell_every = int(getattr(cfg, "test_force_sell_every", 0))
210:         buy_every = int(getattr(cfg, "test_force_buy_every", 0))
211: 
212:         _STATE.last_tick_id = tick_id
```

### Context 50

```text
190: 
191:     warmup = int(getattr(cfg, "test_force_warmup_ticks", 0))
192:     if tick_id <= warmup:
193:         _STATE.last_tick_id = tick_id
194:         _STATE.recent_scores = []
195:         _STATE.last_position = "FLAT"
196:         _STATE.last_flat_after_position_tick = None
197:         _debug_log_line(
198:             tick_id=tick_id,
199:             current_position="FLAT",
200:             score=0,
201:             intent="HOLD",
202:             forced=False,
203:             atr_sig=0,
204:         )
205:         return ("HOLD", False)
206: 
207:     force_enabled = bool(getattr(cfg, "test_force_intents", False))
208:     if force_enabled:
209:         sell_every = int(getattr(cfg, "test_force_sell_every", 0))
210:         buy_every = int(getattr(cfg, "test_force_buy_every", 0))
211: 
212:         _STATE.last_tick_id = tick_id
213:         _STATE.recent_scores = []
214: 
215:         if sell_every > 0 and tick_id % sell_every == 0:
216:             _debug_log_line(
217:                 tick_id=tick_id,
218:                 current_position=_normalize_position(current_position),
```

### Context 51

```text
191:     warmup = int(getattr(cfg, "test_force_warmup_ticks", 0))
192:     if tick_id <= warmup:
193:         _STATE.last_tick_id = tick_id
194:         _STATE.recent_scores = []
195:         _STATE.last_position = "FLAT"
196:         _STATE.last_flat_after_position_tick = None
197:         _debug_log_line(
198:             tick_id=tick_id,
199:             current_position="FLAT",
200:             score=0,
201:             intent="HOLD",
202:             forced=False,
203:             atr_sig=0,
204:         )
205:         return ("HOLD", False)
206: 
207:     force_enabled = bool(getattr(cfg, "test_force_intents", False))
208:     if force_enabled:
209:         sell_every = int(getattr(cfg, "test_force_sell_every", 0))
210:         buy_every = int(getattr(cfg, "test_force_buy_every", 0))
211: 
212:         _STATE.last_tick_id = tick_id
213:         _STATE.recent_scores = []
214: 
215:         if sell_every > 0 and tick_id % sell_every == 0:
216:             _debug_log_line(
217:                 tick_id=tick_id,
218:                 current_position=_normalize_position(current_position),
219:                 score=0,
```

### Context 52

```text
195:         _STATE.last_position = "FLAT"
196:         _STATE.last_flat_after_position_tick = None
197:         _debug_log_line(
198:             tick_id=tick_id,
199:             current_position="FLAT",
200:             score=0,
201:             intent="HOLD",
202:             forced=False,
203:             atr_sig=0,
204:         )
205:         return ("HOLD", False)
206: 
207:     force_enabled = bool(getattr(cfg, "test_force_intents", False))
208:     if force_enabled:
209:         sell_every = int(getattr(cfg, "test_force_sell_every", 0))
210:         buy_every = int(getattr(cfg, "test_force_buy_every", 0))
211: 
212:         _STATE.last_tick_id = tick_id
213:         _STATE.recent_scores = []
214: 
215:         if sell_every > 0 and tick_id % sell_every == 0:
216:             _debug_log_line(
217:                 tick_id=tick_id,
218:                 current_position=_normalize_position(current_position),
219:                 score=0,
220:                 intent="SELL",
221:                 forced=True,
222:                 atr_sig=0,
223:             )
```

### Context 53

```text
203:             atr_sig=0,
204:         )
205:         return ("HOLD", False)
206: 
207:     force_enabled = bool(getattr(cfg, "test_force_intents", False))
208:     if force_enabled:
209:         sell_every = int(getattr(cfg, "test_force_sell_every", 0))
210:         buy_every = int(getattr(cfg, "test_force_buy_every", 0))
211: 
212:         _STATE.last_tick_id = tick_id
213:         _STATE.recent_scores = []
214: 
215:         if sell_every > 0 and tick_id % sell_every == 0:
216:             _debug_log_line(
217:                 tick_id=tick_id,
218:                 current_position=_normalize_position(current_position),
219:                 score=0,
220:                 intent="SELL",
221:                 forced=True,
222:                 atr_sig=0,
223:             )
224:             return ("SELL", True)
225: 
226:         if buy_every > 0 and tick_id % buy_every == 0:
227:             _debug_log_line(
228:                 tick_id=tick_id,
229:                 current_position=_normalize_position(current_position),
230:                 score=0,
231:                 intent="BUY",
```

### Context 54

```text
209:         sell_every = int(getattr(cfg, "test_force_sell_every", 0))
210:         buy_every = int(getattr(cfg, "test_force_buy_every", 0))
211: 
212:         _STATE.last_tick_id = tick_id
213:         _STATE.recent_scores = []
214: 
215:         if sell_every > 0 and tick_id % sell_every == 0:
216:             _debug_log_line(
217:                 tick_id=tick_id,
218:                 current_position=_normalize_position(current_position),
219:                 score=0,
220:                 intent="SELL",
221:                 forced=True,
222:                 atr_sig=0,
223:             )
224:             return ("SELL", True)
225: 
226:         if buy_every > 0 and tick_id % buy_every == 0:
227:             _debug_log_line(
228:                 tick_id=tick_id,
229:                 current_position=_normalize_position(current_position),
230:                 score=0,
231:                 intent="BUY",
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
```

### Context 55

```text
210:         buy_every = int(getattr(cfg, "test_force_buy_every", 0))
211: 
212:         _STATE.last_tick_id = tick_id
213:         _STATE.recent_scores = []
214: 
215:         if sell_every > 0 and tick_id % sell_every == 0:
216:             _debug_log_line(
217:                 tick_id=tick_id,
218:                 current_position=_normalize_position(current_position),
219:                 score=0,
220:                 intent="SELL",
221:                 forced=True,
222:                 atr_sig=0,
223:             )
224:             return ("SELL", True)
225: 
226:         if buy_every > 0 and tick_id % buy_every == 0:
227:             _debug_log_line(
228:                 tick_id=tick_id,
229:                 current_position=_normalize_position(current_position),
230:                 score=0,
231:                 intent="BUY",
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
```

### Context 56

```text
214: 
215:         if sell_every > 0 and tick_id % sell_every == 0:
216:             _debug_log_line(
217:                 tick_id=tick_id,
218:                 current_position=_normalize_position(current_position),
219:                 score=0,
220:                 intent="SELL",
221:                 forced=True,
222:                 atr_sig=0,
223:             )
224:             return ("SELL", True)
225: 
226:         if buy_every > 0 and tick_id % buy_every == 0:
227:             _debug_log_line(
228:                 tick_id=tick_id,
229:                 current_position=_normalize_position(current_position),
230:                 score=0,
231:                 intent="BUY",
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
```

### Context 57

```text
220:                 intent="SELL",
221:                 forced=True,
222:                 atr_sig=0,
223:             )
224:             return ("SELL", True)
225: 
226:         if buy_every > 0 and tick_id % buy_every == 0:
227:             _debug_log_line(
228:                 tick_id=tick_id,
229:                 current_position=_normalize_position(current_position),
230:                 score=0,
231:                 intent="BUY",
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
```

### Context 58

```text
221:                 forced=True,
222:                 atr_sig=0,
223:             )
224:             return ("SELL", True)
225: 
226:         if buy_every > 0 and tick_id % buy_every == 0:
227:             _debug_log_line(
228:                 tick_id=tick_id,
229:                 current_position=_normalize_position(current_position),
230:                 score=0,
231:                 intent="BUY",
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
```

### Context 59

```text
225: 
226:         if buy_every > 0 and tick_id % buy_every == 0:
227:             _debug_log_line(
228:                 tick_id=tick_id,
229:                 current_position=_normalize_position(current_position),
230:                 score=0,
231:                 intent="BUY",
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
```

### Context 60

```text
230:                 score=0,
231:                 intent="BUY",
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
```

### Context 61

```text
231:                 intent="BUY",
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
```

### Context 62

```text
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
```

### Context 63

```text
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
```

### Context 64

```text
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
```

### Context 65

```text
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
```

### Context 66

```text
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
```

### Context 67

```text
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
```

### Context 68

```text
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
```

### Context 69

```text
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
```

### Context 70

```text
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
279:             intent = "SELL"
280: 
281:     elif pos == "SHORT":
282:         if _last_n_all_ge(2, 2):
```

### Context 71

```text
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
279:             intent = "SELL"
280: 
281:     elif pos == "SHORT":
282:         if _last_n_all_ge(2, 2):
283:             intent = "BUY"
284: 
285:     _STATE.last_tick_id = tick_id
```

### Context 72

```text
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
279:             intent = "SELL"
280: 
281:     elif pos == "SHORT":
282:         if _last_n_all_ge(2, 2):
283:             intent = "BUY"
284: 
285:     _STATE.last_tick_id = tick_id
286: 
287:     _debug_log_line(
288:         tick_id=tick_id,
289:         current_position=pos,
290:         score=score,
```

### Context 73

```text
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
279:             intent = "SELL"
280: 
281:     elif pos == "SHORT":
282:         if _last_n_all_ge(2, 2):
283:             intent = "BUY"
284: 
285:     _STATE.last_tick_id = tick_id
286: 
287:     _debug_log_line(
288:         tick_id=tick_id,
289:         current_position=pos,
290:         score=score,
291:         intent=intent,
292:         forced=False,
293:         atr_sig=atr_sig,
```

### Context 74

```text
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
279:             intent = "SELL"
280: 
281:     elif pos == "SHORT":
282:         if _last_n_all_ge(2, 2):
283:             intent = "BUY"
284: 
285:     _STATE.last_tick_id = tick_id
286: 
287:     _debug_log_line(
288:         tick_id=tick_id,
289:         current_position=pos,
290:         score=score,
291:         intent=intent,
292:         forced=False,
293:         atr_sig=atr_sig,
294:     )
295: 
296:     return (intent, False)
```

### Context 75

```text
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
279:             intent = "SELL"
280: 
281:     elif pos == "SHORT":
282:         if _last_n_all_ge(2, 2):
283:             intent = "BUY"
284: 
285:     _STATE.last_tick_id = tick_id
286: 
287:     _debug_log_line(
288:         tick_id=tick_id,
289:         current_position=pos,
290:         score=score,
291:         intent=intent,
292:         forced=False,
293:         atr_sig=atr_sig,
294:     )
295: 
296:     return (intent, False)
```

### Context 76

```text
280: 
281:     elif pos == "SHORT":
282:         if _last_n_all_ge(2, 2):
283:             intent = "BUY"
284: 
285:     _STATE.last_tick_id = tick_id
286: 
287:     _debug_log_line(
288:         tick_id=tick_id,
289:         current_position=pos,
290:         score=score,
291:         intent=intent,
292:         forced=False,
293:         atr_sig=atr_sig,
294:     )
295: 
296:     return (intent, False)
```

### Context 77

```text
286: 
287:     _debug_log_line(
288:         tick_id=tick_id,
289:         current_position=pos,
290:         score=score,
291:         intent=intent,
292:         forced=False,
293:         atr_sig=atr_sig,
294:     )
295: 
296:     return (intent, False)
```

## Target: live_l1/core/feature_snapshot.py

exists: True

### Context 1

```text
6: # - centralizes signal access and gate fields
7: # - ASCII-only
8: 
9: from __future__ import annotations
10: 
11: from dataclasses import dataclass
12: from typing import Dict, Mapping
13: 
14: 
15: SIGNAL_COLUMNS = (
16:     "rsi_signal",
17:     "macd_signal",
18:     "bollinger_signal",
19:     "ma200_signal",
20:     "stoch_signal",
21:     "atr_signal",
22:     "ema50_signal",
23:     "adx_signal",
24:     "cci_signal",
25:     "mfi_signal",
26:     "obv_signal",
27:     "roc_signal",
28: )
29: 
30: 
31: def _to_int(value: object, default: int = 0) -> int:
32:     if value is None:
33:         return default
34:     s = str(value).strip()
```

### Context 2

```text
9: from __future__ import annotations
10: 
11: from dataclasses import dataclass
12: from typing import Dict, Mapping
13: 
14: 
15: SIGNAL_COLUMNS = (
16:     "rsi_signal",
17:     "macd_signal",
18:     "bollinger_signal",
19:     "ma200_signal",
20:     "stoch_signal",
21:     "atr_signal",
22:     "ema50_signal",
23:     "adx_signal",
24:     "cci_signal",
25:     "mfi_signal",
26:     "obv_signal",
27:     "roc_signal",
28: )
29: 
30: 
31: def _to_int(value: object, default: int = 0) -> int:
32:     if value is None:
33:         return default
34:     s = str(value).strip()
35:     if s == "":
36:         return default
37:     try:
```

### Context 3

```text
10: 
11: from dataclasses import dataclass
12: from typing import Dict, Mapping
13: 
14: 
15: SIGNAL_COLUMNS = (
16:     "rsi_signal",
17:     "macd_signal",
18:     "bollinger_signal",
19:     "ma200_signal",
20:     "stoch_signal",
21:     "atr_signal",
22:     "ema50_signal",
23:     "adx_signal",
24:     "cci_signal",
25:     "mfi_signal",
26:     "obv_signal",
27:     "roc_signal",
28: )
29: 
30: 
31: def _to_int(value: object, default: int = 0) -> int:
32:     if value is None:
33:         return default
34:     s = str(value).strip()
35:     if s == "":
36:         return default
37:     try:
38:         return int(float(s))
```

### Context 4

```text
15: SIGNAL_COLUMNS = (
16:     "rsi_signal",
17:     "macd_signal",
18:     "bollinger_signal",
19:     "ma200_signal",
20:     "stoch_signal",
21:     "atr_signal",
22:     "ema50_signal",
23:     "adx_signal",
24:     "cci_signal",
25:     "mfi_signal",
26:     "obv_signal",
27:     "roc_signal",
28: )
29: 
30: 
31: def _to_int(value: object, default: int = 0) -> int:
32:     if value is None:
33:         return default
34:     s = str(value).strip()
35:     if s == "":
36:         return default
37:     try:
38:         return int(float(s))
39:     except Exception:
40:         return default
41: 
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
```

### Context 5

```text
23:     "adx_signal",
24:     "cci_signal",
25:     "mfi_signal",
26:     "obv_signal",
27:     "roc_signal",
28: )
29: 
30: 
31: def _to_int(value: object, default: int = 0) -> int:
32:     if value is None:
33:         return default
34:     s = str(value).strip()
35:     if s == "":
36:         return default
37:     try:
38:         return int(float(s))
39:     except Exception:
40:         return default
41: 
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
44:     if value is None:
45:         return default
46:     s = str(value).strip()
47:     if s == "":
48:         return default
49:     try:
50:         return float(s)
51:     except Exception:
```

### Context 6

```text
26:     "obv_signal",
27:     "roc_signal",
28: )
29: 
30: 
31: def _to_int(value: object, default: int = 0) -> int:
32:     if value is None:
33:         return default
34:     s = str(value).strip()
35:     if s == "":
36:         return default
37:     try:
38:         return int(float(s))
39:     except Exception:
40:         return default
41: 
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
44:     if value is None:
45:         return default
46:     s = str(value).strip()
47:     if s == "":
48:         return default
49:     try:
50:         return float(s)
51:     except Exception:
52:         return default
53: 
54: 
```

### Context 7

```text
28: )
29: 
30: 
31: def _to_int(value: object, default: int = 0) -> int:
32:     if value is None:
33:         return default
34:     s = str(value).strip()
35:     if s == "":
36:         return default
37:     try:
38:         return int(float(s))
39:     except Exception:
40:         return default
41: 
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
44:     if value is None:
45:         return default
46:     s = str(value).strip()
47:     if s == "":
48:         return default
49:     try:
50:         return float(s)
51:     except Exception:
52:         return default
53: 
54: 
55: @dataclass(frozen=True)
56: class FeatureSnapshot:
```

### Context 8

```text
30: 
31: def _to_int(value: object, default: int = 0) -> int:
32:     if value is None:
33:         return default
34:     s = str(value).strip()
35:     if s == "":
36:         return default
37:     try:
38:         return int(float(s))
39:     except Exception:
40:         return default
41: 
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
44:     if value is None:
45:         return default
46:     s = str(value).strip()
47:     if s == "":
48:         return default
49:     try:
50:         return float(s)
51:     except Exception:
52:         return default
53: 
54: 
55: @dataclass(frozen=True)
56: class FeatureSnapshot:
57:     snapshot_id: str
58:     timestamp_utc: str
```

### Context 9

```text
35:     if s == "":
36:         return default
37:     try:
38:         return int(float(s))
39:     except Exception:
40:         return default
41: 
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
44:     if value is None:
45:         return default
46:     s = str(value).strip()
47:     if s == "":
48:         return default
49:     try:
50:         return float(s)
51:     except Exception:
52:         return default
53: 
54: 
55: @dataclass(frozen=True)
56: class FeatureSnapshot:
57:     snapshot_id: str
58:     timestamp_utc: str
59:     symbol: str
60:     price: float
61:     open: float
62:     high: float
63:     low: float
```

### Context 10

```text
38:         return int(float(s))
39:     except Exception:
40:         return default
41: 
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
44:     if value is None:
45:         return default
46:     s = str(value).strip()
47:     if s == "":
48:         return default
49:     try:
50:         return float(s)
51:     except Exception:
52:         return default
53: 
54: 
55: @dataclass(frozen=True)
56: class FeatureSnapshot:
57:     snapshot_id: str
58:     timestamp_utc: str
59:     symbol: str
60:     price: float
61:     open: float
62:     high: float
63:     low: float
64:     close: float
65:     volume: float
66:     allow_long: int
```

### Context 11

```text
40:         return default
41: 
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
44:     if value is None:
45:         return default
46:     s = str(value).strip()
47:     if s == "":
48:         return default
49:     try:
50:         return float(s)
51:     except Exception:
52:         return default
53: 
54: 
55: @dataclass(frozen=True)
56: class FeatureSnapshot:
57:     snapshot_id: str
58:     timestamp_utc: str
59:     symbol: str
60:     price: float
61:     open: float
62:     high: float
63:     low: float
64:     close: float
65:     volume: float
66:     allow_long: int
67:     allow_short: int
68:     regime_v2: int
```

### Context 12

```text
42: 
43: def _to_float(value: object, default: float = 0.0) -> float:
44:     if value is None:
45:         return default
46:     s = str(value).strip()
47:     if s == "":
48:         return default
49:     try:
50:         return float(s)
51:     except Exception:
52:         return default
53: 
54: 
55: @dataclass(frozen=True)
56: class FeatureSnapshot:
57:     snapshot_id: str
58:     timestamp_utc: str
59:     symbol: str
60:     price: float
61:     open: float
62:     high: float
63:     low: float
64:     close: float
65:     volume: float
66:     allow_long: int
67:     allow_short: int
68:     regime_v2: int
69:     signals: Dict[str, int]
70: 
```

### Context 13

```text
62:     high: float
63:     low: float
64:     close: float
65:     volume: float
66:     allow_long: int
67:     allow_short: int
68:     regime_v2: int
69:     signals: Dict[str, int]
70: 
71:     def signal(self, name: str, default: int = 0) -> int:
72:         return _to_int(self.signals.get(name), default)
73: 
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
```

### Context 14

```text
64:     close: float
65:     volume: float
66:     allow_long: int
67:     allow_short: int
68:     regime_v2: int
69:     signals: Dict[str, int]
70: 
71:     def signal(self, name: str, default: int = 0) -> int:
72:         return _to_int(self.signals.get(name), default)
73: 
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
```

### Context 15

```text
65:     volume: float
66:     allow_long: int
67:     allow_short: int
68:     regime_v2: int
69:     signals: Dict[str, int]
70: 
71:     def signal(self, name: str, default: int = 0) -> int:
72:         return _to_int(self.signals.get(name), default)
73: 
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
93: 
```

### Context 16

```text
67:     allow_short: int
68:     regime_v2: int
69:     signals: Dict[str, int]
70: 
71:     def signal(self, name: str, default: int = 0) -> int:
72:         return _to_int(self.signals.get(name), default)
73: 
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
93: 
94:     return FeatureSnapshot(
95:         snapshot_id=str(getattr(snapshot, "snapshot_id", "")).strip(),
```

### Context 17

```text
68:     regime_v2: int
69:     signals: Dict[str, int]
70: 
71:     def signal(self, name: str, default: int = 0) -> int:
72:         return _to_int(self.signals.get(name), default)
73: 
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
93: 
94:     return FeatureSnapshot(
95:         snapshot_id=str(getattr(snapshot, "snapshot_id", "")).strip(),
96:         timestamp_utc=str(getattr(snapshot, "timestamp_utc", "")).strip(),
```

### Context 18

```text
70: 
71:     def signal(self, name: str, default: int = 0) -> int:
72:         return _to_int(self.signals.get(name), default)
73: 
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
93: 
94:     return FeatureSnapshot(
95:         snapshot_id=str(getattr(snapshot, "snapshot_id", "")).strip(),
96:         timestamp_utc=str(getattr(snapshot, "timestamp_utc", "")).strip(),
97:         symbol=str(getattr(snapshot, "symbol", "")).strip(),
98:         price=_to_float(getattr(snapshot, "price", 0.0), 0.0),
```

### Context 19

```text
71:     def signal(self, name: str, default: int = 0) -> int:
72:         return _to_int(self.signals.get(name), default)
73: 
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
93: 
94:     return FeatureSnapshot(
95:         snapshot_id=str(getattr(snapshot, "snapshot_id", "")).strip(),
96:         timestamp_utc=str(getattr(snapshot, "timestamp_utc", "")).strip(),
97:         symbol=str(getattr(snapshot, "symbol", "")).strip(),
98:         price=_to_float(getattr(snapshot, "price", 0.0), 0.0),
99:         open=_to_float(getattr(snapshot, "open", 0.0), 0.0),
```

### Context 20

```text
73: 
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
93: 
94:     return FeatureSnapshot(
95:         snapshot_id=str(getattr(snapshot, "snapshot_id", "")).strip(),
96:         timestamp_utc=str(getattr(snapshot, "timestamp_utc", "")).strip(),
97:         symbol=str(getattr(snapshot, "symbol", "")).strip(),
98:         price=_to_float(getattr(snapshot, "price", 0.0), 0.0),
99:         open=_to_float(getattr(snapshot, "open", 0.0), 0.0),
100:         high=_to_float(getattr(snapshot, "high", 0.0), 0.0),
101:         low=_to_float(getattr(snapshot, "low", 0.0), 0.0),
```

### Context 21

```text
74:     def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
75:         score = 0.0
76:         for col, w in weights.items():
77:             score += float(w) * float(self.signal(col, 0))
78:         return score
79: 
80:     def signal_score(self) -> int:
81:         score = 0
82:         for col in SIGNAL_COLUMNS:
83:             score += self.signal(col, 0)
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
93: 
94:     return FeatureSnapshot(
95:         snapshot_id=str(getattr(snapshot, "snapshot_id", "")).strip(),
96:         timestamp_utc=str(getattr(snapshot, "timestamp_utc", "")).strip(),
97:         symbol=str(getattr(snapshot, "symbol", "")).strip(),
98:         price=_to_float(getattr(snapshot, "price", 0.0), 0.0),
99:         open=_to_float(getattr(snapshot, "open", 0.0), 0.0),
100:         high=_to_float(getattr(snapshot, "high", 0.0), 0.0),
101:         low=_to_float(getattr(snapshot, "low", 0.0), 0.0),
102:         close=_to_float(getattr(snapshot, "close", 0.0), 0.0),
```

### Context 22

```text
84:         return score
85: 
86: 
87: def build_feature_snapshot(snapshot) -> FeatureSnapshot:
88:     raw_signals = getattr(snapshot, "signals", {}) or {}
89: 
90:     signals: Dict[str, int] = {}
91:     for col in SIGNAL_COLUMNS:
92:         signals[col] = _to_int(raw_signals.get(col), 0)
93: 
94:     return FeatureSnapshot(
95:         snapshot_id=str(getattr(snapshot, "snapshot_id", "")).strip(),
96:         timestamp_utc=str(getattr(snapshot, "timestamp_utc", "")).strip(),
97:         symbol=str(getattr(snapshot, "symbol", "")).strip(),
98:         price=_to_float(getattr(snapshot, "price", 0.0), 0.0),
99:         open=_to_float(getattr(snapshot, "open", 0.0), 0.0),
100:         high=_to_float(getattr(snapshot, "high", 0.0), 0.0),
101:         low=_to_float(getattr(snapshot, "low", 0.0), 0.0),
102:         close=_to_float(getattr(snapshot, "close", 0.0), 0.0),
103:         volume=_to_float(getattr(snapshot, "volume", 0.0), 0.0),
104:         allow_long=_to_int(getattr(snapshot, "allow_long", 0), 0),
105:         allow_short=_to_int(getattr(snapshot, "allow_short", 0), 0),
106:         regime_v2=_to_int(getattr(snapshot, "regime_v2", 0), 0),
107:         signals=signals,
108:     )
```

## Target: live_l1/core/loop.py

exists: True

### Context 1

```text
50:     market_csv_path: str
51:     seeds_5m_csv: str
52:     thresh_5m: float
53:     timing_v2_shadow: bool
54:     timing_v2_history_len: int
55: 
56: 
57: def _env_bool(key: str, default: bool = False) -> bool:
58:     v = os.environ.get(key)
59:     if v is None:
60:         return default
61:     return v.strip().lower() in ("1", "true", "yes", "y", "on")
62: 
63: 
64: def _env_int(key: str, default: int) -> int:
65:     v = os.environ.get(key)
66:     if v is None or v.strip() == "":
67:         return default
68:     try:
69:         return int(v)
70:     except Exception:
71:         return default
72: 
73: 
74: def _env_float(key: str, default: float) -> float:
75:     v = os.environ.get(key)
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
```

### Context 2

```text
51:     seeds_5m_csv: str
52:     thresh_5m: float
53:     timing_v2_shadow: bool
54:     timing_v2_history_len: int
55: 
56: 
57: def _env_bool(key: str, default: bool = False) -> bool:
58:     v = os.environ.get(key)
59:     if v is None:
60:         return default
61:     return v.strip().lower() in ("1", "true", "yes", "y", "on")
62: 
63: 
64: def _env_int(key: str, default: int) -> int:
65:     v = os.environ.get(key)
66:     if v is None or v.strip() == "":
67:         return default
68:     try:
69:         return int(v)
70:     except Exception:
71:         return default
72: 
73: 
74: def _env_float(key: str, default: float) -> float:
75:     v = os.environ.get(key)
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
79:         return float(v)
```

### Context 3

```text
57: def _env_bool(key: str, default: bool = False) -> bool:
58:     v = os.environ.get(key)
59:     if v is None:
60:         return default
61:     return v.strip().lower() in ("1", "true", "yes", "y", "on")
62: 
63: 
64: def _env_int(key: str, default: int) -> int:
65:     v = os.environ.get(key)
66:     if v is None or v.strip() == "":
67:         return default
68:     try:
69:         return int(v)
70:     except Exception:
71:         return default
72: 
73: 
74: def _env_float(key: str, default: float) -> float:
75:     v = os.environ.get(key)
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
79:         return float(v)
80:     except Exception:
81:         return default
82: 
83: 
84: def _apply_startup_recovery_to_state(cfg: RuntimeConfig, state) -> dict:
85:     if not _env_bool("L1_STARTUP_RECOVERY", False):
```

### Context 4

```text
59:     if v is None:
60:         return default
61:     return v.strip().lower() in ("1", "true", "yes", "y", "on")
62: 
63: 
64: def _env_int(key: str, default: int) -> int:
65:     v = os.environ.get(key)
66:     if v is None or v.strip() == "":
67:         return default
68:     try:
69:         return int(v)
70:     except Exception:
71:         return default
72: 
73: 
74: def _env_float(key: str, default: float) -> float:
75:     v = os.environ.get(key)
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
79:         return float(v)
80:     except Exception:
81:         return default
82: 
83: 
84: def _apply_startup_recovery_to_state(cfg: RuntimeConfig, state) -> dict:
85:     if not _env_bool("L1_STARTUP_RECOVERY", False):
86:         return {"enabled": 0, "applied": 0, "reason": "disabled"}
87: 
```

### Context 5

```text
61:     return v.strip().lower() in ("1", "true", "yes", "y", "on")
62: 
63: 
64: def _env_int(key: str, default: int) -> int:
65:     v = os.environ.get(key)
66:     if v is None or v.strip() == "":
67:         return default
68:     try:
69:         return int(v)
70:     except Exception:
71:         return default
72: 
73: 
74: def _env_float(key: str, default: float) -> float:
75:     v = os.environ.get(key)
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
79:         return float(v)
80:     except Exception:
81:         return default
82: 
83: 
84: def _apply_startup_recovery_to_state(cfg: RuntimeConfig, state) -> dict:
85:     if not _env_bool("L1_STARTUP_RECOVERY", False):
86:         return {"enabled": 0, "applied": 0, "reason": "disabled"}
87: 
88:     if _env_bool("L1_STARTUP_RECONCILIATION_GATE", False):
89:         audit_path = os.environ.get(
```

### Context 6

```text
67:         return default
68:     try:
69:         return int(v)
70:     except Exception:
71:         return default
72: 
73: 
74: def _env_float(key: str, default: float) -> float:
75:     v = os.environ.get(key)
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
79:         return float(v)
80:     except Exception:
81:         return default
82: 
83: 
84: def _apply_startup_recovery_to_state(cfg: RuntimeConfig, state) -> dict:
85:     if not _env_bool("L1_STARTUP_RECOVERY", False):
86:         return {"enabled": 0, "applied": 0, "reason": "disabled"}
87: 
88:     if _env_bool("L1_STARTUP_RECONCILIATION_GATE", False):
89:         audit_path = os.environ.get(
90:             "L1_AUDIT_LOG_PATH",
91:             os.path.join(cfg.repo_root, "live_logs", "execution_audit.jsonl"),
92:         )
93:         loss_path = os.environ.get(
94:             "L1_LOSS_CLUSTER_STATE_PATH",
95:             os.path.join(cfg.repo_root, "live_state", "loss_cluster_state.json"),
```

### Context 7

```text
69:         return int(v)
70:     except Exception:
71:         return default
72: 
73: 
74: def _env_float(key: str, default: float) -> float:
75:     v = os.environ.get(key)
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
79:         return float(v)
80:     except Exception:
81:         return default
82: 
83: 
84: def _apply_startup_recovery_to_state(cfg: RuntimeConfig, state) -> dict:
85:     if not _env_bool("L1_STARTUP_RECOVERY", False):
86:         return {"enabled": 0, "applied": 0, "reason": "disabled"}
87: 
88:     if _env_bool("L1_STARTUP_RECONCILIATION_GATE", False):
89:         audit_path = os.environ.get(
90:             "L1_AUDIT_LOG_PATH",
91:             os.path.join(cfg.repo_root, "live_logs", "execution_audit.jsonl"),
92:         )
93:         loss_path = os.environ.get(
94:             "L1_LOSS_CLUSTER_STATE_PATH",
95:             os.path.join(cfg.repo_root, "live_state", "loss_cluster_state.json"),
96:         )
97:         s2_path = os.environ.get(
```

### Context 8

```text
71:         return default
72: 
73: 
74: def _env_float(key: str, default: float) -> float:
75:     v = os.environ.get(key)
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
79:         return float(v)
80:     except Exception:
81:         return default
82: 
83: 
84: def _apply_startup_recovery_to_state(cfg: RuntimeConfig, state) -> dict:
85:     if not _env_bool("L1_STARTUP_RECOVERY", False):
86:         return {"enabled": 0, "applied": 0, "reason": "disabled"}
87: 
88:     if _env_bool("L1_STARTUP_RECONCILIATION_GATE", False):
89:         audit_path = os.environ.get(
90:             "L1_AUDIT_LOG_PATH",
91:             os.path.join(cfg.repo_root, "live_logs", "execution_audit.jsonl"),
92:         )
93:         loss_path = os.environ.get(
94:             "L1_LOSS_CLUSTER_STATE_PATH",
95:             os.path.join(cfg.repo_root, "live_state", "loss_cluster_state.json"),
96:         )
97:         s2_path = os.environ.get(
98:             "L1_S2_POSITION_PATH",
99:             os.path.join(cfg.repo_root, "live_state", "s2_position.jsonl"),
```

### Context 9

```text
76:     if v is None or v.strip() == "":
77:         return default
78:     try:
79:         return float(v)
80:     except Exception:
81:         return default
82: 
83: 
84: def _apply_startup_recovery_to_state(cfg: RuntimeConfig, state) -> dict:
85:     if not _env_bool("L1_STARTUP_RECOVERY", False):
86:         return {"enabled": 0, "applied": 0, "reason": "disabled"}
87: 
88:     if _env_bool("L1_STARTUP_RECONCILIATION_GATE", False):
89:         audit_path = os.environ.get(
90:             "L1_AUDIT_LOG_PATH",
91:             os.path.join(cfg.repo_root, "live_logs", "execution_audit.jsonl"),
92:         )
93:         loss_path = os.environ.get(
94:             "L1_LOSS_CLUSTER_STATE_PATH",
95:             os.path.join(cfg.repo_root, "live_state", "loss_cluster_state.json"),
96:         )
97:         s2_path = os.environ.get(
98:             "L1_S2_POSITION_PATH",
99:             os.path.join(cfg.repo_root, "live_state", "s2_position.jsonl"),
100:         )
101:         trades_path = os.environ.get(
102:             "L1_TRADE_LOG_PATH",
103:             os.path.join(cfg.repo_root, "live_logs", "trades_l1.jsonl"),
104:         )
```

### Context 10

```text
106:         reconciliation_results = run_reconciliation(
107:             audit_path=Path(audit_path),
108:             s2_path=Path(s2_path),
109:             trades_path=Path(trades_path),
110:             loss_path=Path(loss_path),
111:         )
112: 
113:         failed = [x for x in reconciliation_results if not x.passed]
114: 
115:         if failed:
116:             return {
117:                 "enabled": 1,
118:                 "applied": 0,
119:                 "reason": "startup_reconciliation_failed",
120:                 "reconciliation_gate_enabled": 1,
121:                 "reconciliation_failed_checks": ",".join(x.name for x in failed),
122:                 "reconciliation_failed_details": " | ".join(x.name + ":" + x.detail for x in failed),
123:                 "hard_fail": 1,
124:             }
125: 
126:     recovered = recover_runtime_state(
127:         audit_log_path=os.environ.get(
128:             "L1_AUDIT_LOG_PATH",
129:             os.path.join(cfg.repo_root, "live_logs", "execution_audit.jsonl"),
130:         ),
131:         loss_cluster_state_path=os.environ.get(
132:             "L1_LOSS_CLUSTER_STATE_PATH",
133:             os.path.join(cfg.repo_root, "live_state", "loss_cluster_state.json"),
134:         ),
```

### Context 11

```text
128:             "L1_AUDIT_LOG_PATH",
129:             os.path.join(cfg.repo_root, "live_logs", "execution_audit.jsonl"),
130:         ),
131:         loss_cluster_state_path=os.environ.get(
132:             "L1_LOSS_CLUSTER_STATE_PATH",
133:             os.path.join(cfg.repo_root, "live_state", "loss_cluster_state.json"),
134:         ),
135:     )
136: 
137:     if int(recovered.execution_bad_json_lines) != 0:
138:         return {
139:             "enabled": 1,
140:             "applied": 0,
141:             "reason": "bad_execution_audit_json",
142:             "bad_json_lines": int(recovered.execution_bad_json_lines),
143:         }
144: 
145:     if recovered.position not in ("LONG", "SHORT", "FLAT"):
146:         return {"enabled": 1, "applied": 0, "reason": "invalid_recovered_position"}
147: 
148:     if recovered.position == "FLAT":
149:         state.s2_position.position = "FLAT"
150:         state.s2_position.side = ""
151:         state.s2_position.size = 0.0
152:         state.s2_position.position_size = 0.0
153:         state.s2_position.entry_price = None
154:         state.s2_position.entry_timestamp_utc = ""
155:     else:
156:         state.s2_position.position = recovered.position
```

### Context 12

```text
136: 
137:     if int(recovered.execution_bad_json_lines) != 0:
138:         return {
139:             "enabled": 1,
140:             "applied": 0,
141:             "reason": "bad_execution_audit_json",
142:             "bad_json_lines": int(recovered.execution_bad_json_lines),
143:         }
144: 
145:     if recovered.position not in ("LONG", "SHORT", "FLAT"):
146:         return {"enabled": 1, "applied": 0, "reason": "invalid_recovered_position"}
147: 
148:     if recovered.position == "FLAT":
149:         state.s2_position.position = "FLAT"
150:         state.s2_position.side = ""
151:         state.s2_position.size = 0.0
152:         state.s2_position.position_size = 0.0
153:         state.s2_position.entry_price = None
154:         state.s2_position.entry_timestamp_utc = ""
155:     else:
156:         state.s2_position.position = recovered.position
157:         state.s2_position.side = recovered.side
158:         state.s2_position.entry_price = recovered.entry_price
159:         state.s2_position.entry_timestamp_utc = recovered.entry_timestamp_utc
160: 
161:         size = float(getattr(state.s2_position, "position_size", 0.0) or 0.0)
162:         if size <= 0.0:
163:             size = 1.0
164: 
```

### Context 13

```text
143:         }
144: 
145:     if recovered.position not in ("LONG", "SHORT", "FLAT"):
146:         return {"enabled": 1, "applied": 0, "reason": "invalid_recovered_position"}
147: 
148:     if recovered.position == "FLAT":
149:         state.s2_position.position = "FLAT"
150:         state.s2_position.side = ""
151:         state.s2_position.size = 0.0
152:         state.s2_position.position_size = 0.0
153:         state.s2_position.entry_price = None
154:         state.s2_position.entry_timestamp_utc = ""
155:     else:
156:         state.s2_position.position = recovered.position
157:         state.s2_position.side = recovered.side
158:         state.s2_position.entry_price = recovered.entry_price
159:         state.s2_position.entry_timestamp_utc = recovered.entry_timestamp_utc
160: 
161:         size = float(getattr(state.s2_position, "position_size", 0.0) or 0.0)
162:         if size <= 0.0:
163:             size = 1.0
164: 
165:         state.s2_position.size = size
166:         state.s2_position.position_size = size
167: 
168:     return {
169:         "enabled": 1,
170:         "applied": 1,
171:         "reason": "startup_recovery_applied",
```

### Context 14

```text
144: 
145:     if recovered.position not in ("LONG", "SHORT", "FLAT"):
146:         return {"enabled": 1, "applied": 0, "reason": "invalid_recovered_position"}
147: 
148:     if recovered.position == "FLAT":
149:         state.s2_position.position = "FLAT"
150:         state.s2_position.side = ""
151:         state.s2_position.size = 0.0
152:         state.s2_position.position_size = 0.0
153:         state.s2_position.entry_price = None
154:         state.s2_position.entry_timestamp_utc = ""
155:     else:
156:         state.s2_position.position = recovered.position
157:         state.s2_position.side = recovered.side
158:         state.s2_position.entry_price = recovered.entry_price
159:         state.s2_position.entry_timestamp_utc = recovered.entry_timestamp_utc
160: 
161:         size = float(getattr(state.s2_position, "position_size", 0.0) or 0.0)
162:         if size <= 0.0:
163:             size = 1.0
164: 
165:         state.s2_position.size = size
166:         state.s2_position.position_size = size
167: 
168:     return {
169:         "enabled": 1,
170:         "applied": 1,
171:         "reason": "startup_recovery_applied",
172:         "position": str(recovered.position),
```

### Context 15

```text
148:     if recovered.position == "FLAT":
149:         state.s2_position.position = "FLAT"
150:         state.s2_position.side = ""
151:         state.s2_position.size = 0.0
152:         state.s2_position.position_size = 0.0
153:         state.s2_position.entry_price = None
154:         state.s2_position.entry_timestamp_utc = ""
155:     else:
156:         state.s2_position.position = recovered.position
157:         state.s2_position.side = recovered.side
158:         state.s2_position.entry_price = recovered.entry_price
159:         state.s2_position.entry_timestamp_utc = recovered.entry_timestamp_utc
160: 
161:         size = float(getattr(state.s2_position, "position_size", 0.0) or 0.0)
162:         if size <= 0.0:
163:             size = 1.0
164: 
165:         state.s2_position.size = size
166:         state.s2_position.position_size = size
167: 
168:     return {
169:         "enabled": 1,
170:         "applied": 1,
171:         "reason": "startup_recovery_applied",
172:         "position": str(recovered.position),
173:         "side": str(recovered.side),
174:         "entry_price": "" if recovered.entry_price is None else float(recovered.entry_price),
175:         "entry_timestamp_utc": str(recovered.entry_timestamp_utc),
176:         "execution_events_read": int(recovered.execution_events_read),
```

### Context 16

```text
149:         state.s2_position.position = "FLAT"
150:         state.s2_position.side = ""
151:         state.s2_position.size = 0.0
152:         state.s2_position.position_size = 0.0
153:         state.s2_position.entry_price = None
154:         state.s2_position.entry_timestamp_utc = ""
155:     else:
156:         state.s2_position.position = recovered.position
157:         state.s2_position.side = recovered.side
158:         state.s2_position.entry_price = recovered.entry_price
159:         state.s2_position.entry_timestamp_utc = recovered.entry_timestamp_utc
160: 
161:         size = float(getattr(state.s2_position, "position_size", 0.0) or 0.0)
162:         if size <= 0.0:
163:             size = 1.0
164: 
165:         state.s2_position.size = size
166:         state.s2_position.position_size = size
167: 
168:     return {
169:         "enabled": 1,
170:         "applied": 1,
171:         "reason": "startup_recovery_applied",
172:         "position": str(recovered.position),
173:         "side": str(recovered.side),
174:         "entry_price": "" if recovered.entry_price is None else float(recovered.entry_price),
175:         "entry_timestamp_utc": str(recovered.entry_timestamp_utc),
176:         "execution_events_read": int(recovered.execution_events_read),
177:         "loss_cluster_state_loaded": int(recovered.loss_cluster_state_loaded),
```

### Context 17

```text
158:         state.s2_position.entry_price = recovered.entry_price
159:         state.s2_position.entry_timestamp_utc = recovered.entry_timestamp_utc
160: 
161:         size = float(getattr(state.s2_position, "position_size", 0.0) or 0.0)
162:         if size <= 0.0:
163:             size = 1.0
164: 
165:         state.s2_position.size = size
166:         state.s2_position.position_size = size
167: 
168:     return {
169:         "enabled": 1,
170:         "applied": 1,
171:         "reason": "startup_recovery_applied",
172:         "position": str(recovered.position),
173:         "side": str(recovered.side),
174:         "entry_price": "" if recovered.entry_price is None else float(recovered.entry_price),
175:         "entry_timestamp_utc": str(recovered.entry_timestamp_utc),
176:         "execution_events_read": int(recovered.execution_events_read),
177:         "loss_cluster_state_loaded": int(recovered.loss_cluster_state_loaded),
178:     }
179: 
180: 
181: 
182: def load_runtime_config(repo_root: str) -> RuntimeConfig:
183:     log_path = os.environ.get(
184:         "L1_LOG_PATH",
185:         os.path.join(repo_root, "live_logs", "l1_paper.log"),
186:     )
```

### Context 18

```text
164: 
165:         state.s2_position.size = size
166:         state.s2_position.position_size = size
167: 
168:     return {
169:         "enabled": 1,
170:         "applied": 1,
171:         "reason": "startup_recovery_applied",
172:         "position": str(recovered.position),
173:         "side": str(recovered.side),
174:         "entry_price": "" if recovered.entry_price is None else float(recovered.entry_price),
175:         "entry_timestamp_utc": str(recovered.entry_timestamp_utc),
176:         "execution_events_read": int(recovered.execution_events_read),
177:         "loss_cluster_state_loaded": int(recovered.loss_cluster_state_loaded),
178:     }
179: 
180: 
181: 
182: def load_runtime_config(repo_root: str) -> RuntimeConfig:
183:     log_path = os.environ.get(
184:         "L1_LOG_PATH",
185:         os.path.join(repo_root, "live_logs", "l1_paper.log"),
186:     )
187: 
188:     cfg = RuntimeConfig(
189:         repo_root=repo_root,
190:         log_path=log_path,
191:         state_dir=os.path.join(repo_root, "live_state"),
192:         symbol=os.environ.get("L1_SYMBOL", "BTCUSDT"),
```

### Context 19

```text
165:         state.s2_position.size = size
166:         state.s2_position.position_size = size
167: 
168:     return {
169:         "enabled": 1,
170:         "applied": 1,
171:         "reason": "startup_recovery_applied",
172:         "position": str(recovered.position),
173:         "side": str(recovered.side),
174:         "entry_price": "" if recovered.entry_price is None else float(recovered.entry_price),
175:         "entry_timestamp_utc": str(recovered.entry_timestamp_utc),
176:         "execution_events_read": int(recovered.execution_events_read),
177:         "loss_cluster_state_loaded": int(recovered.loss_cluster_state_loaded),
178:     }
179: 
180: 
181: 
182: def load_runtime_config(repo_root: str) -> RuntimeConfig:
183:     log_path = os.environ.get(
184:         "L1_LOG_PATH",
185:         os.path.join(repo_root, "live_logs", "l1_paper.log"),
186:     )
187: 
188:     cfg = RuntimeConfig(
189:         repo_root=repo_root,
190:         log_path=log_path,
191:         state_dir=os.path.join(repo_root, "live_state"),
192:         symbol=os.environ.get("L1_SYMBOL", "BTCUSDT"),
193:         gate_mode=os.environ.get("L1_GATE_MODE", "auto"),
```

### Context 20

```text
188:     cfg = RuntimeConfig(
189:         repo_root=repo_root,
190:         log_path=log_path,
191:         state_dir=os.path.join(repo_root, "live_state"),
192:         symbol=os.environ.get("L1_SYMBOL", "BTCUSDT"),
193:         gate_mode=os.environ.get("L1_GATE_MODE", "auto"),
194:         fee_roundtrip=_env_float("L1_FEE_ROUNDTRIP", 0.0004),
195:         decision_tick_seconds=_env_float("L1_DECISION_TICK_SECONDS", 1.0),
196:         trades_window_hours=_env_int("L1_TRADES_WINDOW_HOURS", 6),
197:         test_force_intents=_env_bool("L1_TEST_FORCE_INTENTS", False),
198:         test_force_buy_every=_env_int("L1_TEST_FORCE_BUY_EVERY", 10),
199:         test_force_sell_every=_env_int("L1_TEST_FORCE_SELL_EVERY", 15),
200:         test_force_warmup_ticks=_env_int("L1_TEST_FORCE_WARMUP_TICKS", 0),
201:         market_csv_path=os.environ.get(
202:             "L1_MARKET_CSV_PATH",
203:             "data/l1_paper_short_gate_test.csv",
204:         ),
205:         seeds_5m_csv=os.environ.get(
206:             "SEEDS_5M_CSV",
207:             "seeds/5m/btcusdt_5m_timing_core_v2.csv",
208:         ),
209:         thresh_5m=_env_float("THRESH_5M", 0.60),
210:         timing_v2_shadow=_env_bool("L1_TIMING_V2_SHADOW", False),
211:         timing_v2_history_len=_env_int("L1_TIMING_V2_HISTORY_LEN", 3),
212:     )
213: 
214:     validate_runtime_config(cfg)
215:     return cfg
216: 
```

### Context 21

```text
189:         repo_root=repo_root,
190:         log_path=log_path,
191:         state_dir=os.path.join(repo_root, "live_state"),
192:         symbol=os.environ.get("L1_SYMBOL", "BTCUSDT"),
193:         gate_mode=os.environ.get("L1_GATE_MODE", "auto"),
194:         fee_roundtrip=_env_float("L1_FEE_ROUNDTRIP", 0.0004),
195:         decision_tick_seconds=_env_float("L1_DECISION_TICK_SECONDS", 1.0),
196:         trades_window_hours=_env_int("L1_TRADES_WINDOW_HOURS", 6),
197:         test_force_intents=_env_bool("L1_TEST_FORCE_INTENTS", False),
198:         test_force_buy_every=_env_int("L1_TEST_FORCE_BUY_EVERY", 10),
199:         test_force_sell_every=_env_int("L1_TEST_FORCE_SELL_EVERY", 15),
200:         test_force_warmup_ticks=_env_int("L1_TEST_FORCE_WARMUP_TICKS", 0),
201:         market_csv_path=os.environ.get(
202:             "L1_MARKET_CSV_PATH",
203:             "data/l1_paper_short_gate_test.csv",
204:         ),
205:         seeds_5m_csv=os.environ.get(
206:             "SEEDS_5M_CSV",
207:             "seeds/5m/btcusdt_5m_timing_core_v2.csv",
208:         ),
209:         thresh_5m=_env_float("THRESH_5M", 0.60),
210:         timing_v2_shadow=_env_bool("L1_TIMING_V2_SHADOW", False),
211:         timing_v2_history_len=_env_int("L1_TIMING_V2_HISTORY_LEN", 3),
212:     )
213: 
214:     validate_runtime_config(cfg)
215:     return cfg
216: 
217: 
```

### Context 22

```text
205:         seeds_5m_csv=os.environ.get(
206:             "SEEDS_5M_CSV",
207:             "seeds/5m/btcusdt_5m_timing_core_v2.csv",
208:         ),
209:         thresh_5m=_env_float("THRESH_5M", 0.60),
210:         timing_v2_shadow=_env_bool("L1_TIMING_V2_SHADOW", False),
211:         timing_v2_history_len=_env_int("L1_TIMING_V2_HISTORY_LEN", 3),
212:     )
213: 
214:     validate_runtime_config(cfg)
215:     return cfg
216: 
217: 
218: def _warnings_to_text(warnings: list[str]) -> str:
219:     if not warnings:
220:         return ""
221:     return ",".join(str(w).strip() for w in warnings if str(w).strip() != "")
222: 
223: def _safe_float_lifecycle(value: object, default: float = 0.0) -> float:
224:     if value is None:
225:         return default
226:     try:
227:         return float(value)
228:     except Exception:
229:         return default
230: 
231: 
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
```

### Context 23

```text
210:         timing_v2_shadow=_env_bool("L1_TIMING_V2_SHADOW", False),
211:         timing_v2_history_len=_env_int("L1_TIMING_V2_HISTORY_LEN", 3),
212:     )
213: 
214:     validate_runtime_config(cfg)
215:     return cfg
216: 
217: 
218: def _warnings_to_text(warnings: list[str]) -> str:
219:     if not warnings:
220:         return ""
221:     return ",".join(str(w).strip() for w in warnings if str(w).strip() != "")
222: 
223: def _safe_float_lifecycle(value: object, default: float = 0.0) -> float:
224:     if value is None:
225:         return default
226:     try:
227:         return float(value)
228:     except Exception:
229:         return default
230: 
231: 
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
```

### Context 24

```text
211:         timing_v2_history_len=_env_int("L1_TIMING_V2_HISTORY_LEN", 3),
212:     )
213: 
214:     validate_runtime_config(cfg)
215:     return cfg
216: 
217: 
218: def _warnings_to_text(warnings: list[str]) -> str:
219:     if not warnings:
220:         return ""
221:     return ",".join(str(w).strip() for w in warnings if str(w).strip() != "")
222: 
223: def _safe_float_lifecycle(value: object, default: float = 0.0) -> float:
224:     if value is None:
225:         return default
226:     try:
227:         return float(value)
228:     except Exception:
229:         return default
230: 
231: 
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
```

### Context 25

```text
215:     return cfg
216: 
217: 
218: def _warnings_to_text(warnings: list[str]) -> str:
219:     if not warnings:
220:         return ""
221:     return ",".join(str(w).strip() for w in warnings if str(w).strip() != "")
222: 
223: def _safe_float_lifecycle(value: object, default: float = 0.0) -> float:
224:     if value is None:
225:         return default
226:     try:
227:         return float(value)
228:     except Exception:
229:         return default
230: 
231: 
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
```

### Context 26

```text
217: 
218: def _warnings_to_text(warnings: list[str]) -> str:
219:     if not warnings:
220:         return ""
221:     return ",".join(str(w).strip() for w in warnings if str(w).strip() != "")
222: 
223: def _safe_float_lifecycle(value: object, default: float = 0.0) -> float:
224:     if value is None:
225:         return default
226:     try:
227:         return float(value)
228:     except Exception:
229:         return default
230: 
231: 
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
```

### Context 27

```text
219:     if not warnings:
220:         return ""
221:     return ",".join(str(w).strip() for w in warnings if str(w).strip() != "")
222: 
223: def _safe_float_lifecycle(value: object, default: float = 0.0) -> float:
224:     if value is None:
225:         return default
226:     try:
227:         return float(value)
228:     except Exception:
229:         return default
230: 
231: 
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
```

### Context 28

```text
225:         return default
226:     try:
227:         return float(value)
228:     except Exception:
229:         return default
230: 
231: 
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
```

### Context 29

```text
229:         return default
230: 
231: 
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
```

### Context 30

```text
232: def _parse_lifecycle_ts(value: object) -> datetime | None:
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
258: 
259: def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
260:     side_l = str(side).strip().lower()
```

### Context 31

```text
233:     s = "" if value is None else str(value).strip()
234:     if s == "":
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
258: 
259: def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
260:     side_l = str(side).strip().lower()
261:     regime_l = str(regime).strip().lower()
```

### Context 32

```text
235:         return None
236:     s = s.replace("_", " ")
237:     try:
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
258: 
259: def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
260:     side_l = str(side).strip().lower()
261:     regime_l = str(regime).strip().lower()
262:     atr_l = str(atr_quality).strip().lower()
263: 
```

### Context 33

```text
238:         if s.endswith("Z"):
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
258: 
259: def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
260:     side_l = str(side).strip().lower()
261:     regime_l = str(regime).strip().lower()
262:     atr_l = str(atr_quality).strip().lower()
263: 
264:     reasons = []
265:     risk = 0
266: 
```

### Context 34

```text
239:             return datetime.fromisoformat(s[:-1] + "+00:00")
240:         dt = datetime.fromisoformat(s)
241:         if dt.tzinfo is None:
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
258: 
259: def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
260:     side_l = str(side).strip().lower()
261:     regime_l = str(regime).strip().lower()
262:     atr_l = str(atr_quality).strip().lower()
263: 
264:     reasons = []
265:     risk = 0
266: 
267:     if side_l == "long" and regime_l == "bear":
```

### Context 35

```text
242:             return dt.replace(tzinfo=timezone.utc)
243:         return dt
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
258: 
259: def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
260:     side_l = str(side).strip().lower()
261:     regime_l = str(regime).strip().lower()
262:     atr_l = str(atr_quality).strip().lower()
263: 
264:     reasons = []
265:     risk = 0
266: 
267:     if side_l == "long" and regime_l == "bear":
268:         risk = max(risk, 2)
269:         reasons.append("long_bear_incompatibility")
270: 
```

### Context 36

```text
244:     except Exception:
245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
258: 
259: def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
260:     side_l = str(side).strip().lower()
261:     regime_l = str(regime).strip().lower()
262:     atr_l = str(atr_quality).strip().lower()
263: 
264:     reasons = []
265:     risk = 0
266: 
267:     if side_l == "long" and regime_l == "bear":
268:         risk = max(risk, 2)
269:         reasons.append("long_bear_incompatibility")
270: 
271:     if side_l == "short" and regime_l == "bull":
272:         risk = max(risk, 2)
```

### Context 37

```text
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:
252:         return 0.0
253:     out = (b - a).total_seconds()
254:     return float(out) if out > 0.0 else 0.0
255: 
256: 
257: 
258: 
259: def _passive_shadow_risk_from_context(side: str, regime: str, atr_quality: str, current_score: int) -> tuple[int, str, str]:
260:     side_l = str(side).strip().lower()
261:     regime_l = str(regime).strip().lower()
262:     atr_l = str(atr_quality).strip().lower()
263: 
264:     reasons = []
265:     risk = 0
266: 
267:     if side_l == "long" and regime_l == "bear":
268:         risk = max(risk, 2)
269:         reasons.append("long_bear_incompatibility")
270: 
271:     if side_l == "short" and regime_l == "bull":
272:         risk = max(risk, 2)
273:         reasons.append("short_bull_incompatibility")
274: 
275:     if side_l == "short" and regime_l == "bear":
276:         reasons.append("short_bear_compatible")
277: 
```

### Context 38

```text
275:     if side_l == "short" and regime_l == "bear":
276:         reasons.append("short_bear_compatible")
277: 
278:     if side_l == "long" and regime_l == "bull":
279:         reasons.append("long_bull_compatible")
280: 
281:     if atr_l == "bad_atr":
282:         risk = max(risk, 1)
283:         reasons.append("bad_atr")
284: 
285:     if side_l == "long" and current_score <= -3:
286:         risk = max(risk, 2)
287:         reasons.append("long_adverse_score")
288: 
289:     if side_l == "short" and current_score >= 3:
290:         risk = max(risk, 2)
291:         reasons.append("short_adverse_score")
292: 
293:     if risk >= 3:
294:         name = "COLLAPSE_RISK"
295:     elif risk == 2:
296:         name = "TOXIC"
297:     elif risk == 1:
298:         name = "WARNING"
299:     else:
300:         name = "SAFE"
301: 
302:     return risk, name, "|".join(reasons)
303: 
```

### Context 39

```text
277: 
278:     if side_l == "long" and regime_l == "bull":
279:         reasons.append("long_bull_compatible")
280: 
281:     if atr_l == "bad_atr":
282:         risk = max(risk, 1)
283:         reasons.append("bad_atr")
284: 
285:     if side_l == "long" and current_score <= -3:
286:         risk = max(risk, 2)
287:         reasons.append("long_adverse_score")
288: 
289:     if side_l == "short" and current_score >= 3:
290:         risk = max(risk, 2)
291:         reasons.append("short_adverse_score")
292: 
293:     if risk >= 3:
294:         name = "COLLAPSE_RISK"
295:     elif risk == 2:
296:         name = "TOXIC"
297:     elif risk == 1:
298:         name = "WARNING"
299:     else:
300:         name = "SAFE"
301: 
302:     return risk, name, "|".join(reasons)
303: 
304: 
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
```

### Context 40

```text
279:         reasons.append("long_bull_compatible")
280: 
281:     if atr_l == "bad_atr":
282:         risk = max(risk, 1)
283:         reasons.append("bad_atr")
284: 
285:     if side_l == "long" and current_score <= -3:
286:         risk = max(risk, 2)
287:         reasons.append("long_adverse_score")
288: 
289:     if side_l == "short" and current_score >= 3:
290:         risk = max(risk, 2)
291:         reasons.append("short_adverse_score")
292: 
293:     if risk >= 3:
294:         name = "COLLAPSE_RISK"
295:     elif risk == 2:
296:         name = "TOXIC"
297:     elif risk == 1:
298:         name = "WARNING"
299:     else:
300:         name = "SAFE"
301: 
302:     return risk, name, "|".join(reasons)
303: 
304: 
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
306:     side_l = str(side).strip().lower()
307:     regime_l = str(regime).strip().lower()
```

### Context 41

```text
281:     if atr_l == "bad_atr":
282:         risk = max(risk, 1)
283:         reasons.append("bad_atr")
284: 
285:     if side_l == "long" and current_score <= -3:
286:         risk = max(risk, 2)
287:         reasons.append("long_adverse_score")
288: 
289:     if side_l == "short" and current_score >= 3:
290:         risk = max(risk, 2)
291:         reasons.append("short_adverse_score")
292: 
293:     if risk >= 3:
294:         name = "COLLAPSE_RISK"
295:     elif risk == 2:
296:         name = "TOXIC"
297:     elif risk == 1:
298:         name = "WARNING"
299:     else:
300:         name = "SAFE"
301: 
302:     return risk, name, "|".join(reasons)
303: 
304: 
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
306:     side_l = str(side).strip().lower()
307:     regime_l = str(regime).strip().lower()
308:     atr_l = str(atr_quality).strip().lower()
309:     score = int(current_score)
```

### Context 42

```text
292: 
293:     if risk >= 3:
294:         name = "COLLAPSE_RISK"
295:     elif risk == 2:
296:         name = "TOXIC"
297:     elif risk == 1:
298:         name = "WARNING"
299:     else:
300:         name = "SAFE"
301: 
302:     return risk, name, "|".join(reasons)
303: 
304: 
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
306:     side_l = str(side).strip().lower()
307:     regime_l = str(regime).strip().lower()
308:     atr_l = str(atr_quality).strip().lower()
309:     score = int(current_score)
310: 
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
```

### Context 43

```text
295:     elif risk == 2:
296:         name = "TOXIC"
297:     elif risk == 1:
298:         name = "WARNING"
299:     else:
300:         name = "SAFE"
301: 
302:     return risk, name, "|".join(reasons)
303: 
304: 
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
306:     side_l = str(side).strip().lower()
307:     regime_l = str(regime).strip().lower()
308:     atr_l = str(atr_quality).strip().lower()
309:     score = int(current_score)
310: 
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
```

### Context 44

```text
299:     else:
300:         name = "SAFE"
301: 
302:     return risk, name, "|".join(reasons)
303: 
304: 
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
306:     side_l = str(side).strip().lower()
307:     regime_l = str(regime).strip().lower()
308:     atr_l = str(atr_quality).strip().lower()
309:     score = int(current_score)
310: 
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
```

### Context 45

```text
301: 
302:     return risk, name, "|".join(reasons)
303: 
304: 
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
306:     side_l = str(side).strip().lower()
307:     regime_l = str(regime).strip().lower()
308:     atr_l = str(atr_quality).strip().lower()
309:     score = int(current_score)
310: 
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
```

### Context 46

```text
303: 
304: 
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
306:     side_l = str(side).strip().lower()
307:     regime_l = str(regime).strip().lower()
308:     atr_l = str(atr_quality).strip().lower()
309:     score = int(current_score)
310: 
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
```

### Context 47

```text
305: def _passive_shadow_risk_components(side: str, regime: str, atr_quality: str, current_score: int) -> dict:
306:     side_l = str(side).strip().lower()
307:     regime_l = str(regime).strip().lower()
308:     atr_l = str(atr_quality).strip().lower()
309:     score = int(current_score)
310: 
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
```

### Context 48

```text
307:     regime_l = str(regime).strip().lower()
308:     atr_l = str(atr_quality).strip().lower()
309:     score = int(current_score)
310: 
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
```

### Context 49

```text
309:     score = int(current_score)
310: 
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
```

### Context 50

```text
311:     regime_mismatch_score = 0.0
312:     if side_l == "long" and regime_l == "bear":
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
```

### Context 51

```text
313:         regime_mismatch_score = 1.0
314:     elif side_l == "short" and regime_l == "bull":
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
```

### Context 52

```text
315:         regime_mismatch_score = 1.0
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
```

### Context 53

```text
316: 
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
```

### Context 54

```text
317:     atr_stress_score = 1.0 if atr_l == "bad_atr" else 0.0
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
345:     features,
```

### Context 55

```text
318: 
319:     adverse_score_pressure = 0.0
320:     if side_l == "long":
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
345:     features,
346:     regime: str,
```

### Context 56

```text
321:         adverse_score_pressure = max(0.0, min(1.0, abs(min(score, 0)) / 4.0))
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
```

### Context 57

```text
322:     elif side_l == "short":
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
```

### Context 58

```text
323:         adverse_score_pressure = max(0.0, min(1.0, max(score, 0) / 4.0))
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
```

### Context 59

```text
324: 
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
```

### Context 60

```text
325:     shadow_risk_score = (
326:         0.50 * regime_mismatch_score
327:         + 0.30 * atr_stress_score
328:         + 0.20 * adverse_score_pressure
329:     )
330: 
331:     return {
332:         "shadow_risk_score": float(shadow_risk_score),
333:         "regime_mismatch_score": float(regime_mismatch_score),
334:         "atr_stress_score": float(atr_stress_score),
335:         "adverse_score_pressure": float(adverse_score_pressure),
336:     }
337: 
338: 
339: def _append_passive_shadow_risk_snapshot(
340:     repo_root: str,
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
```

### Context 61

```text
341:     tick_id: int,
342:     timestamp_utc: str,
343:     snapshot_id: str,
344:     state,
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
```

### Context 62

```text
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
```

### Context 63

```text
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
```

### Context 64

```text
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
```

### Context 65

```text
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
376:         atr_quality=atr_quality,
```

### Context 66

```text
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
376:         atr_quality=atr_quality,
377:         current_score=current_score,
```

### Context 67

```text
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
376:         atr_quality=atr_quality,
377:         current_score=current_score,
378:     )
379: 
380:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_risk_snapshots.csv")
```

### Context 68

```text
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
376:         atr_quality=atr_quality,
377:         current_score=current_score,
378:     )
379: 
380:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_risk_snapshots.csv")
381:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
382: 
383:     fieldnames = [
384:         "tick_id",
385:         "timestamp_utc",
386:         "snapshot_id",
387:         "entry_timestamp_utc",
388:         "side",
389:         "position",
```

### Context 69

```text
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
376:         atr_quality=atr_quality,
377:         current_score=current_score,
378:     )
379: 
380:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_risk_snapshots.csv")
381:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
382: 
383:     fieldnames = [
384:         "tick_id",
385:         "timestamp_utc",
386:         "snapshot_id",
387:         "entry_timestamp_utc",
388:         "side",
389:         "position",
390:         "price",
391:         "current_score",
392:         "market_regime",
393:         "atr_quality",
394:         "shadow_risk_level",
395:         "shadow_risk_name",
```

### Context 70

```text
377:         current_score=current_score,
378:     )
379: 
380:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_risk_snapshots.csv")
381:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
382: 
383:     fieldnames = [
384:         "tick_id",
385:         "timestamp_utc",
386:         "snapshot_id",
387:         "entry_timestamp_utc",
388:         "side",
389:         "position",
390:         "price",
391:         "current_score",
392:         "market_regime",
393:         "atr_quality",
394:         "shadow_risk_level",
395:         "shadow_risk_name",
396:         "shadow_risk_reason",
397:         "shadow_risk_score",
398:         "regime_mismatch_score",
399:         "atr_stress_score",
400:         "adverse_score_pressure",
401:         "meta_state_score",
402:         "meta_state_bucket",
403:         "position_multiplier",
404:         "runtime_position_multiplier",
405:         "meta_state_enabled",
```

### Context 71

```text
381:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
382: 
383:     fieldnames = [
384:         "tick_id",
385:         "timestamp_utc",
386:         "snapshot_id",
387:         "entry_timestamp_utc",
388:         "side",
389:         "position",
390:         "price",
391:         "current_score",
392:         "market_regime",
393:         "atr_quality",
394:         "shadow_risk_level",
395:         "shadow_risk_name",
396:         "shadow_risk_reason",
397:         "shadow_risk_score",
398:         "regime_mismatch_score",
399:         "atr_stress_score",
400:         "adverse_score_pressure",
401:         "meta_state_score",
402:         "meta_state_bucket",
403:         "position_multiplier",
404:         "runtime_position_multiplier",
405:         "meta_state_enabled",
406:     ]
407: 
408:     exists = os.path.exists(out_path)
409: 
```

### Context 72

```text
387:         "entry_timestamp_utc",
388:         "side",
389:         "position",
390:         "price",
391:         "current_score",
392:         "market_regime",
393:         "atr_quality",
394:         "shadow_risk_level",
395:         "shadow_risk_name",
396:         "shadow_risk_reason",
397:         "shadow_risk_score",
398:         "regime_mismatch_score",
399:         "atr_stress_score",
400:         "adverse_score_pressure",
401:         "meta_state_score",
402:         "meta_state_bucket",
403:         "position_multiplier",
404:         "runtime_position_multiplier",
405:         "meta_state_enabled",
406:     ]
407: 
408:     exists = os.path.exists(out_path)
409: 
410:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
411:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
412: 
413:         if not exists:
414:             writer.writeheader()
415: 
```

### Context 73

```text
388:         "side",
389:         "position",
390:         "price",
391:         "current_score",
392:         "market_regime",
393:         "atr_quality",
394:         "shadow_risk_level",
395:         "shadow_risk_name",
396:         "shadow_risk_reason",
397:         "shadow_risk_score",
398:         "regime_mismatch_score",
399:         "atr_stress_score",
400:         "adverse_score_pressure",
401:         "meta_state_score",
402:         "meta_state_bucket",
403:         "position_multiplier",
404:         "runtime_position_multiplier",
405:         "meta_state_enabled",
406:     ]
407: 
408:     exists = os.path.exists(out_path)
409: 
410:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
411:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
412: 
413:         if not exists:
414:             writer.writeheader()
415: 
416:         writer.writerow(
```

### Context 74

```text
389:         "position",
390:         "price",
391:         "current_score",
392:         "market_regime",
393:         "atr_quality",
394:         "shadow_risk_level",
395:         "shadow_risk_name",
396:         "shadow_risk_reason",
397:         "shadow_risk_score",
398:         "regime_mismatch_score",
399:         "atr_stress_score",
400:         "adverse_score_pressure",
401:         "meta_state_score",
402:         "meta_state_bucket",
403:         "position_multiplier",
404:         "runtime_position_multiplier",
405:         "meta_state_enabled",
406:     ]
407: 
408:     exists = os.path.exists(out_path)
409: 
410:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
411:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
412: 
413:         if not exists:
414:             writer.writeheader()
415: 
416:         writer.writerow(
417:             {
```

### Context 75

```text
390:         "price",
391:         "current_score",
392:         "market_regime",
393:         "atr_quality",
394:         "shadow_risk_level",
395:         "shadow_risk_name",
396:         "shadow_risk_reason",
397:         "shadow_risk_score",
398:         "regime_mismatch_score",
399:         "atr_stress_score",
400:         "adverse_score_pressure",
401:         "meta_state_score",
402:         "meta_state_bucket",
403:         "position_multiplier",
404:         "runtime_position_multiplier",
405:         "meta_state_enabled",
406:     ]
407: 
408:     exists = os.path.exists(out_path)
409: 
410:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
411:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
412: 
413:         if not exists:
414:             writer.writeheader()
415: 
416:         writer.writerow(
417:             {
418:                 "tick_id": int(tick_id),
```

### Context 76

```text
391:         "current_score",
392:         "market_regime",
393:         "atr_quality",
394:         "shadow_risk_level",
395:         "shadow_risk_name",
396:         "shadow_risk_reason",
397:         "shadow_risk_score",
398:         "regime_mismatch_score",
399:         "atr_stress_score",
400:         "adverse_score_pressure",
401:         "meta_state_score",
402:         "meta_state_bucket",
403:         "position_multiplier",
404:         "runtime_position_multiplier",
405:         "meta_state_enabled",
406:     ]
407: 
408:     exists = os.path.exists(out_path)
409: 
410:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
411:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
412: 
413:         if not exists:
414:             writer.writeheader()
415: 
416:         writer.writerow(
417:             {
418:                 "tick_id": int(tick_id),
419:                 "timestamp_utc": str(timestamp_utc),
```

### Context 77

```text
411:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
412: 
413:         if not exists:
414:             writer.writeheader()
415: 
416:         writer.writerow(
417:             {
418:                 "tick_id": int(tick_id),
419:                 "timestamp_utc": str(timestamp_utc),
420:                 "snapshot_id": str(snapshot_id),
421:                 "entry_timestamp_utc": str(getattr(state.s2_position, "entry_timestamp_utc", "")),
422:                 "side": side,
423:                 "position": position,
424:                 "price": float(getattr(features, "price", 0.0)),
425:                 "current_score": int(current_score),
426:                 "market_regime": regime_label,
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
```

### Context 78

```text
415: 
416:         writer.writerow(
417:             {
418:                 "tick_id": int(tick_id),
419:                 "timestamp_utc": str(timestamp_utc),
420:                 "snapshot_id": str(snapshot_id),
421:                 "entry_timestamp_utc": str(getattr(state.s2_position, "entry_timestamp_utc", "")),
422:                 "side": side,
423:                 "position": position,
424:                 "price": float(getattr(features, "price", 0.0)),
425:                 "current_score": int(current_score),
426:                 "market_regime": regime_label,
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
```

### Context 79

```text
421:                 "entry_timestamp_utc": str(getattr(state.s2_position, "entry_timestamp_utc", "")),
422:                 "side": side,
423:                 "position": position,
424:                 "price": float(getattr(features, "price", 0.0)),
425:                 "current_score": int(current_score),
426:                 "market_regime": regime_label,
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
```

### Context 80

```text
422:                 "side": side,
423:                 "position": position,
424:                 "price": float(getattr(features, "price", 0.0)),
425:                 "current_score": int(current_score),
426:                 "market_regime": regime_label,
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
```

### Context 81

```text
423:                 "position": position,
424:                 "price": float(getattr(features, "price", 0.0)),
425:                 "current_score": int(current_score),
426:                 "market_regime": regime_label,
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
```

### Context 82

```text
424:                 "price": float(getattr(features, "price", 0.0)),
425:                 "current_score": int(current_score),
426:                 "market_regime": regime_label,
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
```

### Context 83

```text
425:                 "current_score": int(current_score),
426:                 "market_regime": regime_label,
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
```

### Context 84

```text
426:                 "market_regime": regime_label,
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
```

### Context 85

```text
427:                 "atr_quality": atr_quality,
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
455:     if executed != 1:
```

### Context 86

```text
428:                 "shadow_risk_level": int(risk_level),
429:                 "shadow_risk_name": str(risk_name),
430:                 "shadow_risk_reason": str(reason),
431:                 "shadow_risk_score": float(risk_components["shadow_risk_score"]),
432:                 "regime_mismatch_score": float(risk_components["regime_mismatch_score"]),
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
455:     if executed != 1:
456:         return
```

### Context 87

```text
433:                 "atr_stress_score": float(risk_components["atr_stress_score"]),
434:                 "adverse_score_pressure": float(risk_components["adverse_score_pressure"]),
435:                 "meta_state_score": build_meta_state_shadow(int(current_score))["meta_state_score"],
436:                 "meta_state_bucket": build_meta_state_shadow(int(current_score))["meta_state_bucket"],
437:                 "position_multiplier": build_meta_state_shadow(int(current_score))["position_multiplier"],
438:                 "runtime_position_multiplier": resolve_position_multiplier(int(current_score))[0],
439:                 "meta_state_enabled": 0,
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
455:     if executed != 1:
456:         return
457: 
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
```

### Context 88

```text
440:             }
441:         )
442: 
443: def _append_passive_shadow_entry_multiplier(
444:     *,
445:     repo_root: str,
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
455:     if executed != 1:
456:         return
457: 
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
```

### Context 89

```text
446:     tick_id: int,
447:     timestamp_utc: str,
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
455:     if executed != 1:
456:         return
457: 
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
```

### Context 90

```text
448:     snapshot_id: str,
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
455:     if executed != 1:
456:         return
457: 
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
```

### Context 91

```text
449:     exec_decision,
450:     current_score: int,
451: ) -> None:
452:     action = str(getattr(exec_decision, "action", "")).strip().upper()
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
455:     if executed != 1:
456:         return
457: 
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
```

### Context 92

```text
453:     executed = int(getattr(exec_decision, "executed", 0))
454: 
455:     if executed != 1:
456:         return
457: 
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
```

### Context 93

```text
455:     if executed != 1:
456:         return
457: 
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
```

### Context 94

```text
457: 
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
```

### Context 95

```text
458:     if action not in ("OPEN_LONG", "OPEN_SHORT", "BUY", "SELL"):
459:         return
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
```

### Context 96

```text
460: 
461:     side_after = str(getattr(exec_decision, "side_after", "")).strip().lower()
462: 
463:     side_aware_score = int(current_score)
464:     if side_after == "short":
465:         side_aware_score = -side_aware_score
466: 
467:     shadow = build_meta_state_shadow(int(side_aware_score))
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
```

### Context 97

```text
468:     effective_multiplier = resolve_position_multiplier(int(side_aware_score))[0]
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
489: 
490:     exists = os.path.exists(out_path)
491: 
492:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
493:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
494: 
495:         if not exists:
496:             writer.writeheader()
```

### Context 98

```text
469: 
470:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
489: 
490:     exists = os.path.exists(out_path)
491: 
492:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
493:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
494: 
495:         if not exists:
496:             writer.writeheader()
497: 
```

### Context 99

```text
471:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
489: 
490:     exists = os.path.exists(out_path)
491: 
492:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
493:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
494: 
495:         if not exists:
496:             writer.writeheader()
497: 
498:         writer.writerow(
499:             {
```

### Context 100

```text
472: 
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
489: 
490:     exists = os.path.exists(out_path)
491: 
492:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
493:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
494: 
495:         if not exists:
496:             writer.writeheader()
497: 
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
```

### Context 101

```text
473:     fieldnames = [
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
489: 
490:     exists = os.path.exists(out_path)
491: 
492:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
493:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
494: 
495:         if not exists:
496:             writer.writeheader()
497: 
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
```

### Context 102

```text
474:         "tick_id",
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
489: 
490:     exists = os.path.exists(out_path)
491: 
492:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
493:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
494: 
495:         if not exists:
496:             writer.writeheader()
497: 
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
```

### Context 103

```text
475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
489: 
490:     exists = os.path.exists(out_path)
491: 
492:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
493:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
494: 
495:         if not exists:
496:             writer.writeheader()
497: 
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
```

### Context 104

```text
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",
482:         "side_aware_score",
483:         "entry_meta_state_score",
484:         "entry_meta_state_bucket",
485:         "entry_shadow_multiplier",
486:         "entry_effective_runtime_multiplier",
487:         "meta_state_enabled",
488:     ]
489: 
490:     exists = os.path.exists(out_path)
491: 
492:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
493:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
494: 
495:         if not exists:
496:             writer.writeheader()
497: 
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
```

### Context 105

```text
494: 
495:         if not exists:
496:             writer.writeheader()
497: 
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),
508:                 "side_aware_score": int(side_aware_score),
509:                 "entry_meta_state_score": float(shadow["meta_state_score"]),
510:                 "entry_meta_state_bucket": str(shadow["meta_state_bucket"]),
511:                 "entry_shadow_multiplier": float(shadow["position_multiplier"]),
512:                 "entry_effective_runtime_multiplier": float(effective_multiplier),
513:                 "meta_state_enabled": 0,
514:             }
515:         )
516: 
517: 
518: 
519: def _append_passive_shadow_close_accounting(
520:     *,
521:     repo_root: str,
522:     tick_id: int,
```

### Context 106

```text
495:         if not exists:
496:             writer.writeheader()
497: 
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),
508:                 "side_aware_score": int(side_aware_score),
509:                 "entry_meta_state_score": float(shadow["meta_state_score"]),
510:                 "entry_meta_state_bucket": str(shadow["meta_state_bucket"]),
511:                 "entry_shadow_multiplier": float(shadow["position_multiplier"]),
512:                 "entry_effective_runtime_multiplier": float(effective_multiplier),
513:                 "meta_state_enabled": 0,
514:             }
515:         )
516: 
517: 
518: 
519: def _append_passive_shadow_close_accounting(
520:     *,
521:     repo_root: str,
522:     tick_id: int,
523:     timestamp_utc: str,
```

### Context 107

```text
497: 
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),
508:                 "side_aware_score": int(side_aware_score),
509:                 "entry_meta_state_score": float(shadow["meta_state_score"]),
510:                 "entry_meta_state_bucket": str(shadow["meta_state_bucket"]),
511:                 "entry_shadow_multiplier": float(shadow["position_multiplier"]),
512:                 "entry_effective_runtime_multiplier": float(effective_multiplier),
513:                 "meta_state_enabled": 0,
514:             }
515:         )
516: 
517: 
518: 
519: def _append_passive_shadow_close_accounting(
520:     *,
521:     repo_root: str,
522:     tick_id: int,
523:     timestamp_utc: str,
524:     snapshot_id: str,
525:     exec_decision,
```

### Context 108

```text
498:         writer.writerow(
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),
508:                 "side_aware_score": int(side_aware_score),
509:                 "entry_meta_state_score": float(shadow["meta_state_score"]),
510:                 "entry_meta_state_bucket": str(shadow["meta_state_bucket"]),
511:                 "entry_shadow_multiplier": float(shadow["position_multiplier"]),
512:                 "entry_effective_runtime_multiplier": float(effective_multiplier),
513:                 "meta_state_enabled": 0,
514:             }
515:         )
516: 
517: 
518: 
519: def _append_passive_shadow_close_accounting(
520:     *,
521:     repo_root: str,
522:     tick_id: int,
523:     timestamp_utc: str,
524:     snapshot_id: str,
525:     exec_decision,
526: ) -> None:
```

### Context 109

```text
499:             {
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),
508:                 "side_aware_score": int(side_aware_score),
509:                 "entry_meta_state_score": float(shadow["meta_state_score"]),
510:                 "entry_meta_state_bucket": str(shadow["meta_state_bucket"]),
511:                 "entry_shadow_multiplier": float(shadow["position_multiplier"]),
512:                 "entry_effective_runtime_multiplier": float(effective_multiplier),
513:                 "meta_state_enabled": 0,
514:             }
515:         )
516: 
517: 
518: 
519: def _append_passive_shadow_close_accounting(
520:     *,
521:     repo_root: str,
522:     tick_id: int,
523:     timestamp_utc: str,
524:     snapshot_id: str,
525:     exec_decision,
526: ) -> None:
527:     action = str(getattr(exec_decision, "action", "")).strip().upper()
```

### Context 110

```text
500:                 "tick_id": int(tick_id),
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),
508:                 "side_aware_score": int(side_aware_score),
509:                 "entry_meta_state_score": float(shadow["meta_state_score"]),
510:                 "entry_meta_state_bucket": str(shadow["meta_state_bucket"]),
511:                 "entry_shadow_multiplier": float(shadow["position_multiplier"]),
512:                 "entry_effective_runtime_multiplier": float(effective_multiplier),
513:                 "meta_state_enabled": 0,
514:             }
515:         )
516: 
517: 
518: 
519: def _append_passive_shadow_close_accounting(
520:     *,
521:     repo_root: str,
522:     tick_id: int,
523:     timestamp_utc: str,
524:     snapshot_id: str,
525:     exec_decision,
526: ) -> None:
527:     action = str(getattr(exec_decision, "action", "")).strip().upper()
528:     executed = int(getattr(exec_decision, "executed", 0))
```

### Context 111

```text
501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),
508:                 "side_aware_score": int(side_aware_score),
509:                 "entry_meta_state_score": float(shadow["meta_state_score"]),
510:                 "entry_meta_state_bucket": str(shadow["meta_state_bucket"]),
511:                 "entry_shadow_multiplier": float(shadow["position_multiplier"]),
512:                 "entry_effective_runtime_multiplier": float(effective_multiplier),
513:                 "meta_state_enabled": 0,
514:             }
515:         )
516: 
517: 
518: 
519: def _append_passive_shadow_close_accounting(
520:     *,
521:     repo_root: str,
522:     tick_id: int,
523:     timestamp_utc: str,
524:     snapshot_id: str,
525:     exec_decision,
526: ) -> None:
527:     action = str(getattr(exec_decision, "action", "")).strip().upper()
528:     executed = int(getattr(exec_decision, "executed", 0))
529: 
```

### Context 112

```text
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),
508:                 "side_aware_score": int(side_aware_score),
509:                 "entry_meta_state_score": float(shadow["meta_state_score"]),
510:                 "entry_meta_state_bucket": str(shadow["meta_state_bucket"]),
511:                 "entry_shadow_multiplier": float(shadow["position_multiplier"]),
512:                 "entry_effective_runtime_multiplier": float(effective_multiplier),
513:                 "meta_state_enabled": 0,
514:             }
515:         )
516: 
517: 
518: 
519: def _append_passive_shadow_close_accounting(
520:     *,
521:     repo_root: str,
522:     tick_id: int,
523:     timestamp_utc: str,
524:     snapshot_id: str,
525:     exec_decision,
526: ) -> None:
527:     action = str(getattr(exec_decision, "action", "")).strip().upper()
528:     executed = int(getattr(exec_decision, "executed", 0))
529: 
530:     if executed != 1:
```

### Context 113

```text
521:     repo_root: str,
522:     tick_id: int,
523:     timestamp_utc: str,
524:     snapshot_id: str,
525:     exec_decision,
526: ) -> None:
527:     action = str(getattr(exec_decision, "action", "")).strip().upper()
528:     executed = int(getattr(exec_decision, "executed", 0))
529: 
530:     if executed != 1:
531:         return
532: 
533:     if not action.startswith("CLOSE") and not action.startswith("SL") and not action.startswith("TP"):
534:         return
535: 
536:     trades_path = os.path.join(repo_root, "live_logs", "trades_l1.jsonl")
537:     entry_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
538:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_close_accounting.csv")
539: 
540:     if not os.path.exists(trades_path):
541:         return
542: 
543:     if not os.path.exists(entry_path):
544:         return
545: 
546:     import json
547: 
548:     last_trade = None
549:     with open(trades_path, "r", encoding="utf-8") as fh:
```

### Context 114

```text
524:     snapshot_id: str,
525:     exec_decision,
526: ) -> None:
527:     action = str(getattr(exec_decision, "action", "")).strip().upper()
528:     executed = int(getattr(exec_decision, "executed", 0))
529: 
530:     if executed != 1:
531:         return
532: 
533:     if not action.startswith("CLOSE") and not action.startswith("SL") and not action.startswith("TP"):
534:         return
535: 
536:     trades_path = os.path.join(repo_root, "live_logs", "trades_l1.jsonl")
537:     entry_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
538:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_close_accounting.csv")
539: 
540:     if not os.path.exists(trades_path):
541:         return
542: 
543:     if not os.path.exists(entry_path):
544:         return
545: 
546:     import json
547: 
548:     last_trade = None
549:     with open(trades_path, "r", encoding="utf-8") as fh:
550:         for line in fh:
551:             s = line.strip()
552:             if s:
```

### Context 115

```text
527:     action = str(getattr(exec_decision, "action", "")).strip().upper()
528:     executed = int(getattr(exec_decision, "executed", 0))
529: 
530:     if executed != 1:
531:         return
532: 
533:     if not action.startswith("CLOSE") and not action.startswith("SL") and not action.startswith("TP"):
534:         return
535: 
536:     trades_path = os.path.join(repo_root, "live_logs", "trades_l1.jsonl")
537:     entry_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
538:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_close_accounting.csv")
539: 
540:     if not os.path.exists(trades_path):
541:         return
542: 
543:     if not os.path.exists(entry_path):
544:         return
545: 
546:     import json
547: 
548:     last_trade = None
549:     with open(trades_path, "r", encoding="utf-8") as fh:
550:         for line in fh:
551:             s = line.strip()
552:             if s:
553:                 last_trade = json.loads(s)
554: 
555:     if not last_trade:
```

### Context 116

```text
531:         return
532: 
533:     if not action.startswith("CLOSE") and not action.startswith("SL") and not action.startswith("TP"):
534:         return
535: 
536:     trades_path = os.path.join(repo_root, "live_logs", "trades_l1.jsonl")
537:     entry_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
538:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_close_accounting.csv")
539: 
540:     if not os.path.exists(trades_path):
541:         return
542: 
543:     if not os.path.exists(entry_path):
544:         return
545: 
546:     import json
547: 
548:     last_trade = None
549:     with open(trades_path, "r", encoding="utf-8") as fh:
550:         for line in fh:
551:             s = line.strip()
552:             if s:
553:                 last_trade = json.loads(s)
554: 
555:     if not last_trade:
556:         return
557: 
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
```

### Context 117

```text
533:     if not action.startswith("CLOSE") and not action.startswith("SL") and not action.startswith("TP"):
534:         return
535: 
536:     trades_path = os.path.join(repo_root, "live_logs", "trades_l1.jsonl")
537:     entry_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
538:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_close_accounting.csv")
539: 
540:     if not os.path.exists(trades_path):
541:         return
542: 
543:     if not os.path.exists(entry_path):
544:         return
545: 
546:     import json
547: 
548:     last_trade = None
549:     with open(trades_path, "r", encoding="utf-8") as fh:
550:         for line in fh:
551:             s = line.strip()
552:             if s:
553:                 last_trade = json.loads(s)
554: 
555:     if not last_trade:
556:         return
557: 
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
560:     real_pnl = float(last_trade.get("pnl", 0.0))
561: 
```

### Context 118

```text
534:         return
535: 
536:     trades_path = os.path.join(repo_root, "live_logs", "trades_l1.jsonl")
537:     entry_path = os.path.join(repo_root, "live_logs", "passive_shadow_entry_multipliers.csv")
538:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_close_accounting.csv")
539: 
540:     if not os.path.exists(trades_path):
541:         return
542: 
543:     if not os.path.exists(entry_path):
544:         return
545: 
546:     import json
547: 
548:     last_trade = None
549:     with open(trades_path, "r", encoding="utf-8") as fh:
550:         for line in fh:
551:             s = line.strip()
552:             if s:
553:                 last_trade = json.loads(s)
554: 
555:     if not last_trade:
556:         return
557: 
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
560:     real_pnl = float(last_trade.get("pnl", 0.0))
561: 
562:     entry_multiplier = None
```

### Context 119

```text
546:     import json
547: 
548:     last_trade = None
549:     with open(trades_path, "r", encoding="utf-8") as fh:
550:         for line in fh:
551:             s = line.strip()
552:             if s:
553:                 last_trade = json.loads(s)
554: 
555:     if not last_trade:
556:         return
557: 
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
560:     real_pnl = float(last_trade.get("pnl", 0.0))
561: 
562:     entry_multiplier = None
563: 
564:     with open(entry_path, "r", newline="", encoding="utf-8") as fh:
565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
```

### Context 120

```text
548:     last_trade = None
549:     with open(trades_path, "r", encoding="utf-8") as fh:
550:         for line in fh:
551:             s = line.strip()
552:             if s:
553:                 last_trade = json.loads(s)
554: 
555:     if not last_trade:
556:         return
557: 
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
560:     real_pnl = float(last_trade.get("pnl", 0.0))
561: 
562:     entry_multiplier = None
563: 
564:     with open(entry_path, "r", newline="", encoding="utf-8") as fh:
565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
575: 
576:     shadow_pnl = real_pnl * entry_multiplier
```

### Context 121

```text
552:             if s:
553:                 last_trade = json.loads(s)
554: 
555:     if not last_trade:
556:         return
557: 
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
560:     real_pnl = float(last_trade.get("pnl", 0.0))
561: 
562:     entry_multiplier = None
563: 
564:     with open(entry_path, "r", newline="", encoding="utf-8") as fh:
565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
575: 
576:     shadow_pnl = real_pnl * entry_multiplier
577: 
578:     start_capital = 10000.0
579:     previous_shadow_equity = start_capital
580: 
```

### Context 122

```text
554: 
555:     if not last_trade:
556:         return
557: 
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
560:     real_pnl = float(last_trade.get("pnl", 0.0))
561: 
562:     entry_multiplier = None
563: 
564:     with open(entry_path, "r", newline="", encoding="utf-8") as fh:
565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
575: 
576:     shadow_pnl = real_pnl * entry_multiplier
577: 
578:     start_capital = 10000.0
579:     previous_shadow_equity = start_capital
580: 
581:     if os.path.exists(out_path):
582:         try:
```

### Context 123

```text
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
560:     real_pnl = float(last_trade.get("pnl", 0.0))
561: 
562:     entry_multiplier = None
563: 
564:     with open(entry_path, "r", newline="", encoding="utf-8") as fh:
565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
575: 
576:     shadow_pnl = real_pnl * entry_multiplier
577: 
578:     start_capital = 10000.0
579:     previous_shadow_equity = start_capital
580: 
581:     if os.path.exists(out_path):
582:         try:
583:             import pandas as pd
584:             prev_df = pd.read_csv(out_path)
585:             if len(prev_df) > 0 and "shadow_equity_after" in prev_df.columns:
586:                 previous_shadow_equity = float(prev_df["shadow_equity_after"].iloc[-1])
```

### Context 124

```text
561: 
562:     entry_multiplier = None
563: 
564:     with open(entry_path, "r", newline="", encoding="utf-8") as fh:
565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
575: 
576:     shadow_pnl = real_pnl * entry_multiplier
577: 
578:     start_capital = 10000.0
579:     previous_shadow_equity = start_capital
580: 
581:     if os.path.exists(out_path):
582:         try:
583:             import pandas as pd
584:             prev_df = pd.read_csv(out_path)
585:             if len(prev_df) > 0 and "shadow_equity_after" in prev_df.columns:
586:                 previous_shadow_equity = float(prev_df["shadow_equity_after"].iloc[-1])
587:         except Exception:
588:             previous_shadow_equity = start_capital
589: 
```

### Context 125

```text
563: 
564:     with open(entry_path, "r", newline="", encoding="utf-8") as fh:
565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
575: 
576:     shadow_pnl = real_pnl * entry_multiplier
577: 
578:     start_capital = 10000.0
579:     previous_shadow_equity = start_capital
580: 
581:     if os.path.exists(out_path):
582:         try:
583:             import pandas as pd
584:             prev_df = pd.read_csv(out_path)
585:             if len(prev_df) > 0 and "shadow_equity_after" in prev_df.columns:
586:                 previous_shadow_equity = float(prev_df["shadow_equity_after"].iloc[-1])
587:         except Exception:
588:             previous_shadow_equity = start_capital
589: 
590:     shadow_equity_before = previous_shadow_equity
591:     shadow_equity_after = shadow_equity_before + shadow_pnl
```

### Context 126

```text
564:     with open(entry_path, "r", newline="", encoding="utf-8") as fh:
565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
575: 
576:     shadow_pnl = real_pnl * entry_multiplier
577: 
578:     start_capital = 10000.0
579:     previous_shadow_equity = start_capital
580: 
581:     if os.path.exists(out_path):
582:         try:
583:             import pandas as pd
584:             prev_df = pd.read_csv(out_path)
585:             if len(prev_df) > 0 and "shadow_equity_after" in prev_df.columns:
586:                 previous_shadow_equity = float(prev_df["shadow_equity_after"].iloc[-1])
587:         except Exception:
588:             previous_shadow_equity = start_capital
589: 
590:     shadow_equity_before = previous_shadow_equity
591:     shadow_equity_after = shadow_equity_before + shadow_pnl
592:     shadow_return_pct = (shadow_equity_after - start_capital) / start_capital
```

### Context 127

```text
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))
572: 
573:     if entry_multiplier is None:
574:         entry_multiplier = 1.0
575: 
576:     shadow_pnl = real_pnl * entry_multiplier
577: 
578:     start_capital = 10000.0
579:     previous_shadow_equity = start_capital
580: 
581:     if os.path.exists(out_path):
582:         try:
583:             import pandas as pd
584:             prev_df = pd.read_csv(out_path)
585:             if len(prev_df) > 0 and "shadow_equity_after" in prev_df.columns:
586:                 previous_shadow_equity = float(prev_df["shadow_equity_after"].iloc[-1])
587:         except Exception:
588:             previous_shadow_equity = start_capital
589: 
590:     shadow_equity_before = previous_shadow_equity
591:     shadow_equity_after = shadow_equity_before + shadow_pnl
592:     shadow_return_pct = (shadow_equity_after - start_capital) / start_capital
593: 
594:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
```

### Context 128

```text
582:         try:
583:             import pandas as pd
584:             prev_df = pd.read_csv(out_path)
585:             if len(prev_df) > 0 and "shadow_equity_after" in prev_df.columns:
586:                 previous_shadow_equity = float(prev_df["shadow_equity_after"].iloc[-1])
587:         except Exception:
588:             previous_shadow_equity = start_capital
589: 
590:     shadow_equity_before = previous_shadow_equity
591:     shadow_equity_after = shadow_equity_before + shadow_pnl
592:     shadow_return_pct = (shadow_equity_after - start_capital) / start_capital
593: 
594:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
595: 
596:     fieldnames = [
597:         "tick_id",
598:         "timestamp_utc",
599:         "snapshot_id",
600:         "action",
601:         "entry_timestamp_utc",
602:         "side",
603:         "real_pnl",
604:         "entry_shadow_multiplier",
605:         "shadow_pnl",
606:         "shadow_equity_before",
607:         "shadow_equity_after",
608:         "shadow_return_pct",
609:     ]
610: 
```

### Context 129

```text
591:     shadow_equity_after = shadow_equity_before + shadow_pnl
592:     shadow_return_pct = (shadow_equity_after - start_capital) / start_capital
593: 
594:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
595: 
596:     fieldnames = [
597:         "tick_id",
598:         "timestamp_utc",
599:         "snapshot_id",
600:         "action",
601:         "entry_timestamp_utc",
602:         "side",
603:         "real_pnl",
604:         "entry_shadow_multiplier",
605:         "shadow_pnl",
606:         "shadow_equity_before",
607:         "shadow_equity_after",
608:         "shadow_return_pct",
609:     ]
610: 
611:     exists = os.path.exists(out_path)
612: 
613:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
614:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
615: 
616:         if not exists:
617:             writer.writeheader()
618: 
619:         writer.writerow(
```

### Context 130

```text
594:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
595: 
596:     fieldnames = [
597:         "tick_id",
598:         "timestamp_utc",
599:         "snapshot_id",
600:         "action",
601:         "entry_timestamp_utc",
602:         "side",
603:         "real_pnl",
604:         "entry_shadow_multiplier",
605:         "shadow_pnl",
606:         "shadow_equity_before",
607:         "shadow_equity_after",
608:         "shadow_return_pct",
609:     ]
610: 
611:     exists = os.path.exists(out_path)
612: 
613:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
614:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
615: 
616:         if not exists:
617:             writer.writeheader()
618: 
619:         writer.writerow(
620:             {
621:                 "tick_id": int(tick_id),
622:                 "timestamp_utc": str(timestamp_utc),
```

### Context 131

```text
598:         "timestamp_utc",
599:         "snapshot_id",
600:         "action",
601:         "entry_timestamp_utc",
602:         "side",
603:         "real_pnl",
604:         "entry_shadow_multiplier",
605:         "shadow_pnl",
606:         "shadow_equity_before",
607:         "shadow_equity_after",
608:         "shadow_return_pct",
609:     ]
610: 
611:     exists = os.path.exists(out_path)
612: 
613:     with open(out_path, "a", newline="", encoding="utf-8") as fh:
614:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
615: 
616:         if not exists:
617:             writer.writeheader()
618: 
619:         writer.writerow(
620:             {
621:                 "tick_id": int(tick_id),
622:                 "timestamp_utc": str(timestamp_utc),
623:                 "snapshot_id": str(snapshot_id),
624:                 "action": action,
625:                 "entry_timestamp_utc": entry_ts,
626:                 "side": side,
```

### Context 132

```text
615: 
616:         if not exists:
617:             writer.writeheader()
618: 
619:         writer.writerow(
620:             {
621:                 "tick_id": int(tick_id),
622:                 "timestamp_utc": str(timestamp_utc),
623:                 "snapshot_id": str(snapshot_id),
624:                 "action": action,
625:                 "entry_timestamp_utc": entry_ts,
626:                 "side": side,
627:                 "real_pnl": float(real_pnl),
628:                 "entry_shadow_multiplier": float(entry_multiplier),
629:                 "shadow_pnl": float(shadow_pnl),
630:                 "shadow_equity_before": float(shadow_equity_before),
631:                 "shadow_equity_after": float(shadow_equity_after),
632:                 "shadow_return_pct": float(shadow_return_pct),
633:             }
634:         )
635: 
636: 
637: 
638: def _append_trade_lifecycle_snapshot(
639:     *,
640:     repo_root: str,
641:     tick_id: int,
642:     timestamp_utc: str,
643:     snapshot_id: str,
```

### Context 133

```text
618: 
619:         writer.writerow(
620:             {
621:                 "tick_id": int(tick_id),
622:                 "timestamp_utc": str(timestamp_utc),
623:                 "snapshot_id": str(snapshot_id),
624:                 "action": action,
625:                 "entry_timestamp_utc": entry_ts,
626:                 "side": side,
627:                 "real_pnl": float(real_pnl),
628:                 "entry_shadow_multiplier": float(entry_multiplier),
629:                 "shadow_pnl": float(shadow_pnl),
630:                 "shadow_equity_before": float(shadow_equity_before),
631:                 "shadow_equity_after": float(shadow_equity_after),
632:                 "shadow_return_pct": float(shadow_return_pct),
633:             }
634:         )
635: 
636: 
637: 
638: def _append_trade_lifecycle_snapshot(
639:     *,
640:     repo_root: str,
641:     tick_id: int,
642:     timestamp_utc: str,
643:     snapshot_id: str,
644:     state,
645:     features,
646:     regime,
```

### Context 134

```text
622:                 "timestamp_utc": str(timestamp_utc),
623:                 "snapshot_id": str(snapshot_id),
624:                 "action": action,
625:                 "entry_timestamp_utc": entry_ts,
626:                 "side": side,
627:                 "real_pnl": float(real_pnl),
628:                 "entry_shadow_multiplier": float(entry_multiplier),
629:                 "shadow_pnl": float(shadow_pnl),
630:                 "shadow_equity_before": float(shadow_equity_before),
631:                 "shadow_equity_after": float(shadow_equity_after),
632:                 "shadow_return_pct": float(shadow_return_pct),
633:             }
634:         )
635: 
636: 
637: 
638: def _append_trade_lifecycle_snapshot(
639:     *,
640:     repo_root: str,
641:     tick_id: int,
642:     timestamp_utc: str,
643:     snapshot_id: str,
644:     state,
645:     features,
646:     regime,
647: ) -> None:
648:     if not hasattr(state, "s2_position"):
649:         return
650: 
```

### Context 135

```text
639:     *,
640:     repo_root: str,
641:     tick_id: int,
642:     timestamp_utc: str,
643:     snapshot_id: str,
644:     state,
645:     features,
646:     regime,
647: ) -> None:
648:     if not hasattr(state, "s2_position"):
649:         return
650: 
651:     pos = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
652:     if pos not in ("LONG", "SHORT"):
653:         return
654: 
655:     side = str(getattr(state.s2_position, "side", "")).strip().lower()
656:     entry_price = _safe_float_lifecycle(getattr(state.s2_position, "entry_price", None), 0.0)
657:     size = _safe_float_lifecycle(
658:         getattr(
659:             state.s2_position,
660:             "position_size",
661:             getattr(state.s2_position, "size", 0.0),
662:         ),
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
```

### Context 136

```text
643:     snapshot_id: str,
644:     state,
645:     features,
646:     regime,
647: ) -> None:
648:     if not hasattr(state, "s2_position"):
649:         return
650: 
651:     pos = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
652:     if pos not in ("LONG", "SHORT"):
653:         return
654: 
655:     side = str(getattr(state.s2_position, "side", "")).strip().lower()
656:     entry_price = _safe_float_lifecycle(getattr(state.s2_position, "entry_price", None), 0.0)
657:     size = _safe_float_lifecycle(
658:         getattr(
659:             state.s2_position,
660:             "position_size",
661:             getattr(state.s2_position, "size", 0.0),
662:         ),
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return
669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
```

### Context 137

```text
646:     regime,
647: ) -> None:
648:     if not hasattr(state, "s2_position"):
649:         return
650: 
651:     pos = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
652:     if pos not in ("LONG", "SHORT"):
653:         return
654: 
655:     side = str(getattr(state.s2_position, "side", "")).strip().lower()
656:     entry_price = _safe_float_lifecycle(getattr(state.s2_position, "entry_price", None), 0.0)
657:     size = _safe_float_lifecycle(
658:         getattr(
659:             state.s2_position,
660:             "position_size",
661:             getattr(state.s2_position, "size", 0.0),
662:         ),
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return
669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
672:     if duration_sec < 60.0:
673:         return
674: 
```

### Context 138

```text
655:     side = str(getattr(state.s2_position, "side", "")).strip().lower()
656:     entry_price = _safe_float_lifecycle(getattr(state.s2_position, "entry_price", None), 0.0)
657:     size = _safe_float_lifecycle(
658:         getattr(
659:             state.s2_position,
660:             "position_size",
661:             getattr(state.s2_position, "size", 0.0),
662:         ),
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return
669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
672:     if duration_sec < 60.0:
673:         return
674: 
675:     if int(duration_sec) % 60 != 0:
676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size
683: 
```

### Context 139

```text
657:     size = _safe_float_lifecycle(
658:         getattr(
659:             state.s2_position,
660:             "position_size",
661:             getattr(state.s2_position, "size", 0.0),
662:         ),
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return
669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
672:     if duration_sec < 60.0:
673:         return
674: 
675:     if int(duration_sec) % 60 != 0:
676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size
683: 
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
```

### Context 140

```text
658:         getattr(
659:             state.s2_position,
660:             "position_size",
661:             getattr(state.s2_position, "size", 0.0),
662:         ),
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return
669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
672:     if duration_sec < 60.0:
673:         return
674: 
675:     if int(duration_sec) % 60 != 0:
676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size
683: 
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
686: 
```

### Context 141

```text
660:             "position_size",
661:             getattr(state.s2_position, "size", 0.0),
662:         ),
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return
669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
672:     if duration_sec < 60.0:
673:         return
674: 
675:     if int(duration_sec) % 60 != 0:
676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size
683: 
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
686: 
687:     fieldnames = [
688:         "timestamp_utc",
```

### Context 142

```text
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return
669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
672:     if duration_sec < 60.0:
673:         return
674: 
675:     if int(duration_sec) % 60 != 0:
676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size
683: 
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
686: 
687:     fieldnames = [
688:         "timestamp_utc",
689:         "tick",
690:         "snapshot_id",
691:         "side",
```

### Context 143

```text
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return
669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
672:     if duration_sec < 60.0:
673:         return
674: 
675:     if int(duration_sec) % 60 != 0:
676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size
683: 
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
686: 
687:     fieldnames = [
688:         "timestamp_utc",
689:         "tick",
690:         "snapshot_id",
691:         "side",
692:         "duration_sec",
693:         "entry_timestamp_utc",
694:         "entry_price",
```

### Context 144

```text
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)
671: 
672:     if duration_sec < 60.0:
673:         return
674: 
675:     if int(duration_sec) % 60 != 0:
676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size
683: 
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
686: 
687:     fieldnames = [
688:         "timestamp_utc",
689:         "tick",
690:         "snapshot_id",
691:         "side",
692:         "duration_sec",
693:         "entry_timestamp_utc",
694:         "entry_price",
695:         "current_price",
696:         "position_size",
697:         "unrealized_pnl",
698:         "current_score",
```

### Context 145

```text
672:     if duration_sec < 60.0:
673:         return
674: 
675:     if int(duration_sec) % 60 != 0:
676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)
679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size
683: 
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
686: 
687:     fieldnames = [
688:         "timestamp_utc",
689:         "tick",
690:         "snapshot_id",
691:         "side",
692:         "duration_sec",
693:         "entry_timestamp_utc",
694:         "entry_price",
695:         "current_price",
696:         "position_size",
697:         "unrealized_pnl",
698:         "current_score",
699:         "market_regime",
700:         "atr_quality",
```

### Context 146

```text
683: 
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
686: 
687:     fieldnames = [
688:         "timestamp_utc",
689:         "tick",
690:         "snapshot_id",
691:         "side",
692:         "duration_sec",
693:         "entry_timestamp_utc",
694:         "entry_price",
695:         "current_price",
696:         "position_size",
697:         "unrealized_pnl",
698:         "current_score",
699:         "market_regime",
700:         "atr_quality",
701:         "ma200_signal",
702:         "atr_signal",
703:         "mfi_signal",
704:     ]
705: 
706:     write_header = not os.path.isfile(out_path)
707: 
708:     with open(out_path, "a", encoding="utf-8", newline="") as fh:
709:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
710:         if write_header:
711:             writer.writeheader()
```

### Context 147

```text
684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)
686: 
687:     fieldnames = [
688:         "timestamp_utc",
689:         "tick",
690:         "snapshot_id",
691:         "side",
692:         "duration_sec",
693:         "entry_timestamp_utc",
694:         "entry_price",
695:         "current_price",
696:         "position_size",
697:         "unrealized_pnl",
698:         "current_score",
699:         "market_regime",
700:         "atr_quality",
701:         "ma200_signal",
702:         "atr_signal",
703:         "mfi_signal",
704:     ]
705: 
706:     write_header = not os.path.isfile(out_path)
707: 
708:     with open(out_path, "a", encoding="utf-8", newline="") as fh:
709:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
710:         if write_header:
711:             writer.writeheader()
712:         writer.writerow(
```

### Context 148

```text
688:         "timestamp_utc",
689:         "tick",
690:         "snapshot_id",
691:         "side",
692:         "duration_sec",
693:         "entry_timestamp_utc",
694:         "entry_price",
695:         "current_price",
696:         "position_size",
697:         "unrealized_pnl",
698:         "current_score",
699:         "market_regime",
700:         "atr_quality",
701:         "ma200_signal",
702:         "atr_signal",
703:         "mfi_signal",
704:     ]
705: 
706:     write_header = not os.path.isfile(out_path)
707: 
708:     with open(out_path, "a", encoding="utf-8", newline="") as fh:
709:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
710:         if write_header:
711:             writer.writeheader()
712:         writer.writerow(
713:             {
714:                 "timestamp_utc": timestamp_utc,
715:                 "tick": int(tick_id),
716:                 "snapshot_id": snapshot_id,
```

### Context 149

```text
691:         "side",
692:         "duration_sec",
693:         "entry_timestamp_utc",
694:         "entry_price",
695:         "current_price",
696:         "position_size",
697:         "unrealized_pnl",
698:         "current_score",
699:         "market_regime",
700:         "atr_quality",
701:         "ma200_signal",
702:         "atr_signal",
703:         "mfi_signal",
704:     ]
705: 
706:     write_header = not os.path.isfile(out_path)
707: 
708:     with open(out_path, "a", encoding="utf-8", newline="") as fh:
709:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
710:         if write_header:
711:             writer.writeheader()
712:         writer.writerow(
713:             {
714:                 "timestamp_utc": timestamp_utc,
715:                 "tick": int(tick_id),
716:                 "snapshot_id": snapshot_id,
717:                 "side": side,
718:                 "duration_sec": float(duration_sec),
719:                 "entry_timestamp_utc": entry_ts,
```

### Context 150

```text
693:         "entry_timestamp_utc",
694:         "entry_price",
695:         "current_price",
696:         "position_size",
697:         "unrealized_pnl",
698:         "current_score",
699:         "market_regime",
700:         "atr_quality",
701:         "ma200_signal",
702:         "atr_signal",
703:         "mfi_signal",
704:     ]
705: 
706:     write_header = not os.path.isfile(out_path)
707: 
708:     with open(out_path, "a", encoding="utf-8", newline="") as fh:
709:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
710:         if write_header:
711:             writer.writeheader()
712:         writer.writerow(
713:             {
714:                 "timestamp_utc": timestamp_utc,
715:                 "tick": int(tick_id),
716:                 "snapshot_id": snapshot_id,
717:                 "side": side,
718:                 "duration_sec": float(duration_sec),
719:                 "entry_timestamp_utc": entry_ts,
720:                 "entry_price": float(entry_price),
721:                 "current_price": float(current_price),
```

### Context 151

```text
709:         writer = csv.DictWriter(fh, fieldnames=fieldnames)
710:         if write_header:
711:             writer.writeheader()
712:         writer.writerow(
713:             {
714:                 "timestamp_utc": timestamp_utc,
715:                 "tick": int(tick_id),
716:                 "snapshot_id": snapshot_id,
717:                 "side": side,
718:                 "duration_sec": float(duration_sec),
719:                 "entry_timestamp_utc": entry_ts,
720:                 "entry_price": float(entry_price),
721:                 "current_price": float(current_price),
722:                 "position_size": float(size),
723:                 "unrealized_pnl": float(unrealized_pnl),
724:                 "current_score": int(getattr(regime, "score", 0)),
725:                 "market_regime": str(getattr(regime, "label", "")),
726:                 "atr_quality": str(getattr(regime, "risk_label", "")),
727:                 "ma200_signal": int(getattr(regime, "ma200_signal", 0)),
728:                 "atr_signal": int(getattr(regime, "atr_signal", 0)),
729:                 "mfi_signal": int(getattr(regime, "mfi_signal", 0)),
730:             }
731:         )
732: 
733: 
734: 
735: def run_l1_loop_step1234567(
736:     repo_root: str,
737:     max_ticks: int = 6,
```

### Context 152

```text
710:         if write_header:
711:             writer.writeheader()
712:         writer.writerow(
713:             {
714:                 "timestamp_utc": timestamp_utc,
715:                 "tick": int(tick_id),
716:                 "snapshot_id": snapshot_id,
717:                 "side": side,
718:                 "duration_sec": float(duration_sec),
719:                 "entry_timestamp_utc": entry_ts,
720:                 "entry_price": float(entry_price),
721:                 "current_price": float(current_price),
722:                 "position_size": float(size),
723:                 "unrealized_pnl": float(unrealized_pnl),
724:                 "current_score": int(getattr(regime, "score", 0)),
725:                 "market_regime": str(getattr(regime, "label", "")),
726:                 "atr_quality": str(getattr(regime, "risk_label", "")),
727:                 "ma200_signal": int(getattr(regime, "ma200_signal", 0)),
728:                 "atr_signal": int(getattr(regime, "atr_signal", 0)),
729:                 "mfi_signal": int(getattr(regime, "mfi_signal", 0)),
730:             }
731:         )
732: 
733: 
734: 
735: def run_l1_loop_step1234567(
736:     repo_root: str,
737:     max_ticks: int = 6,
738:     max_run_seconds: float | None = None,
```

### Context 153

```text
714:                 "timestamp_utc": timestamp_utc,
715:                 "tick": int(tick_id),
716:                 "snapshot_id": snapshot_id,
717:                 "side": side,
718:                 "duration_sec": float(duration_sec),
719:                 "entry_timestamp_utc": entry_ts,
720:                 "entry_price": float(entry_price),
721:                 "current_price": float(current_price),
722:                 "position_size": float(size),
723:                 "unrealized_pnl": float(unrealized_pnl),
724:                 "current_score": int(getattr(regime, "score", 0)),
725:                 "market_regime": str(getattr(regime, "label", "")),
726:                 "atr_quality": str(getattr(regime, "risk_label", "")),
727:                 "ma200_signal": int(getattr(regime, "ma200_signal", 0)),
728:                 "atr_signal": int(getattr(regime, "atr_signal", 0)),
729:                 "mfi_signal": int(getattr(regime, "mfi_signal", 0)),
730:             }
731:         )
732: 
733: 
734: 
735: def run_l1_loop_step1234567(
736:     repo_root: str,
737:     max_ticks: int = 6,
738:     max_run_seconds: float | None = None,
739: ) -> int:
740:     system_state_id = f"L1P-{uuid.uuid4().hex[:11]}"
741: 
742:     cfg = load_runtime_config(repo_root)
```

### Context 154

```text
717:                 "side": side,
718:                 "duration_sec": float(duration_sec),
719:                 "entry_timestamp_utc": entry_ts,
720:                 "entry_price": float(entry_price),
721:                 "current_price": float(current_price),
722:                 "position_size": float(size),
723:                 "unrealized_pnl": float(unrealized_pnl),
724:                 "current_score": int(getattr(regime, "score", 0)),
725:                 "market_regime": str(getattr(regime, "label", "")),
726:                 "atr_quality": str(getattr(regime, "risk_label", "")),
727:                 "ma200_signal": int(getattr(regime, "ma200_signal", 0)),
728:                 "atr_signal": int(getattr(regime, "atr_signal", 0)),
729:                 "mfi_signal": int(getattr(regime, "mfi_signal", 0)),
730:             }
731:         )
732: 
733: 
734: 
735: def run_l1_loop_step1234567(
736:     repo_root: str,
737:     max_ticks: int = 6,
738:     max_run_seconds: float | None = None,
739: ) -> int:
740:     system_state_id = f"L1P-{uuid.uuid4().hex[:11]}"
741: 
742:     cfg = load_runtime_config(repo_root)
743:     log = L1Logger(cfg.log_path)
744: 
745:     startup_validation = validate_startup(
```

### Context 155

```text
719:                 "entry_timestamp_utc": entry_ts,
720:                 "entry_price": float(entry_price),
721:                 "current_price": float(current_price),
722:                 "position_size": float(size),
723:                 "unrealized_pnl": float(unrealized_pnl),
724:                 "current_score": int(getattr(regime, "score", 0)),
725:                 "market_regime": str(getattr(regime, "label", "")),
726:                 "atr_quality": str(getattr(regime, "risk_label", "")),
727:                 "ma200_signal": int(getattr(regime, "ma200_signal", 0)),
728:                 "atr_signal": int(getattr(regime, "atr_signal", 0)),
729:                 "mfi_signal": int(getattr(regime, "mfi_signal", 0)),
730:             }
731:         )
732: 
733: 
734: 
735: def run_l1_loop_step1234567(
736:     repo_root: str,
737:     max_ticks: int = 6,
738:     max_run_seconds: float | None = None,
739: ) -> int:
740:     system_state_id = f"L1P-{uuid.uuid4().hex[:11]}"
741: 
742:     cfg = load_runtime_config(repo_root)
743:     log = L1Logger(cfg.log_path)
744: 
745:     startup_validation = validate_startup(
746:         repo_root=Path(cfg.repo_root),
747:         market_csv_path=str(cfg.market_csv_path),
```

### Context 156

```text
755:             event="system_stop",
756:             severity="ERROR",
757:             system_state_id=system_state_id,
758:             fields={
759:                 "reason": "startup_validation_failed",
760:                 "startup_validation_failed_checks": ",".join(x.code for x in startup_validation.issues),
761:                 "startup_validation_failed_details": " | ".join(x.code + ":" + x.detail for x in startup_validation.issues),
762:             },
763:         )
764:         log.close()
765:         return 1
766: 
767:     state = load_or_init_state(cfg.state_dir, system_state_id=system_state_id)
768:     validation = validate_loaded_state(state)
769:     startup_recovery = _apply_startup_recovery_to_state(cfg, state)
770: 
771:     if int(startup_recovery.get("hard_fail", 0)) == 1:
772:         log.log(
773:             category="L1",
774:             event="system_stop",
775:             severity="ERROR",
776:             system_state_id=getattr(state, "system_state_id", system_state_id),
777:             fields={
778:                 "reason": str(startup_recovery.get("reason", "startup_hard_fail")),
779:                 "startup_recovery_enabled": int(startup_recovery.get("enabled", 0)),
780:                 "startup_recovery_applied": int(startup_recovery.get("applied", 0)),
781:                 "reconciliation_failed_checks": str(startup_recovery.get("reconciliation_failed_checks", "")),
782:                 "reconciliation_failed_details": str(startup_recovery.get("reconciliation_failed_details", "")),
783:             },
```

### Context 157

```text
776:             system_state_id=getattr(state, "system_state_id", system_state_id),
777:             fields={
778:                 "reason": str(startup_recovery.get("reason", "startup_hard_fail")),
779:                 "startup_recovery_enabled": int(startup_recovery.get("enabled", 0)),
780:                 "startup_recovery_applied": int(startup_recovery.get("applied", 0)),
781:                 "reconciliation_failed_checks": str(startup_recovery.get("reconciliation_failed_checks", "")),
782:                 "reconciliation_failed_details": str(startup_recovery.get("reconciliation_failed_details", "")),
783:             },
784:         )
785:         log.close()
786:         return 1
787: 
788:     market = CSVMarketFeed(
789:         csv_path=os.path.join(repo_root, cfg.market_csv_path),
790:         symbol=cfg.symbol,
791:         resume_after_snapshot_id=getattr(state, "last_snapshot_id", ""),
792:     )
793: 
794:     clock = TickClock(decision_tick_seconds=cfg.decision_tick_seconds)
795: 
796:     deadline_monotonic: float | None = None
797:     if max_run_seconds is not None and max_run_seconds > 0:
798:         deadline_monotonic = time.monotonic() + float(max_run_seconds)
799: 
800:     try:
801:         clock.start()
802: 
803:         log.log(
804:             category="L1",
```

### Context 158

```text
841: 
842:         while state.is_running and clock.tick_id < max_ticks:
843:             if deadline_monotonic is not None and time.monotonic() >= deadline_monotonic:
844:                 log.log(
845:                     category="L1",
846:                     event="system_stop",
847:                     severity="INFO",
848:                     system_state_id=state.system_state_id,
849:                     fields={"reason": "max_run_seconds_reached", "tick": clock.tick_id},
850:                 )
851:                 return 0
852: 
853:             tick = clock.next_tick()
854: 
855:             try:
856:                 snapshot = market.next_snapshot()
857:             except StopIteration:
858:                 log.log(
859:                     category="L1",
860:                     event="system_stop",
861:                     severity="INFO",
862:                     system_state_id=state.system_state_id,
863:                     fields={"reason": "market_feed_exhausted", "tick": tick.tick_id},
864:                 )
865:                 return 0
866: 
867:             features = build_feature_snapshot(snapshot)
868:             regime = detect_regime(features)
869: 
```

### Context 159

```text
855:             try:
856:                 snapshot = market.next_snapshot()
857:             except StopIteration:
858:                 log.log(
859:                     category="L1",
860:                     event="system_stop",
861:                     severity="INFO",
862:                     system_state_id=state.system_state_id,
863:                     fields={"reason": "market_feed_exhausted", "tick": tick.tick_id},
864:                 )
865:                 return 0
866: 
867:             features = build_feature_snapshot(snapshot)
868:             regime = detect_regime(features)
869: 
870:             current_position = "FLAT"
871:             if hasattr(state, "s2_position") and hasattr(state.s2_position, "position"):
872:                 current_position = str(state.s2_position.position).strip().upper()
873: 
874:             intent_1m_raw, forced = compute_1m_intent_raw(
875:                 cfg=cfg,
876:                 tick_id=tick.tick_id,
877:                 features=features,
878:                 current_position=current_position,
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
```

### Context 160

```text
864:                 )
865:                 return 0
866: 
867:             features = build_feature_snapshot(snapshot)
868:             regime = detect_regime(features)
869: 
870:             current_position = "FLAT"
871:             if hasattr(state, "s2_position") and hasattr(state.s2_position, "position"):
872:                 current_position = str(state.s2_position.position).strip().upper()
873: 
874:             intent_1m_raw, forced = compute_1m_intent_raw(
875:                 cfg=cfg,
876:                 tick_id=tick.tick_id,
877:                 features=features,
878:                 current_position=current_position,
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
```

### Context 161

```text
876:                 tick_id=tick.tick_id,
877:                 features=features,
878:                 current_position=current_position,
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
```

### Context 162

```text
877:                 features=features,
878:                 current_position=current_position,
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
```

### Context 163

```text
878:                 current_position=current_position,
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
```

### Context 164

```text
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
```

### Context 165

```text
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
```

### Context 166

```text
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
909:             )
```

### Context 167

```text
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
909:             )
910: 
```

### Context 168

```text
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
909:             )
910: 
911:             log.log(
```

### Context 169

```text
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
909:             )
910: 
911:             log.log(
912:                 category="L1",
```

### Context 170

```text
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
909:             )
910: 
911:             log.log(
912:                 category="L1",
913:                 event="clock_tick",
```

### Context 171

```text
886:                 rsi_signal=features.signal("rsi_signal"),
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
909:             )
910: 
911:             log.log(
912:                 category="L1",
913:                 event="clock_tick",
914:                 severity="INFO",
```

### Context 172

```text
887:                 macd_signal=features.signal("macd_signal"),
888:                 bollinger_signal=features.signal("bollinger_signal"),
889:                 ma200_signal=features.signal("ma200_signal"),
890:                 stoch_signal=features.signal("stoch_signal"),
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
909:             )
910: 
911:             log.log(
912:                 category="L1",
913:                 event="clock_tick",
914:                 severity="INFO",
915:                 system_state_id=state.system_state_id,
```

### Context 173

```text
891:                 atr_signal=features.signal("atr_signal"),
892:                 ema50_signal=features.signal("ema50_signal"),
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
895:                 mfi_signal=features.signal("mfi_signal"),
896:                 obv_signal=features.signal("obv_signal"),
897:                 roc_signal=features.signal("roc_signal"),
898:             )
899: 
900:             fused = fuse_intent_with_5m_timing(
901:                 intent_1m_raw=intent_1m_raw,
902:                 vote_5m_direction=vote_v1.direction,
903:                 vote_5m_strength=vote_v1.strength,
904:                 vote_5m_seed_id=vote_v1.seed_id,
905:                 thresh=cfg.thresh_5m,
906:                 allow_long=int(features.allow_long),
907:                 allow_short=int(features.allow_short),
908:                 current_position=current_position,
909:             )
910: 
911:             log.log(
912:                 category="L1",
913:                 event="clock_tick",
914:                 severity="INFO",
915:                 system_state_id=state.system_state_id,
916:                 fields={
917:                     "tick": tick.tick_id,
918:                     "tick_started_utc": tick.tick_started_utc,
919:                     "decision_tick_seconds": cfg.decision_tick_seconds,
```

### Context 174

```text
941:                 category="REGIME",
942:                 event="regime_snapshot",
943:                 severity="INFO",
944:                 system_state_id=state.system_state_id,
945:                 fields={
946:                     "tick": tick.tick_id,
947:                     "snapshot_id": features.snapshot_id,
948:                     "timestamp_utc": features.timestamp_utc,
949:                     "regime_label": regime.label,
950:                     "risk_label": regime.risk_label,
951:                     "ma200_signal": regime.ma200_signal,
952:                     "atr_signal": regime.atr_signal,
953:                     "mfi_signal": regime.mfi_signal,
954:                     "entry_score": regime.score,
955:                 },
956:             )
957: 
958:             log.log(
959:                 category="L3",
960:                 event="intent_fused",
961:                 severity="INFO",
962:                 system_state_id=state.system_state_id,
963:                 intent_id=fused.intent_id,
964:                 fields={
965:                     "tick": tick.tick_id,
966:                     "allow_long": int(features.allow_long),
967:                     "allow_short": int(features.allow_short),
968:                     "intent_1m_raw": intent_1m_raw,
969:                     "intent_final": fused.intent_final,
```

### Context 175

```text
943:                 severity="INFO",
944:                 system_state_id=state.system_state_id,
945:                 fields={
946:                     "tick": tick.tick_id,
947:                     "snapshot_id": features.snapshot_id,
948:                     "timestamp_utc": features.timestamp_utc,
949:                     "regime_label": regime.label,
950:                     "risk_label": regime.risk_label,
951:                     "ma200_signal": regime.ma200_signal,
952:                     "atr_signal": regime.atr_signal,
953:                     "mfi_signal": regime.mfi_signal,
954:                     "entry_score": regime.score,
955:                 },
956:             )
957: 
958:             log.log(
959:                 category="L3",
960:                 event="intent_fused",
961:                 severity="INFO",
962:                 system_state_id=state.system_state_id,
963:                 intent_id=fused.intent_id,
964:                 fields={
965:                     "tick": tick.tick_id,
966:                     "allow_long": int(features.allow_long),
967:                     "allow_short": int(features.allow_short),
968:                     "intent_1m_raw": intent_1m_raw,
969:                     "intent_final": fused.intent_final,
970:                     "reason_code": fused.reason_code,
971:                     "current_position": fused.current_position,
```

### Context 176

```text
944:                 system_state_id=state.system_state_id,
945:                 fields={
946:                     "tick": tick.tick_id,
947:                     "snapshot_id": features.snapshot_id,
948:                     "timestamp_utc": features.timestamp_utc,
949:                     "regime_label": regime.label,
950:                     "risk_label": regime.risk_label,
951:                     "ma200_signal": regime.ma200_signal,
952:                     "atr_signal": regime.atr_signal,
953:                     "mfi_signal": regime.mfi_signal,
954:                     "entry_score": regime.score,
955:                 },
956:             )
957: 
958:             log.log(
959:                 category="L3",
960:                 event="intent_fused",
961:                 severity="INFO",
962:                 system_state_id=state.system_state_id,
963:                 intent_id=fused.intent_id,
964:                 fields={
965:                     "tick": tick.tick_id,
966:                     "allow_long": int(features.allow_long),
967:                     "allow_short": int(features.allow_short),
968:                     "intent_1m_raw": intent_1m_raw,
969:                     "intent_final": fused.intent_final,
970:                     "reason_code": fused.reason_code,
971:                     "current_position": fused.current_position,
972:                     "test_forced_intent": int(forced),
```

### Context 177

```text
958:             log.log(
959:                 category="L3",
960:                 event="intent_fused",
961:                 severity="INFO",
962:                 system_state_id=state.system_state_id,
963:                 intent_id=fused.intent_id,
964:                 fields={
965:                     "tick": tick.tick_id,
966:                     "allow_long": int(features.allow_long),
967:                     "allow_short": int(features.allow_short),
968:                     "intent_1m_raw": intent_1m_raw,
969:                     "intent_final": fused.intent_final,
970:                     "reason_code": fused.reason_code,
971:                     "current_position": fused.current_position,
972:                     "test_forced_intent": int(forced),
973:                     "thresh": cfg.thresh_5m,
974:                     "vote_5m_direction": vote_v1.direction,
975:                     "vote_5m_seed_id": str(vote_v1.seed_id),
976:                     "vote_5m_strength": float(vote_v1.strength),
977:                 },
978:             )
979: 
980:             _append_trade_lifecycle_snapshot(
981:                 repo_root=repo_root,
982:                 tick_id=tick.tick_id,
983:                 timestamp_utc=str(features.timestamp_utc),
984:                 snapshot_id=str(features.snapshot_id),
985:                 state=state,
986:                 features=features,
```

### Context 178

```text
998:             )
999: 
1000:             exec_decision = apply_paper_execution(
1001:                 state=state,
1002:                 intent_final=fused.intent_final,
1003:                 price=float(features.price),
1004:                 timestamp_utc=str(features.timestamp_utc),
1005:                 position_size=1.0,
1006:             )
1007: 
1008:             _append_passive_shadow_entry_multiplier(
1009:                 repo_root=repo_root,
1010:                 tick_id=tick.tick_id,
1011:                 timestamp_utc=str(features.timestamp_utc),
1012:                 snapshot_id=str(features.snapshot_id),
1013:                 exec_decision=exec_decision,
1014:                 current_score=int(regime.score),
1015:             )
1016: 
1017:             _append_passive_shadow_close_accounting(
1018:                 repo_root=repo_root,
1019:                 tick_id=tick.tick_id,
1020:                 timestamp_utc=str(features.timestamp_utc),
1021:                 snapshot_id=str(features.snapshot_id),
1022:                 exec_decision=exec_decision,
1023:             )
1024: 
1025:             log.log(
1026:                 category="L5",
```

### Context 179

```text
1004:                 timestamp_utc=str(features.timestamp_utc),
1005:                 position_size=1.0,
1006:             )
1007: 
1008:             _append_passive_shadow_entry_multiplier(
1009:                 repo_root=repo_root,
1010:                 tick_id=tick.tick_id,
1011:                 timestamp_utc=str(features.timestamp_utc),
1012:                 snapshot_id=str(features.snapshot_id),
1013:                 exec_decision=exec_decision,
1014:                 current_score=int(regime.score),
1015:             )
1016: 
1017:             _append_passive_shadow_close_accounting(
1018:                 repo_root=repo_root,
1019:                 tick_id=tick.tick_id,
1020:                 timestamp_utc=str(features.timestamp_utc),
1021:                 snapshot_id=str(features.snapshot_id),
1022:                 exec_decision=exec_decision,
1023:             )
1024: 
1025:             log.log(
1026:                 category="L5",
1027:                 event="execution",
1028:                 severity="INFO",
1029:                 system_state_id=state.system_state_id,
1030:                 intent_id=fused.intent_id,
1031:                 fields={
1032:                     "tick": tick.tick_id,
```

### Context 180

```text
1028:                 severity="INFO",
1029:                 system_state_id=state.system_state_id,
1030:                 intent_id=fused.intent_id,
1031:                 fields={
1032:                     "tick": tick.tick_id,
1033:                     "action": exec_decision.action,
1034:                     "executed": int(exec_decision.executed),
1035:                     "position_before": exec_decision.position_before,
1036:                     "position_after": exec_decision.position_after,
1037:                     "side_after": exec_decision.side_after,
1038:                     "entry_price": "" if exec_decision.entry_price is None else float(exec_decision.entry_price),
1039:                     "entry_timestamp_utc": exec_decision.entry_timestamp_utc,
1040:                     "reason": exec_decision.reason,
1041:                 },
1042:             )
1043: 
1044:             guard_reason, s4_kill_level = evaluate_guards(cfg=cfg, state=state)
1045:             state.s4_risk.kill_level = s4_kill_level
1046: 
1047:             state.last_snapshot_id = str(features.snapshot_id)
1048:             state.last_timestamp_utc = str(features.timestamp_utc)
1049:             state.last_tick_id = int(tick.tick_id)
1050: 
1051:             if hasattr(state, "s2_position"):
1052:                 if hasattr(state.s2_position, "snapshot_id"):
1053:                     state.s2_position.snapshot_id = str(features.snapshot_id)
1054:                 if hasattr(state.s2_position, "last_intent_id"):
1055:                     state.s2_position.last_intent_id = str(fused.intent_id)
1056: 
```

### Context 181

```text
1029:                 system_state_id=state.system_state_id,
1030:                 intent_id=fused.intent_id,
1031:                 fields={
1032:                     "tick": tick.tick_id,
1033:                     "action": exec_decision.action,
1034:                     "executed": int(exec_decision.executed),
1035:                     "position_before": exec_decision.position_before,
1036:                     "position_after": exec_decision.position_after,
1037:                     "side_after": exec_decision.side_after,
1038:                     "entry_price": "" if exec_decision.entry_price is None else float(exec_decision.entry_price),
1039:                     "entry_timestamp_utc": exec_decision.entry_timestamp_utc,
1040:                     "reason": exec_decision.reason,
1041:                 },
1042:             )
1043: 
1044:             guard_reason, s4_kill_level = evaluate_guards(cfg=cfg, state=state)
1045:             state.s4_risk.kill_level = s4_kill_level
1046: 
1047:             state.last_snapshot_id = str(features.snapshot_id)
1048:             state.last_timestamp_utc = str(features.timestamp_utc)
1049:             state.last_tick_id = int(tick.tick_id)
1050: 
1051:             if hasattr(state, "s2_position"):
1052:                 if hasattr(state.s2_position, "snapshot_id"):
1053:                     state.s2_position.snapshot_id = str(features.snapshot_id)
1054:                 if hasattr(state.s2_position, "last_intent_id"):
1055:                     state.s2_position.last_intent_id = str(fused.intent_id)
1056: 
1057:             if hasattr(state, "s4_risk"):
```

### Context 182

```text
1090:                 },
1091:             )
1092: 
1093:         log.log(
1094:             category="L1",
1095:             event="system_stop",
1096:             severity="INFO",
1097:             system_state_id=state.system_state_id,
1098:             fields={"reason": "max_ticks_reached", "tick": clock.tick_id},
1099:         )
1100:         return 0
1101: 
1102:     finally:
1103:         try:
1104:             market.close()
1105:         except Exception:
1106:             pass
1107:         log.close()
```

## Preliminary Assessment

- If compute_1m_intent_raw emits HOLD unless specific score thresholds are reached, timing cannot create trades alone.
- The audit should identify the raw 1m scoring formula and BUY/SELL thresholds.
- Next step should quantify score distribution in post-fix segments or a new controlled segment.

## Required Next Step

Review this source audit and then run a raw intent score distribution audit.

## Result

Status: PASS
