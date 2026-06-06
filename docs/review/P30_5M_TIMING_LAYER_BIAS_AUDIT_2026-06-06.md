# P30 5M TIMING LAYER BIAS AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Determine why the 5m timing layer emits only long votes in Live L1 logs.

## Runtime Vote Distribution

- long: 4300720

## Seed File

path: seeds/5m/btcusdt_5m_long_timing_core_v1.csv

exists: True

rows: 2

columns:

- seed_id
- comb_json

## Seed Direction Columns

No explicit direction/side column found.

## Top Seed IDs

- C01_rsi_stoch_06: 1
- C02_rsi_stoch_08: 1

## timing_5m.py Keyword Hits

```text
15: from live_l1.core.intent_fusion import TimingVote
20:     seed_id: str
22:     direction: str  # long | short | none
27:         return float(x)
29:         return default
32: def _normalize_direction(d: Optional[str]) -> str:
34:         return "long"
36:     if dd in ("long", "short", "none"):
37:         return dd
39:         return "long"
41:         return "short"
42:     return "long"
49:         return {}
52:         return {}
55:         return obj if isinstance(obj, dict) else {}
57:         return {}
61:     for k in ("dir", "direction"):
63:             return str(raw.get(k)).strip()
64:     return None
73:         if kk in ("dir", "direction"):
76:     return out
79: def _read_seeds_csv(path: str) -> List[SeedRow]:
81:         raise FileNotFoundError("seeds csv not found: {0}".format(path))
89:             return []
92:             seed_id = str(line.get("seed_id", "")).strip()
93:             if not seed_id:
98:             dir_from_col = line.get("direction", None)
99:             direction = _normalize_direction(dir_from_col)
105:                 direction = _normalize_direction(dir_from_comb)
111:                     seed_id=seed_id,
113:                     direction=direction,
117:     return rows
120: def _seed_score(seed: SeedRow) -> float:
123:     for _, w in seed.comb.items():
126:     if seed.direction == "short":
127:         return -abs(base)
129:     if seed.direction == "none":
130:         return 0.0
132:     return abs(base)
139:         return 0.0
142:         return 1.0
144:     return a
147: def _pick_best_seed(seeds: List[SeedRow]) -> Tuple[Optional[SeedRow], float]:
151:     for s in seeds:
152:         sc = _seed_score(s)
165:             if s.seed_id < best.seed_id:
169:     return best, best_score
172: def compute_5m_timing_vote(
174:     seeds_csv: str,
181: ) -> TimingVote:
193:     seeds = _read_seeds_csv(seeds_csv)
195:     if not seeds:
196:         return TimingVote(direction="none", strength=0.0, seed_id=None)
198:     best, score = _pick_best_seed(seeds)
201:         return TimingVote(direction="none", strength=0.0, seed_id=None)
203:     direction = best.direction
206:     if direction not in ("long", "short") or strength <= 0.0:
207:         return TimingVote(direction="none", strength=0.0, seed_id=None)
209:     return TimingVote(
210:         direction=direction,
212:         seed_id=best.seed_id,
220:     parser.add_argument("--seeds", required=True)
224:     vote = compute_5m_timing_vote(
227:         seeds_csv=args.seeds,
231:     seeds = _read_seeds_csv(args.seeds)
232:     best, best_score = _pick_best_seed(seeds)
234:     sid = vote.seed_id if vote.seed_id is not None else ""
235:     best_dir = best.direction if best is not None else ""
238:         "vote_5m direction={d} strength={s:.6f} seed_id={sid} best_seed_dir={bd} score={sc:.6f}".format(
239:             d=vote.direction,
240:             s=vote.strength,
247:     return 0
```

## loop.py Timing Integration Hits

```text
26: from live_l1.core.timing_5m import compute_5m_timing_vote
27: from live_l1.core.intent_fusion import fuse_intent_with_5m_timing
51:     seeds_5m_csv: str
53:     timing_v2_shadow: bool
54:     timing_v2_history_len: int
205:         seeds_5m_csv=os.environ.get(
207:             "seeds/5m/btcusdt_5m_long_timing_core_v1.csv",
210:         timing_v2_shadow=_env_bool("L1_TIMING_V2_SHADOW", False),
211:         timing_v2_history_len=_env_int("L1_TIMING_V2_HISTORY_LEN", 3),
748:         seeds_5m_csv=str(cfg.seeds_5m_csv),
826:                 "seeds_5m_csv": cfg.seeds_5m_csv,
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
888:             fused = fuse_intent_with_5m_timing(
890:                 vote_5m_direction=vote_v1.direction,
891:                 vote_5m_strength=vote_v1.strength,
892:                 vote_5m_seed_id=vote_v1.seed_id,
962:                     "vote_5m_direction": vote_v1.direction,
963:                     "vote_5m_seed_id": str(vote_v1.seed_id),
964:                     "vote_5m_strength": float(vote_v1.strength),
```

## Preliminary Assessment

- Runtime confirms a permanent long-only 5m vote stream.
- Seed filename indicates a long-specific timing seed file.
- Seed file does not expose an obvious direction column in standard names.

## Result

Status: PASS
