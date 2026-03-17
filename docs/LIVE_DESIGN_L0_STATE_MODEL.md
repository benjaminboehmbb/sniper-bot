# LIVE DESIGN — L0 STATE MODEL
Projekt: Sniper-Bot  
Datum: 2026-01-10  
Status: VERBINDLICH (L0)

---

## Grundsatz

State speichert Fakten, keine Entscheidungen.
State enthält keine Optimierung.

---

## S1 — Market Snapshot (Read-Only)

- timestamp_utc
- price_close
- signals_hash
- data_valid

data_valid == false → keine neuen Intents

---

## S2 — Position State

- position_side: NONE | LONG | SHORT
- entry_price
- entry_time
- size

Beschreibt Ist-Zustand, keine Bewertung.

---

## S3 — Intent State (flüchtig)

- intent: BUY | SELL | HOLD | CLOSE
- intent_id
- intent_timestamp

Lebensdauer: 1 Tick

---

## S4 — Risk & Guard State

- trades_today
- loss_today
- cooldown_until
- anomaly_counter
- kill_level: NONE | SOFT | HARD | EMERGENCY

kill_level ist monoton.

---

## S5 — System Health

- heartbeat_ok
- clock_drift_ms
- resource_ok
- last_error_code

Health-Fehler stoppen den Flow.

---

## Persistenzregeln

Persistieren:
- S2 Position State
- S4 Risk State

Nicht persistieren:
- S1 Market
- S3 Intent
- S5 Health

---

## Verbotene States

- Confidence
- Edge
- Expected ROI
- Probability
- GS Scores

---

## Zentrale Invariante

Live-State enthält niemals mehr Information,
als ein menschlicher Operator sehen dürfte.
