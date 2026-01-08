# GS_SIMTRADER_SPEC (Gold-Standard) — Contract v1

Status: Draft v1 (stabilisieren -> v1-final)
Scope: engine/simtraderGS.py + GS Datengrundlage (2017–2024) + optional Forward-Layer (ab 2025)
Ziel: Ein reproduzierbarer, deterministischer, minimaler Evaluator fuer LONG/SHORT-Backtests, der als Referenz ("Goldstandard") fuer alle K-Runs dient.

---

## 1. Zweck und Nicht-Ziele

### 1.1 Zweck
simtraderGS implementiert eine eindeutige, stabile Evaluationslogik fuer Strategiekombinationen (comb) auf Basis diskreter Signalspalten (*_signal).
Er liefert robuste Kennzahlen pro Kombination und Richtung (long/short), geeignet fuer:
- Smoke/Intermediate/Full Runs (K3–K12)
- Regime-Gating (extern) ohne Eingriff in die Kernlogik
- Vergleichbarkeit ueber Zeit und Hardware

### 1.2 Nicht-Ziele (explizit ausgeschlossen)
simtraderGS enthaelt NICHT:
- Positionsgroessen-/Capital-Allocation-Logik
- Multi-Asset/Portfolio-Logik
- Slippage/Spread/Orderbook-Modelle (ausser einfache Fee-Roundtrip-Adjustments in Tests)
- Regime-Erkennung oder "sideways"-Trading (Regime ist externes Gate)
- ML/Feature-Engineering/Labeling-Logik

---

## 2. Datengrundlage

### 2.1 Erwartete Spalten im price_df
Pflicht:
- close (float)

Optional (aber fuer Strategien notwendig):
- *_signal Spalten, diskret in {-1, 0, +1}
  Beispiele: rsi_signal, macd_signal, ma200_signal, ...

Optional (extern erzeugt):
- regime_v1 (int in {-1,0,+1}) als Gate-Label (NICHT im simtraderGS ausgewertet)

### 2.2 Zeitskala / Timestamp
simtraderGS benoetigt fuer die Kernsimulation kein timestamp-Feld.
Die Datensaetze fuer GS/Forward werden jedoch standardisiert erzeugt, u.a.:
- timestamp_utc (String ISO mit +00:00)
Dies dient der Nachvollziehbarkeit und externer Auswertung, nicht der Kernlogik.

---

## 3. Strategie-Modell

### 3.1 comb (Kombination)
comb ist ein dict (oder ein String, der zu einem dict geparst werden kann), das Gewichte pro Signal enthaelt.

Beispiele:
- {"rsi": 1.0, "macd": 1.0, "ma200": 1.0}
- {"rsi_signal": 0.5, "macd_signal": 0.2}

Keys koennen sein:
- Kurzkeys: rsi, macd, ma200, ...
- Vollkeys: *_signal

### 3.2 Score
Fuer jede Zeile t:
score[t] = Summe_i ( weight_i * signal_i[t] )
signal_i[t] in {-1,0,+1} (bei Bedarf intern normalisiert)

### 3.3 Entry/Exit-Regeln (identisch strukturiert fuer long/short)
Parameter (global, aus _CFG):
- take_profit_pct (tp)
- stop_loss_pct (sl)
- max_hold_bars (max_hold)
- enter_z (enter threshold)
- exit_z (exit threshold)

Entry:
- Entry wenn score[t] > enter_z

Exit (in der Trade-Schleife, earliest-first):
- TP: return >= tp
- SL: return <= -sl
- SCORE: score[j] < exit_z
- MAXHOLD: wenn max_hold erreicht, Exit am letzten Bar

Return-Berechnung:
- LONG: r = (close[j] - entry_px) / entry_px
- SHORT: r = (entry_px - close[j]) / entry_px

Wichtig:
- Die Exit-Pruefung laeuft in zeitlicher Reihenfolge; erster Trigger entscheidet.

### 3.4 Richtung (direction)
direction ∈ {"long","short"} (verbindlich)

Hinweis:
- "sideways" ist kein direction-Wert.
- Sideways ist ein Regime-Zustand (regime_v1==0) und wird ausschliesslich extern als Gate verwendet:
  allow_long/allow_short. simtraderGS bleibt unveraendert.

---

## 4. Outputs (Contract v1)

evaluate_strategy(price_df, comb, direction) -> dict

Pflichtfelder:
- roi: float            (Summe der Trade-Returns)
- num_trades: int
- winrate: float        (wins / num_trades, 0 wenn 0 Trades)
- sharpe: float         (mean(rets)/std(rets) auf Trade-Returns, 0 bei <2 Trades)
- pnl_sum: float        (identisch zu roi)
- avg_trade: float      (pnl_sum/num_trades, 0 wenn 0 Trades)

Numerische Sanitisierung:
- Alle Outputs muessen endlich sein (keine NaN/Inf). Unendliche/NaN Werte werden zu 0.0.

---

## 5. Performance und Caching

### 5.1 DF/Signals Cache (pro Worker)
simtraderGS cached:
- close array
- signal arrays pro Spalte

Invalidation erfolgt nur, wenn sich das DataFrame-Objekt aendert.
Ziel: keine Rebuilds pro Strategie.

---

## 6. Fee/Costs

simtraderGS Kern-Output enthaelt keine Fee-Abzuege.
Fee-Adjustments sind Bestandteil von Diagnose/Smoke-Tools (z.B. roundtrip fee),
um Monotonie-Invarianten zu pruefen.

---

## 7. Regime Gate (extern, Contract)

Regime v1:
- basiert auf MA200-Slope (extern erzeugt)
- Label: regime_v1 ∈ {-1,0,+1}
  +1 = bull (allow_long)
  -1 = bear (allow_short)
   0 = side (beides verboten)

Gate-Regel (verbindlich, extern):
- LONG trades werden nur aus Zeilen zugelassen, wo regime_v1 == +1
- SHORT trades nur, wo regime_v1 == -1
- regime_v1 == 0 erzeugt keine Trades

Wichtig:
- Das Gate filtert Entry-Events, nicht die Exit-Mechanik.
- simtraderGS selbst bleibt inhaltlich unveraendert.

---

## 8. Known Limitations (akzeptiert in v1)

- Gaps im Zeitindex werden toleriert (GS Datensaetze enthalten dokumentierte Luecken).
- Kein intrabar modeling.
- Kein Slippage/Spread.
- Kein Portfolio.
- Kein dynamisches Sizing.

---

## 9. Akzeptanzkriterien fuer v1-final

v1-final ist erreicht, wenn:
- gs_smoke_suite.py: ALL PASS
- diagnostics: DIAG vs BASE match: True (fee=0)
- determinism: wiederholte Runs identisch
- numerics: keine NaN/Inf
- direction bleibt strikt {long, short}
- regime gate funktioniert extern als allow_long/allow_short ohne Eingriff in Kernlogik

Ende.
