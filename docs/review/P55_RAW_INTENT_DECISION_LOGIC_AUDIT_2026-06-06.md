# P55 RAW INTENT DECISION LOGIC AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Audit why strong post-fix entry scores in P54 still produced HOLD raw intents.

## Background

P54 showed entry_score distribution in the P49 segment:

- +4: 6
- +3: 10
- -4: 1
- -3: 3

Despite this, raw intent distribution was:

- HOLD: 100
- BUY: 0
- SELL: 0

## Target File

live_l1/core/intent.py

## Relevant Source Context

### Context 1

```text
4: # ASCII-only.
5: 
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
35: 
36: _STATE = _IntentState()
37: 
38: 
```

### Context 2

```text
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
```

### Context 3

```text
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

### Context 4

```text
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
59:         out: dict[str, float] = {}
60:         for k, v in obj.items():
61:             try:
62:                 out[str(k)] = float(v)
63:             except Exception:
64:                 continue
65:         return out if out else None
66:     except Exception:
```

### Context 5

```text
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
```

### Context 6

```text
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
72:         weights = _load_l1_signal_weights()
73:         if weights:
74:             return int(round(features.weighted_signal_score(weights)))
75:         return int(
76:             features.signal("rsi_signal")
77:             + features.signal("bollinger_signal")
78:             + features.signal("stoch_signal")
79:             + features.signal("cci_signal")
80:         )
```

### Context 7

```text
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
```

### Context 8

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
84: 
85: def _normalize_position(value: object) -> Position:
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
```

### Context 9

```text
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
86:     s = "" if value is None else str(value).strip().upper()
87:     if s == "LONG":
88:         return "LONG"
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
```

### Context 10

```text
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
89:     if s == "SHORT":
90:         return "SHORT"
91:     return "FLAT"
92: 
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
```

### Context 11

```text
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

### Context 12

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
93: 
94: def _maybe_reset_on_tick_reset(tick_id: int) -> None:
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
```

### Context 13

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
95:     last_tick = _STATE.last_tick_id
96:     if last_tick is None:
97:         return
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
```

### Context 14

```text
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
98:     if tick_id <= last_tick:
99:         reset_intent_state()
100: 
101: 
102: def _push_score(score: int) -> None:
103:     _STATE.recent_scores.append(int(score))
104:     if len(_STATE.recent_scores) > 6:
```

### Context 15

```text
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
```

### Context 16

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
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
```

### Context 17

```text
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
107: 
108: def _last_n_all_ge(n: int, threshold: int) -> bool:
109:     if len(_STATE.recent_scores) < n:
110:         return False
111:     return all(s >= threshold for s in _STATE.recent_scores[-n:])
112: 
113: 
```

### Context 18

```text
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
```

### Context 19

```text
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
116:         return False
117:     return all(s <= threshold for s in _STATE.recent_scores[-n:])
118: 
119: 
120: def _entry_cooldown_ticks(atr_sig: int) -> int:
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
```

### Context 20

```text
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
121:     if int(atr_sig) == -1:
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
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
122:         return ENTRY_COOLDOWN_BAD_ATR_TICKS
123:     return ENTRY_COOLDOWN_NORMAL_TICKS
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
```

### Context 23

```text
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
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
```

### Context 24

```text
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
124: 
125: 
126: def _in_entry_cooldown(tick_id: int, atr_sig: int) -> bool:
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
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
127:     last = _STATE.last_flat_after_position_tick
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
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
128:     if last is None:
129:         return False
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
```

### Context 27

```text
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
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
```

### Context 28

```text
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
130:     cooldown = _entry_cooldown_ticks(atr_sig)
131:     return (int(tick_id) - int(last)) < int(cooldown)
132: 
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
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
133: 
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
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
134: def _update_position_transition(pos: Position, tick_id: int) -> None:
135:     prev = _STATE.last_position
136:     if prev in ("LONG", "SHORT") and pos == "FLAT":
137:         _STATE.last_flat_after_position_tick = int(tick_id)
138:     _STATE.last_position = pos
139: 
```

### Context 31

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
139: 
140: 
141: def _debug_enabled() -> bool:
142:     v = os.environ.get("L1_INTENT_DEBUG", "")
143:     return v.strip().lower() in ("1", "true", "yes", "on")
144: 
```

### Context 32

```text
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
139: 
140: 
141: def _debug_enabled() -> bool:
142:     v = os.environ.get("L1_INTENT_DEBUG", "")
143:     return v.strip().lower() in ("1", "true", "yes", "on")
144: 
145: 
```

### Context 33

```text
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
145: 
146: def _debug_log_line(
147:     *,
148:     tick_id: int,
149:     current_position: Position,
150:     score: int,
151:     intent: IntentAction,
```

### Context 34

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
148:     tick_id: int,
149:     current_position: Position,
150:     score: int,
151:     intent: IntentAction,
152:     forced: bool,
153:     atr_sig: int = 0,
```

### Context 35

```text
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
```

### Context 36

```text
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
```

### Context 37

```text
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
```

### Context 38

```text
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
```

### Context 39

```text
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

### Context 40

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
183:     cfg,
184:     tick_id: int,
185:     features: FeatureSnapshot,
186:     current_position: str = "FLAT",
187: ) -> Tuple[IntentAction, bool]:
188:     tick_id = int(tick_id)
```

### Context 41

```text
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
183:     cfg,
184:     tick_id: int,
185:     features: FeatureSnapshot,
186:     current_position: str = "FLAT",
187: ) -> Tuple[IntentAction, bool]:
188:     tick_id = int(tick_id)
189:     _maybe_reset_on_tick_reset(tick_id)
```

### Context 42

```text
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
183:     cfg,
184:     tick_id: int,
185:     features: FeatureSnapshot,
186:     current_position: str = "FLAT",
187: ) -> Tuple[IntentAction, bool]:
188:     tick_id = int(tick_id)
189:     _maybe_reset_on_tick_reset(tick_id)
190: 
```

### Context 43

```text
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
```

### Context 44

```text
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
200:             score=0,
201:             intent="HOLD",
202:             forced=False,
203:             atr_sig=0,
204:         )
205:         return ("HOLD", False)
206: 
207:     force_enabled = bool(getattr(cfg, "test_force_intents", False))
208:     if force_enabled:
```

### Context 45

```text
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
```

### Context 46

```text
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
213:         _STATE.recent_scores = []
214: 
215:         if sell_every > 0 and tick_id % sell_every == 0:
216:             _debug_log_line(
217:                 tick_id=tick_id,
218:                 current_position=_normalize_position(current_position),
219:                 score=0,
220:                 intent="SELL",
221:                 forced=True,
```

### Context 47

```text
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
```

### Context 48

```text
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

### Context 49

```text
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
220:                 intent="SELL",
221:                 forced=True,
222:                 atr_sig=0,
223:             )
224:             return ("SELL", True)
225: 
226:         if buy_every > 0 and tick_id % buy_every == 0:
227:             _debug_log_line(
```

### Context 50

```text
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
```

### Context 51

```text
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
232:                 forced=True,
233:                 atr_sig=0,
234:             )
235:             return ("BUY", True)
236: 
237:         _debug_log_line(
238:             tick_id=tick_id,
239:             current_position=_normalize_position(current_position),
240:             score=0,
```

### Context 52

```text
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
```

### Context 53

```text
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

### Context 54

```text
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
239:             current_position=_normalize_position(current_position),
240:             score=0,
241:             intent="HOLD",
242:             forced=True,
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
```

### Context 55

```text
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
243:             atr_sig=0,
244:         )
245:         return ("HOLD", False)
246: 
247:     score = _normalize_score(features)
248:     pos = _normalize_position(current_position)
249: 
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
```

### Context 56

```text
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
```

### Context 57

```text
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

### Context 58

```text
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
250:     _push_score(score)
251:     _update_position_transition(pos, tick_id)
252: 
253:     intent: IntentAction = "HOLD"
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
```

### Context 59

```text
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
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
```

### Context 60

```text
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
254:     atr_sig = int(features.signal("atr_signal"))
255: 
256:     if pos == "FLAT":
257:         ma200_sig = int(features.signal("ma200_signal"))
258:         mfi_sig = int(features.signal("mfi_signal"))
259: 
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
```

### Context 61

```text
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

### Context 62

```text
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
260:         if not _in_entry_cooldown(tick_id, atr_sig):
261:             if ma200_sig == 1 and mfi_sig == 1:
262:                 if atr_sig == -1:
263:                     if _last_n_all_ge(3, 4):
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
```

### Context 63

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
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
```

### Context 64

```text
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
264:                         intent = "BUY"
265:                 else:
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
```

### Context 65

```text
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
266:                     if _last_n_all_ge(3, 3):
267:                         intent = "BUY"
268: 
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
```

### Context 66

```text
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
269:             elif ma200_sig == -1 and mfi_sig == -1:
270:                 if atr_sig == -1:
271:                     if _last_n_all_le(3, -4):
272:                         intent = "SELL"
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
```

### Context 67

```text
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
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
279:             intent = "SELL"
```

### Context 68

```text
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
273:                 else:
274:                     if _last_n_all_le(3, -3):
275:                         intent = "SELL"
276: 
277:     elif pos == "LONG":
278:         if _last_n_all_le(1, -1):
279:             intent = "SELL"
280: 
```

### Context 69

```text
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
279:             intent = "SELL"
280: 
281:     elif pos == "SHORT":
282:         if _last_n_all_ge(2, 2):
283:             intent = "BUY"
284: 
285:     _STATE.last_tick_id = tick_id
286: 
```

### Context 70

```text
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
283:             intent = "BUY"
284: 
285:     _STATE.last_tick_id = tick_id
286: 
287:     _debug_log_line(
288:         tick_id=tick_id,
289:         current_position=pos,
```

### Context 71

```text
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
286: 
287:     _debug_log_line(
288:         tick_id=tick_id,
289:         current_position=pos,
290:         score=score,
291:         intent=intent,
292:         forced=False,
293:         atr_sig=atr_sig,
294:     )
```

### Context 72

```text
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
291:         intent=intent,
292:         forced=False,
293:         atr_sig=atr_sig,
294:     )
295: 
296:     return (intent, False)
```

### Context 73

```text
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
294:     )
295: 
296:     return (intent, False)
```

### Context 74

```text
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

### Context 77

```text
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

## Preliminary Assessment

- This audit captures the raw 1m intent decision logic.
- The next step should compare the exact decision formula against the score fields observed in P54.
- No code changes are introduced in P55.

## Result

Status: PASS
