# P42 TIMING SEED SELECTION LOGIC AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Audit the 5m timing seed scoring and selection logic after P41 showed that short seeds do not win in isolated tests.

## Target File

live_l1/core/timing_5m.py

## Relevant Source Context

### Context 1

```text
115:             )
116: 
117:     return rows
118: 
119: 
120: def _seed_score(seed: SeedRow) -> float:
121:     base = 0.0
122: 
123:     for _, w in seed.comb.items():
124:         base += _safe_float(w, 0.0)
125: 
126:     if seed.direction == "short":
127:         return -abs(base)
128: 
129:     if seed.direction == "none":
130:         return 0.0
131: 
132:     return abs(base)
```

### Context 2

```text
121:     base = 0.0
122: 
123:     for _, w in seed.comb.items():
124:         base += _safe_float(w, 0.0)
125: 
126:     if seed.direction == "short":
127:         return -abs(base)
128: 
129:     if seed.direction == "none":
130:         return 0.0
131: 
132:     return abs(base)
133: 
134: 
135: def _strength_from_score(score: float) -> float:
136:     a = abs(_safe_float(score, 0.0))
137: 
138:     if a <= 0.0:
```

### Context 3

```text
122: 
123:     for _, w in seed.comb.items():
124:         base += _safe_float(w, 0.0)
125: 
126:     if seed.direction == "short":
127:         return -abs(base)
128: 
129:     if seed.direction == "none":
130:         return 0.0
131: 
132:     return abs(base)
133: 
134: 
135: def _strength_from_score(score: float) -> float:
136:     a = abs(_safe_float(score, 0.0))
137: 
138:     if a <= 0.0:
139:         return 0.0
```

### Context 4

```text
124:         base += _safe_float(w, 0.0)
125: 
126:     if seed.direction == "short":
127:         return -abs(base)
128: 
129:     if seed.direction == "none":
130:         return 0.0
131: 
132:     return abs(base)
133: 
134: 
135: def _strength_from_score(score: float) -> float:
136:     a = abs(_safe_float(score, 0.0))
137: 
138:     if a <= 0.0:
139:         return 0.0
140: 
141:     if a >= 1.0:
```

### Context 5

```text
127:         return -abs(base)
128: 
129:     if seed.direction == "none":
130:         return 0.0
131: 
132:     return abs(base)
133: 
134: 
135: def _strength_from_score(score: float) -> float:
136:     a = abs(_safe_float(score, 0.0))
137: 
138:     if a <= 0.0:
139:         return 0.0
140: 
141:     if a >= 1.0:
142:         return 1.0
143: 
144:     return a
```

### Context 6

```text
130:         return 0.0
131: 
132:     return abs(base)
133: 
134: 
135: def _strength_from_score(score: float) -> float:
136:     a = abs(_safe_float(score, 0.0))
137: 
138:     if a <= 0.0:
139:         return 0.0
140: 
141:     if a >= 1.0:
142:         return 1.0
143: 
144:     return a
145: 
146: 
147: def _pick_best_seed(seeds: List[SeedRow]) -> Tuple[Optional[SeedRow], float]:
```

### Context 7

```text
131: 
132:     return abs(base)
133: 
134: 
135: def _strength_from_score(score: float) -> float:
136:     a = abs(_safe_float(score, 0.0))
137: 
138:     if a <= 0.0:
139:         return 0.0
140: 
141:     if a >= 1.0:
142:         return 1.0
143: 
144:     return a
145: 
146: 
147: def _pick_best_seed(seeds: List[SeedRow]) -> Tuple[Optional[SeedRow], float]:
148:     best: Optional[SeedRow] = None
```

### Context 8

```text
142:         return 1.0
143: 
144:     return a
145: 
146: 
147: def _pick_best_seed(seeds: List[SeedRow]) -> Tuple[Optional[SeedRow], float]:
148:     best: Optional[SeedRow] = None
149:     best_score = 0.0
150: 
151:     for s in seeds:
152:         sc = _seed_score(s)
153: 
154:         if best is None:
155:             best = s
156:             best_score = sc
157:             continue
158: 
159:         if abs(sc) > abs(best_score):
```

### Context 9

```text
144:     return a
145: 
146: 
147: def _pick_best_seed(seeds: List[SeedRow]) -> Tuple[Optional[SeedRow], float]:
148:     best: Optional[SeedRow] = None
149:     best_score = 0.0
150: 
151:     for s in seeds:
152:         sc = _seed_score(s)
153: 
154:         if best is None:
155:             best = s
156:             best_score = sc
157:             continue
158: 
159:         if abs(sc) > abs(best_score):
160:             best = s
161:             best_score = sc
```

### Context 10

```text
147: def _pick_best_seed(seeds: List[SeedRow]) -> Tuple[Optional[SeedRow], float]:
148:     best: Optional[SeedRow] = None
149:     best_score = 0.0
150: 
151:     for s in seeds:
152:         sc = _seed_score(s)
153: 
154:         if best is None:
155:             best = s
156:             best_score = sc
157:             continue
158: 
159:         if abs(sc) > abs(best_score):
160:             best = s
161:             best_score = sc
162:             continue
163: 
164:         if abs(sc) == abs(best_score):
```

### Context 11

```text
151:     for s in seeds:
152:         sc = _seed_score(s)
153: 
154:         if best is None:
155:             best = s
156:             best_score = sc
157:             continue
158: 
159:         if abs(sc) > abs(best_score):
160:             best = s
161:             best_score = sc
162:             continue
163: 
164:         if abs(sc) == abs(best_score):
165:             if s.seed_id < best.seed_id:
166:                 best = s
167:                 best_score = sc
168: 
```

### Context 12

```text
154:         if best is None:
155:             best = s
156:             best_score = sc
157:             continue
158: 
159:         if abs(sc) > abs(best_score):
160:             best = s
161:             best_score = sc
162:             continue
163: 
164:         if abs(sc) == abs(best_score):
165:             if s.seed_id < best.seed_id:
166:                 best = s
167:                 best_score = sc
168: 
169:     return best, best_score
170: 
171: 
```

### Context 13

```text
156:             best_score = sc
157:             continue
158: 
159:         if abs(sc) > abs(best_score):
160:             best = s
161:             best_score = sc
162:             continue
163: 
164:         if abs(sc) == abs(best_score):
165:             if s.seed_id < best.seed_id:
166:                 best = s
167:                 best_score = sc
168: 
169:     return best, best_score
170: 
171: 
172: def compute_5m_timing_vote(
173:     *,
```

### Context 14

```text
159:         if abs(sc) > abs(best_score):
160:             best = s
161:             best_score = sc
162:             continue
163: 
164:         if abs(sc) == abs(best_score):
165:             if s.seed_id < best.seed_id:
166:                 best = s
167:                 best_score = sc
168: 
169:     return best, best_score
170: 
171: 
172: def compute_5m_timing_vote(
173:     *,
174:     seeds_csv: str,
175:     repo_root: str = ".",
176:     symbol: str = "BTCUSDT",
```

### Context 15

```text
162:             continue
163: 
164:         if abs(sc) == abs(best_score):
165:             if s.seed_id < best.seed_id:
166:                 best = s
167:                 best_score = sc
168: 
169:     return best, best_score
170: 
171: 
172: def compute_5m_timing_vote(
173:     *,
174:     seeds_csv: str,
175:     repo_root: str = ".",
176:     symbol: str = "BTCUSDT",
177:     now_utc: Optional[str] = None,
178:     timeframe: Optional[str] = None,
179:     thresh: Optional[float] = None,
```

### Context 16

```text
164:         if abs(sc) == abs(best_score):
165:             if s.seed_id < best.seed_id:
166:                 best = s
167:                 best_score = sc
168: 
169:     return best, best_score
170: 
171: 
172: def compute_5m_timing_vote(
173:     *,
174:     seeds_csv: str,
175:     repo_root: str = ".",
176:     symbol: str = "BTCUSDT",
177:     now_utc: Optional[str] = None,
178:     timeframe: Optional[str] = None,
179:     thresh: Optional[float] = None,
180:     **kwargs: Any,
181: ) -> TimingVote:
```

### Context 17

```text
167:                 best_score = sc
168: 
169:     return best, best_score
170: 
171: 
172: def compute_5m_timing_vote(
173:     *,
174:     seeds_csv: str,
175:     repo_root: str = ".",
176:     symbol: str = "BTCUSDT",
177:     now_utc: Optional[str] = None,
178:     timeframe: Optional[str] = None,
179:     thresh: Optional[float] = None,
180:     **kwargs: Any,
181: ) -> TimingVote:
182:     """
183:     API expected by live_l1/core/loop.py
184:     """
```

### Context 18

```text
191:     _ = kwargs
192: 
193:     seeds = _read_seeds_csv(seeds_csv)
194: 
195:     if not seeds:
196:         return TimingVote(direction="none", strength=0.0, seed_id=None)
197: 
198:     best, score = _pick_best_seed(seeds)
199: 
200:     if best is None:
201:         return TimingVote(direction="none", strength=0.0, seed_id=None)
202: 
203:     direction = best.direction
204:     strength = _strength_from_score(score)
205: 
206:     if direction not in ("long", "short") or strength <= 0.0:
207:         return TimingVote(direction="none", strength=0.0, seed_id=None)
208: 
```

### Context 19

```text
193:     seeds = _read_seeds_csv(seeds_csv)
194: 
195:     if not seeds:
196:         return TimingVote(direction="none", strength=0.0, seed_id=None)
197: 
198:     best, score = _pick_best_seed(seeds)
199: 
200:     if best is None:
201:         return TimingVote(direction="none", strength=0.0, seed_id=None)
202: 
203:     direction = best.direction
204:     strength = _strength_from_score(score)
205: 
206:     if direction not in ("long", "short") or strength <= 0.0:
207:         return TimingVote(direction="none", strength=0.0, seed_id=None)
208: 
209:     return TimingVote(
210:         direction=direction,
```

### Context 20

```text
196:         return TimingVote(direction="none", strength=0.0, seed_id=None)
197: 
198:     best, score = _pick_best_seed(seeds)
199: 
200:     if best is None:
201:         return TimingVote(direction="none", strength=0.0, seed_id=None)
202: 
203:     direction = best.direction
204:     strength = _strength_from_score(score)
205: 
206:     if direction not in ("long", "short") or strength <= 0.0:
207:         return TimingVote(direction="none", strength=0.0, seed_id=None)
208: 
209:     return TimingVote(
210:         direction=direction,
211:         strength=strength,
212:         seed_id=best.seed_id,
213:     )
```

### Context 21

```text
199: 
200:     if best is None:
201:         return TimingVote(direction="none", strength=0.0, seed_id=None)
202: 
203:     direction = best.direction
204:     strength = _strength_from_score(score)
205: 
206:     if direction not in ("long", "short") or strength <= 0.0:
207:         return TimingVote(direction="none", strength=0.0, seed_id=None)
208: 
209:     return TimingVote(
210:         direction=direction,
211:         strength=strength,
212:         seed_id=best.seed_id,
213:     )
214: 
215: 
216: def _cli_main() -> int:
```

### Context 22

```text
201:         return TimingVote(direction="none", strength=0.0, seed_id=None)
202: 
203:     direction = best.direction
204:     strength = _strength_from_score(score)
205: 
206:     if direction not in ("long", "short") or strength <= 0.0:
207:         return TimingVote(direction="none", strength=0.0, seed_id=None)
208: 
209:     return TimingVote(
210:         direction=direction,
211:         strength=strength,
212:         seed_id=best.seed_id,
213:     )
214: 
215: 
216: def _cli_main() -> int:
217:     parser = argparse.ArgumentParser()
218:     parser.add_argument("--repo-root", default=".")
```

### Context 23

```text
202: 
203:     direction = best.direction
204:     strength = _strength_from_score(score)
205: 
206:     if direction not in ("long", "short") or strength <= 0.0:
207:         return TimingVote(direction="none", strength=0.0, seed_id=None)
208: 
209:     return TimingVote(
210:         direction=direction,
211:         strength=strength,
212:         seed_id=best.seed_id,
213:     )
214: 
215: 
216: def _cli_main() -> int:
217:     parser = argparse.ArgumentParser()
218:     parser.add_argument("--repo-root", default=".")
219:     parser.add_argument("--symbol", default="BTCUSDT")
```

### Context 24

```text
206:     if direction not in ("long", "short") or strength <= 0.0:
207:         return TimingVote(direction="none", strength=0.0, seed_id=None)
208: 
209:     return TimingVote(
210:         direction=direction,
211:         strength=strength,
212:         seed_id=best.seed_id,
213:     )
214: 
215: 
216: def _cli_main() -> int:
217:     parser = argparse.ArgumentParser()
218:     parser.add_argument("--repo-root", default=".")
219:     parser.add_argument("--symbol", default="BTCUSDT")
220:     parser.add_argument("--seeds", required=True)
221: 
222:     args = parser.parse_args()
223: 
```

### Context 25

```text
227:         seeds_csv=args.seeds,
228:         now_utc=None,
229:     )
230: 
231:     seeds = _read_seeds_csv(args.seeds)
232:     best, best_score = _pick_best_seed(seeds)
233: 
234:     sid = vote.seed_id if vote.seed_id is not None else ""
235:     best_dir = best.direction if best is not None else ""
236: 
237:     print(
238:         "vote_5m direction={d} strength={s:.6f} seed_id={sid} best_seed_dir={bd} score={sc:.6f}".format(
239:             d=vote.direction,
240:             s=vote.strength,
241:             sid=sid,
242:             bd=best_dir,
243:             sc=_safe_float(best_score, 0.0),
244:         )
```

### Context 26

```text
233: 
234:     sid = vote.seed_id if vote.seed_id is not None else ""
235:     best_dir = best.direction if best is not None else ""
236: 
237:     print(
238:         "vote_5m direction={d} strength={s:.6f} seed_id={sid} best_seed_dir={bd} score={sc:.6f}".format(
239:             d=vote.direction,
240:             s=vote.strength,
241:             sid=sid,
242:             bd=best_dir,
243:             sc=_safe_float(best_score, 0.0),
244:         )
245:     )
246: 
247:     return 0
248: 
249: 
250: if __name__ == "__main__":
```

### Context 27

```text
235:     best_dir = best.direction if best is not None else ""
236: 
237:     print(
238:         "vote_5m direction={d} strength={s:.6f} seed_id={sid} best_seed_dir={bd} score={sc:.6f}".format(
239:             d=vote.direction,
240:             s=vote.strength,
241:             sid=sid,
242:             bd=best_dir,
243:             sc=_safe_float(best_score, 0.0),
244:         )
245:     )
246: 
247:     return 0
248: 
249: 
250: if __name__ == "__main__":
251:     raise SystemExit(_cli_main())
252: 
```

### Context 28

```text
238:         "vote_5m direction={d} strength={s:.6f} seed_id={sid} best_seed_dir={bd} score={sc:.6f}".format(
239:             d=vote.direction,
240:             s=vote.strength,
241:             sid=sid,
242:             bd=best_dir,
243:             sc=_safe_float(best_score, 0.0),
244:         )
245:     )
246: 
247:     return 0
248: 
249: 
250: if __name__ == "__main__":
251:     raise SystemExit(_cli_main())
252: 
253: 
254: 
255: 
```

## Preliminary Findings

- P41 showed that negative input signals still selected the long seed.
- This indicates that seed selection is not currently direction-aware with respect to signal polarity.
- The audit must confirm whether _seed_score() uses only seed weights and direction, but not current signal values.
- If true, short seeds cannot win based on negative market signals alone.

## Required Next Step

Review this audit output and design a polarity-aware seed scoring model before patching.

## Result

Status: PASS
