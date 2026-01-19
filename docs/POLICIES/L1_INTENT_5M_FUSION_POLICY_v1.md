# Policy: L1 Intent x 5m Timing Fusion (v1)

Datum: 2026-01-19
Scope: L1 Paper (Designregel, keine Implementierung)
Ziel: 5m Timing-Core wirkt als Confirmation-Filter fuer 1m Intents.

## Definitionen

- intent_1m_raw in {BUY, SELL, HOLD}
- allow_long, allow_short in {0, 1} (aus Gate/Regime-Labels, effective gate=auto)
- vote_5m_direction in {long, short, none}
- vote_5m_strength in [0, 1] (normiert)
- THRESH = 0.60 (fix fuer v1)

## Fusion-Regel (minimal, deterministisch)

1) Wenn intent_1m_raw == HOLD:
   -> intent_final = HOLD (reason=HOLD_RAW)

2) Wenn intent_1m_raw == BUY:
   - wenn allow_long != 1 -> HOLD (reason=GATE_BLOCK_LONG)
   - sonst wenn vote_5m_direction != long -> HOLD (reason=NO_5M_LONG_CONFIRM)
   - sonst wenn vote_5m_strength < THRESH -> HOLD (reason=WEAK_5M_LONG_CONFIRM)
   - sonst -> BUY (reason=CONFIRMED_1M_BUY_5M_LONG)

3) Wenn intent_1m_raw == SELL:
   - wenn allow_short != 1 -> HOLD (reason=GATE_BLOCK_SHORT)
   - sonst wenn vote_5m_direction != short -> HOLD (reason=NO_5M_SHORT_CONFIRM)
   - sonst wenn vote_5m_strength < THRESH -> HOLD (reason=WEAK_5M_SHORT_CONFIRM)
   - sonst -> SELL (reason=CONFIRMED_1M_SELL_5M_SHORT)

## Konfliktregel

- Wenn vote_5m_direction == none:
  -> niemals bestaetigen (immer HOLD bei BUY/SELL raw)

- Wenn (vote_5m_direction == long) und (intent_1m_raw == SELL):
  -> HOLD (reason=5M_CONTRADICTS_1M)

- Wenn (vote_5m_direction == short) und (intent_1m_raw == BUY):
  -> HOLD (reason=5M_CONTRADICTS_1M)

## Logging (verbindlich)

Jede Entscheidung loggt:
- intent_1m_raw
- vote_5m_direction, vote_5m_strength, vote_5m_seed_id
- allow_long, allow_short
- intent_final, reason_code

