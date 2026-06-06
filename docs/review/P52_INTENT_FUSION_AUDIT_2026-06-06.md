# P52 INTENT FUSION AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Audit why post-fix runtime timing votes include long/short/none while final intents remain HOLD.

## Background

P51 post-fix segments showed:

- timing long: 38
- timing short: 29
- timing none: 133
- final intent HOLD: 200
- execution NOOP: 200

This suggests the current bottleneck is now 1m raw intent, intent fusion, or gate interaction.

## Target: live_l1/core/intent_fusion.py

exists: True

### Context 1

```text
5: #
6: # Clean separation of responsibilities:
7: # - intent.py: raw 1m intent
8: # - intent_fusion.py: 1m/5m fusion + exit handling only
9: # - market_gate.py: hard market entry filtering
10: #
11: # Policy:
12: # - Exits must always remain possible
13: # - Fusion must NOT hard-block entries via allow_long / allow_short
14: # - allow_long / allow_short are logged for observability only
15: #
16: # Current asymmetric policy:
17: # - BUY from FLAT still requires 5m long confirmation
18: # - SELL from FLAT is primarily driven by 1m and is only blocked by a
19: #   strong opposing 5m long vote
20: #
21: # ASCII-only.
22: 
23: from __future__ import annotations
24: 
25: import uuid
26: from dataclasses import dataclass
27: from typing import Literal, Optional
28: 
29: 
```

### Context 2

```text
6: # Clean separation of responsibilities:
7: # - intent.py: raw 1m intent
8: # - intent_fusion.py: 1m/5m fusion + exit handling only
9: # - market_gate.py: hard market entry filtering
10: #
11: # Policy:
12: # - Exits must always remain possible
13: # - Fusion must NOT hard-block entries via allow_long / allow_short
14: # - allow_long / allow_short are logged for observability only
15: #
16: # Current asymmetric policy:
17: # - BUY from FLAT still requires 5m long confirmation
18: # - SELL from FLAT is primarily driven by 1m and is only blocked by a
19: #   strong opposing 5m long vote
20: #
21: # ASCII-only.
22: 
23: from __future__ import annotations
24: 
25: import uuid
26: from dataclasses import dataclass
27: from typing import Literal, Optional
28: 
29: 
30: Intent = Literal["BUY", "SELL", "HOLD"]
```

### Context 3

```text
9: # - market_gate.py: hard market entry filtering
10: #
11: # Policy:
12: # - Exits must always remain possible
13: # - Fusion must NOT hard-block entries via allow_long / allow_short
14: # - allow_long / allow_short are logged for observability only
15: #
16: # Current asymmetric policy:
17: # - BUY from FLAT still requires 5m long confirmation
18: # - SELL from FLAT is primarily driven by 1m and is only blocked by a
19: #   strong opposing 5m long vote
20: #
21: # ASCII-only.
22: 
23: from __future__ import annotations
24: 
25: import uuid
26: from dataclasses import dataclass
27: from typing import Literal, Optional
28: 
29: 
30: Intent = Literal["BUY", "SELL", "HOLD"]
31: VoteDir = Literal["long", "short", "none"]
32: Position = Literal["FLAT", "LONG", "SHORT"]
33: 
```

### Context 4

```text
10: #
11: # Policy:
12: # - Exits must always remain possible
13: # - Fusion must NOT hard-block entries via allow_long / allow_short
14: # - allow_long / allow_short are logged for observability only
15: #
16: # Current asymmetric policy:
17: # - BUY from FLAT still requires 5m long confirmation
18: # - SELL from FLAT is primarily driven by 1m and is only blocked by a
19: #   strong opposing 5m long vote
20: #
21: # ASCII-only.
22: 
23: from __future__ import annotations
24: 
25: import uuid
26: from dataclasses import dataclass
27: from typing import Literal, Optional
28: 
29: 
30: Intent = Literal["BUY", "SELL", "HOLD"]
31: VoteDir = Literal["long", "short", "none"]
32: Position = Literal["FLAT", "LONG", "SHORT"]
33: 
34: 
```

### Context 5

```text
22: 
23: from __future__ import annotations
24: 
25: import uuid
26: from dataclasses import dataclass
27: from typing import Literal, Optional
28: 
29: 
30: Intent = Literal["BUY", "SELL", "HOLD"]
31: VoteDir = Literal["long", "short", "none"]
32: Position = Literal["FLAT", "LONG", "SHORT"]
33: 
34: 
35: @dataclass(frozen=True)
36: class TimingVote:
37:     direction: VoteDir
38:     strength: float
39:     seed_id: Optional[str] = None
40: 
41: 
42: @dataclass(frozen=True)
43: class FusionDecision:
44:     intent_id: str
45:     intent_final: Intent
46:     reason_code: str
```

### Context 6

```text
39:     seed_id: Optional[str] = None
40: 
41: 
42: @dataclass(frozen=True)
43: class FusionDecision:
44:     intent_id: str
45:     intent_final: Intent
46:     reason_code: str
47:     intent_1m_raw: Intent
48:     vote_5m_direction: VoteDir
49:     vote_5m_strength: float
50:     vote_5m_seed_id: Optional[str]
51:     allow_long: int
52:     allow_short: int
53:     thresh: float
54:     current_position: str
55: 
56: 
57: def _new_intent_id() -> str:
58:     return "IN-" + uuid.uuid4().hex[:12]
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
```

### Context 7

```text
40: 
41: 
42: @dataclass(frozen=True)
43: class FusionDecision:
44:     intent_id: str
45:     intent_final: Intent
46:     reason_code: str
47:     intent_1m_raw: Intent
48:     vote_5m_direction: VoteDir
49:     vote_5m_strength: float
50:     vote_5m_seed_id: Optional[str]
51:     allow_long: int
52:     allow_short: int
53:     thresh: float
54:     current_position: str
55: 
56: 
57: def _new_intent_id() -> str:
58:     return "IN-" + uuid.uuid4().hex[:12]
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
```

### Context 8

```text
41: 
42: @dataclass(frozen=True)
43: class FusionDecision:
44:     intent_id: str
45:     intent_final: Intent
46:     reason_code: str
47:     intent_1m_raw: Intent
48:     vote_5m_direction: VoteDir
49:     vote_5m_strength: float
50:     vote_5m_seed_id: Optional[str]
51:     allow_long: int
52:     allow_short: int
53:     thresh: float
54:     current_position: str
55: 
56: 
57: def _new_intent_id() -> str:
58:     return "IN-" + uuid.uuid4().hex[:12]
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
```

### Context 9

```text
43: class FusionDecision:
44:     intent_id: str
45:     intent_final: Intent
46:     reason_code: str
47:     intent_1m_raw: Intent
48:     vote_5m_direction: VoteDir
49:     vote_5m_strength: float
50:     vote_5m_seed_id: Optional[str]
51:     allow_long: int
52:     allow_short: int
53:     thresh: float
54:     current_position: str
55: 
56: 
57: def _new_intent_id() -> str:
58:     return "IN-" + uuid.uuid4().hex[:12]
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
66:     if v < 0.0:
67:         return 0.0
```

### Context 10

```text
44:     intent_id: str
45:     intent_final: Intent
46:     reason_code: str
47:     intent_1m_raw: Intent
48:     vote_5m_direction: VoteDir
49:     vote_5m_strength: float
50:     vote_5m_seed_id: Optional[str]
51:     allow_long: int
52:     allow_short: int
53:     thresh: float
54:     current_position: str
55: 
56: 
57: def _new_intent_id() -> str:
58:     return "IN-" + uuid.uuid4().hex[:12]
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
66:     if v < 0.0:
67:         return 0.0
68:     if v > 1.0:
```

### Context 11

```text
46:     reason_code: str
47:     intent_1m_raw: Intent
48:     vote_5m_direction: VoteDir
49:     vote_5m_strength: float
50:     vote_5m_seed_id: Optional[str]
51:     allow_long: int
52:     allow_short: int
53:     thresh: float
54:     current_position: str
55: 
56: 
57: def _new_intent_id() -> str:
58:     return "IN-" + uuid.uuid4().hex[:12]
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
66:     if v < 0.0:
67:         return 0.0
68:     if v > 1.0:
69:         return 1.0
70:     return v
```

### Context 12

```text
50:     vote_5m_seed_id: Optional[str]
51:     allow_long: int
52:     allow_short: int
53:     thresh: float
54:     current_position: str
55: 
56: 
57: def _new_intent_id() -> str:
58:     return "IN-" + uuid.uuid4().hex[:12]
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
66:     if v < 0.0:
67:         return 0.0
68:     if v > 1.0:
69:         return 1.0
70:     return v
71: 
72: 
73: def _norm_position(value: object) -> str:
74:     s = "" if value is None else str(value).strip().upper()
```

### Context 13

```text
57: def _new_intent_id() -> str:
58:     return "IN-" + uuid.uuid4().hex[:12]
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
66:     if v < 0.0:
67:         return 0.0
68:     if v > 1.0:
69:         return 1.0
70:     return v
71: 
72: 
73: def _norm_position(value: object) -> str:
74:     s = "" if value is None else str(value).strip().upper()
75:     if s in ("FLAT", "LONG", "SHORT"):
76:         return s
77:     return "FLAT"
78: 
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
```

### Context 14

```text
59: 
60: 
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
66:     if v < 0.0:
67:         return 0.0
68:     if v > 1.0:
69:         return 1.0
70:     return v
71: 
72: 
73: def _norm_position(value: object) -> str:
74:     s = "" if value is None else str(value).strip().upper()
75:     if s in ("FLAT", "LONG", "SHORT"):
76:         return s
77:     return "FLAT"
78: 
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
```

### Context 15

```text
61: def _clamp01(x: float) -> float:
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
66:     if v < 0.0:
67:         return 0.0
68:     if v > 1.0:
69:         return 1.0
70:     return v
71: 
72: 
73: def _norm_position(value: object) -> str:
74:     s = "" if value is None else str(value).strip().upper()
75:     if s in ("FLAT", "LONG", "SHORT"):
76:         return s
77:     return "FLAT"
78: 
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
```

### Context 16

```text
62:     try:
63:         v = float(x)
64:     except Exception:
65:         return 0.0
66:     if v < 0.0:
67:         return 0.0
68:     if v > 1.0:
69:         return 1.0
70:     return v
71: 
72: 
73: def _norm_position(value: object) -> str:
74:     s = "" if value is None else str(value).strip().upper()
75:     if s in ("FLAT", "LONG", "SHORT"):
76:         return s
77:     return "FLAT"
78: 
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
86:     if s in ("sell", "bear", "down"):
```

### Context 17

```text
68:     if v > 1.0:
69:         return 1.0
70:     return v
71: 
72: 
73: def _norm_position(value: object) -> str:
74:     s = "" if value is None else str(value).strip().upper()
75:     if s in ("FLAT", "LONG", "SHORT"):
76:         return s
77:     return "FLAT"
78: 
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
```

### Context 18

```text
69:         return 1.0
70:     return v
71: 
72: 
73: def _norm_position(value: object) -> str:
74:     s = "" if value is None else str(value).strip().upper()
75:     if s in ("FLAT", "LONG", "SHORT"):
76:         return s
77:     return "FLAT"
78: 
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
```

### Context 19

```text
75:     if s in ("FLAT", "LONG", "SHORT"):
76:         return s
77:     return "FLAT"
78: 
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
```

### Context 20

```text
77:     return "FLAT"
78: 
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
```

### Context 21

```text
79: 
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
```

### Context 22

```text
80: def _norm_vote_dir(value: object) -> VoteDir:
81:     s = "" if value is None else str(value).strip().lower()
82:     if s in ("long", "short", "none"):
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
```

### Context 23

```text
83:         return s  # type: ignore[return-value]
84:     if s in ("buy", "bull", "up"):
85:         return "long"
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
```

### Context 24

```text
85:         return "long"
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
```

### Context 25

```text
86:     if s in ("sell", "bear", "down"):
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
```

### Context 26

```text
87:         return "short"
88:     return "none"
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
```

### Context 27

```text
89: 
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
```

### Context 28

```text
90: 
91: def fuse_intent_with_5m_timing(
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
```

### Context 29

```text
92:     *,
93:     intent_1m_raw: Intent,
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
```

### Context 30

```text
94:     vote_5m_direction: VoteDir,
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
```

### Context 31

```text
95:     vote_5m_strength: float,
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
```

### Context 32

```text
96:     thresh: float = 0.60,
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
```

### Context 33

```text
97:     allow_long: int = 1,
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
```

### Context 34

```text
98:     allow_short: int = 1,
99:     vote_5m_seed_id: Optional[str] = None,
100:     current_position: str = "FLAT",
101: ) -> FusionDecision:
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
```

### Context 35

```text
102:     allow_long_i = 1 if int(allow_long) == 1 else 0
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
```

### Context 36

```text
103:     allow_short_i = 1 if int(allow_short) == 1 else 0
104:     s = _clamp01(vote_5m_strength)
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
```

### Context 37

```text
105:     d = _norm_vote_dir(vote_5m_direction)
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
```

### Context 38

```text
106:     pos = _norm_position(current_position)
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
```

### Context 39

```text
107:     t = float(thresh)
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
```

### Context 40

```text
108:     intent_id = _new_intent_id()
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
```

### Context 41

```text
109: 
110:     if intent_1m_raw == "HOLD":
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
```

### Context 42

```text
111:         return FusionDecision(
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
```

### Context 43

```text
112:             intent_id=intent_id,
113:             intent_final="HOLD",
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
```

### Context 44

```text
114:             reason_code="HOLD_RAW",
115:             intent_1m_raw="HOLD",
116:             vote_5m_direction=d,
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
```

### Context 45

```text
117:             vote_5m_strength=s,
118:             vote_5m_seed_id=vote_5m_seed_id,
119:             allow_long=allow_long_i,
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
```

### Context 46

```text
120:             allow_short=allow_short_i,
121:             thresh=t,
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
```

### Context 47

```text
122:             current_position=pos,
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
```

### Context 48

```text
123:         )
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
```

### Context 49

```text
124: 
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
```

### Context 50

```text
125:     if intent_1m_raw == "BUY":
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
```

### Context 51

```text
126:         # Exit from SHORT must always remain possible.
127:         if pos == "SHORT":
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
```

### Context 52

```text
128:             return FusionDecision(
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
```

### Context 53

```text
129:                 intent_id=intent_id,
130:                 intent_final="BUY",
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
```

### Context 54

```text
131:                 reason_code="EXIT_SHORT_ON_1M_BUY",
132:                 intent_1m_raw="BUY",
133:                 vote_5m_direction=d,
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
```

### Context 55

```text
134:                 vote_5m_strength=s,
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
```

### Context 56

```text
135:                 vote_5m_seed_id=vote_5m_seed_id,
136:                 allow_long=allow_long_i,
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
```

### Context 57

```text
137:                 allow_short=allow_short_i,
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
```

### Context 58

```text
138:                 thresh=t,
139:                 current_position=pos,
140:             )
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
```

### Context 59

```text
141: 
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
```

### Context 60

```text
142:         # FLAT -> BUY is now asymmetric like SELL:
143:         # 1m BUY is allowed unless there is a strong opposing short vote.
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
```

### Context 61

```text
144:         if d == "none":
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
```

### Context 62

```text
145:             out = "BUY"
146:             rc = "ASYM_BUY_NO_5M_VOTE"
147:         elif d == "long":
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
```

### Context 63

```text
148:             if s < t:
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
```

### Context 64

```text
149:                 out = "BUY"
150:                 rc = "ASYM_BUY_WEAK_5M_LONG_ALLOWED"
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
```

### Context 65

```text
151:             else:
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
```

### Context 66

```text
152:                 out = "BUY"
153:                 rc = "CONFIRMED_1M_BUY_5M_LONG"
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
```

### Context 67

```text
154:         elif d == "short":
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
```

### Context 68

```text
155:             if s >= t:
156:                 out = "HOLD"
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
```

### Context 69

```text
157:                 rc = "ASYM_BUY_BLOCKED_BY_STRONG_5M_SHORT"
158:             else:
159:                 out = "BUY"
160:                 rc = "ASYM_BUY_WEAK_5M_SHORT_IGNORED"
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
```

### Context 70

```text
161:         else:
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
```

### Context 71

```text
162:             out = "BUY"
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
```

### Context 72

```text
163:             rc = "ASYM_BUY_UNKNOWN_5M_ALLOWED"
164: 
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
```

### Context 73

```text
165:         return FusionDecision(
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
```

### Context 74

```text
166:             intent_id=intent_id,
167:             intent_final=out,
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
```

### Context 75

```text
168:             reason_code=rc,
169:             intent_1m_raw="BUY",
170:             vote_5m_direction=d,
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
```

### Context 76

```text
171:             vote_5m_strength=s,
172:             vote_5m_seed_id=vote_5m_seed_id,
173:             allow_long=allow_long_i,
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
```

### Context 77

```text
174:             allow_short=allow_short_i,
175:             thresh=t,
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
```

### Context 78

```text
176:             current_position=pos,
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
```

### Context 79

```text
177:         )
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
```

### Context 80

```text
178: 
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
```

### Context 81

```text
179:     if intent_1m_raw == "SELL":
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
```

### Context 82

```text
180:         # Exit from LONG must always remain possible.
181:         if pos == "LONG":
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
```

### Context 83

```text
182:             return FusionDecision(
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
```

### Context 84

```text
183:                 intent_id=intent_id,
184:                 intent_final="SELL",
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
```

### Context 85

```text
185:                 reason_code="EXIT_LONG_ON_1M_SELL",
186:                 intent_1m_raw="SELL",
187:                 vote_5m_direction=d,
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
```

### Context 86

```text
188:                 vote_5m_strength=s,
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
```

### Context 87

```text
189:                 vote_5m_seed_id=vote_5m_seed_id,
190:                 allow_long=allow_long_i,
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
```

### Context 88

```text
191:                 allow_short=allow_short_i,
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
```

### Context 89

```text
192:                 thresh=t,
193:                 current_position=pos,
194:             )
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
```

### Context 90

```text
195: 
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
```

### Context 91

```text
196:         # FLAT -> SELL is now asymmetric:
197:         # 1m SELL is allowed unless there is a strong opposing long vote.
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
```

### Context 92

```text
198:         if d == "none":
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
```

### Context 93

```text
199:             out = "SELL"
200:             rc = "ASYM_SELL_NO_5M_VOTE"
201:         elif d == "short":
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
```

### Context 94

```text
202:             if s < t:
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
```

### Context 95

```text
203:                 out = "SELL"
204:                 rc = "ASYM_SELL_WEAK_5M_SHORT_ALLOWED"
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
```

### Context 96

```text
205:             else:
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
```

### Context 97

```text
206:                 out = "SELL"
207:                 rc = "CONFIRMED_1M_SELL_5M_SHORT"
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
```

### Context 98

```text
208:         elif d == "long":
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
```

### Context 99

```text
209:             if s >= t:
210:                 out = "SELL"
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
```

### Context 100

```text
211:                 rc = "ASYM_SELL_STRONG_5M_LONG_IGNORED"
212:             else:
213:                 out = "SELL"
214:                 rc = "ASYM_SELL_WEAK_5M_LONG_IGNORED"
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
```

### Context 101

```text
215:         else:
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
```

### Context 102

```text
216:             out = "SELL"
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
```

### Context 103

```text
217:             rc = "ASYM_SELL_UNKNOWN_5M_ALLOWED"
218: 
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
```

### Context 104

```text
219:         return FusionDecision(
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
```

### Context 105

```text
220:             intent_id=intent_id,
221:             intent_final=out,
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
```

### Context 106

```text
222:             reason_code=rc,
223:             intent_1m_raw="SELL",
224:             vote_5m_direction=d,
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

### Context 107

```text
225:             vote_5m_strength=s,
226:             vote_5m_seed_id=vote_5m_seed_id,
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

### Context 108

```text
227:             allow_long=allow_long_i,
228:             allow_short=allow_short_i,
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

### Context 109

```text
229:             thresh=t,
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

### Context 110

```text
230:             current_position=pos,
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

### Context 111

```text
231:         )
232: 
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

### Context 112

```text
233:     return FusionDecision(
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

### Context 113

```text
234:         intent_id=intent_id,
235:         intent_final="HOLD",
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

### Context 114

```text
236:         reason_code="UNKNOWN_INTENT_FAILSAFE",
237:         intent_1m_raw="HOLD",
238:         vote_5m_direction=d,
239:         vote_5m_strength=s,
240:         vote_5m_seed_id=vote_5m_seed_id,
241:         allow_long=allow_long_i,
242:         allow_short=allow_short_i,
243:         thresh=t,
244:         current_position=pos,
245:     )
246: 
```

## Target: live_l1/core/intent.py

exists: True

### Context 1

```text
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
```

### Context 2

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
```

### Context 3

```text
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
```

### Context 4

```text
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
```

### Context 5

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
```

### Context 6

```text
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

### Context 7

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
```

### Context 8

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
```

### Context 9

```text
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

### Context 10

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
```

### Context 11

```text
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

### Context 12

```text
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
```

### Context 13

```text
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

### Context 14

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
```

### Context 15

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
```

### Context 16

```text
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

### Context 17

```text
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

### Context 18

```text
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

### Context 19

```text
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

### Context 20

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
```

### Context 21

```text
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

### Context 22

```text
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
```

### Context 23

```text
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

### Context 24

```text
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

### Context 25

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
```

### Context 26

```text
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
```

### Context 27

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
```

### Context 28

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
```

### Context 29

```text
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

### Context 30

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
```

### Context 31

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
```

### Context 32

```text
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

### Context 33

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
```

### Context 34

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
```

### Context 35

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
```

### Context 36

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
```

### Context 37

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
```

### Context 38

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
```

### Context 39

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
```

### Context 40

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
```

### Context 41

```text
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

### Context 42

```text
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
```

### Context 43

```text
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
```

### Context 44

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
```

### Context 45

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
```

### Context 46

```text
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

### Context 47

```text
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

### Context 48

```text
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

## Target: live_l1/core/loop.py

exists: True

### Context 1

```text
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
```

### Context 2

```text
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
```

### Context 3

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
```

### Context 4

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
```

### Context 5

```text
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

### Context 6

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
```

### Context 7

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
```

### Context 8

```text
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

### Context 9

```text
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
```

### Context 10

```text
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
```

### Context 11

```text
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
```

### Context 12

```text
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
```

### Context 13

```text
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
```

### Context 14

```text
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
```

### Context 15

```text
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
```

### Context 16

```text
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
```

### Context 17

```text
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
```

### Context 18

```text
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
```

### Context 19

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
```

### Context 20

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
```

### Context 21

```text
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

### Context 22

```text
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
```

### Context 23

```text
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
```

### Context 24

```text
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
```

### Context 25

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
```

### Context 26

```text
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

### Context 27

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
```

### Context 28

```text
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

### Context 29

```text
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
```

### Context 30

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
```

### Context 31

```text
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
```

### Context 32

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
```

### Context 33

```text
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

### Context 34

```text
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
```

### Context 35

```text
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
```

### Context 36

```text
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
```

### Context 37

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
```

### Context 38

```text
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
```

### Context 39

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
```

### Context 40

```text
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
```

### Context 41

```text
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
```

### Context 42

```text
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
```

### Context 43

```text
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
```

### Context 44

```text
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
```

### Context 45

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
```

### Context 46

```text
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
```

### Context 47

```text
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
```

### Context 48

```text
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
```

### Context 49

```text
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
```

### Context 50

```text
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
```

### Context 51

```text
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
```

### Context 52

```text
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
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:                 rsi_signal=features.signal("rsi_signal"),
```

### Context 53

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
```

### Context 54

```text
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
```

### Context 55

```text
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
893:                 adx_signal=features.signal("adx_signal"),
894:                 cci_signal=features.signal("cci_signal"),
```

### Context 56

```text
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
```

### Context 57

```text
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
```

### Context 58

```text
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

### Context 59

```text
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
920:                 },
921:             )
922: 
```

### Context 60

```text
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
920:                 },
921:             )
922: 
923:             log.log(
```

### Context 61

```text
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
920:                 },
921:             )
922: 
923:             log.log(
924:                 category="L2",
```

### Context 62

```text
926:                 severity="INFO",
927:                 system_state_id=state.system_state_id,
928:                 fields={
929:                     "tick": tick.tick_id,
930:                     "snapshot_id": features.snapshot_id,
931:                     "timestamp_utc": features.timestamp_utc,
932:                     "symbol": features.symbol,
933:                     "price": float(features.price),
934:                     "allow_long": int(features.allow_long),
935:                     "allow_short": int(features.allow_short),
936:                     "regime_v2": int(features.regime_v2),
937:                 },
938:             )
939: 
940:             log.log(
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
```

### Context 63

```text
927:                 system_state_id=state.system_state_id,
928:                 fields={
929:                     "tick": tick.tick_id,
930:                     "snapshot_id": features.snapshot_id,
931:                     "timestamp_utc": features.timestamp_utc,
932:                     "symbol": features.symbol,
933:                     "price": float(features.price),
934:                     "allow_long": int(features.allow_long),
935:                     "allow_short": int(features.allow_short),
936:                     "regime_v2": int(features.regime_v2),
937:                 },
938:             )
939: 
940:             log.log(
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
```

### Context 64

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
```

### Context 65

```text
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
```

### Context 66

```text
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
```

### Context 67

```text
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
987:                 regime=regime,
```

### Context 68

```text
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
987:                 regime=regime,
988:             )
989: 
990:             _append_passive_shadow_risk_snapshot(
```

### Context 69

```text
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
987:                 regime=regime,
988:             )
989: 
990:             _append_passive_shadow_risk_snapshot(
991:                 repo_root=repo_root,
992:                 tick_id=tick.tick_id,
```

### Context 70

```text
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

- If intent_1m_raw is HOLD, fusion likely preserves HOLD regardless of timing vote.
- If gates allow neither direction, BUY/SELL should be blocked even when timing agrees.
- The audit should identify whether timing can create entries or only confirm raw 1m intents.

## Required Next Step

Review fusion rules and decide whether timing remains confirmatory only or can become a candidate signal layer.

## Result

Status: PASS
