# P57 EXACT RAW INTENT RULE EXTRACTION

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Extract the exact raw 1m intent decision block from live_l1/core/intent.py.

## Source

live_l1/core/intent.py

## Extracted Rule Block

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

## Result

Status: PASS
