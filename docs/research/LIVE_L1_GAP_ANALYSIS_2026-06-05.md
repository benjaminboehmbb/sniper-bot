# LIVE L1 GAP ANALYSIS
Date: 2026-06-05

## Basis

Diese Gap-Analyse fasst die Ergebnisse der Live-L1 Audits zusammen:

- Entry Audit
- Regime Audit
- Execution Audit
- Exit Audit
- Data Audit

Ergebnis:

Keine kritischen Produktionsfehler gefunden.

Live-L1 ist aktuell konsistent, deterministisch und entspricht weitgehend dem bekannten BEST_STATE-Hauptpfad.

---

## GAP 1 - Online Signal Builder

Aktueller Zustand:

Live-L1 liest vorberechnete Signale aus CSV:

- rsi_signal
- macd_signal
- bollinger_signal
- ma200_signal
- stoch_signal
- atr_signal
- ema50_signal
- adx_signal
- cci_signal
- mfi_signal
- obv_signal
- roc_signal

Bewertung:

Für deterministische Paper-Runs korrekt.

Für echten Live-Betrieb noch unvollständig.

Offen:

Online-Berechnung der Signale aus Live-OHLCV-Daten.

Priorität:

P1 für späteren Live-Betrieb.

---

## GAP 2 - Online Regime und Gate Builder

Aktueller Zustand:

Live-L1 liest aus CSV:

- regime_v2
- allow_long
- allow_short

Diese Felder werden aktuell nicht live-intern erzeugt.

Regime-Definition:

regime_v1:

- bull: close > ma200 und ma200_slope_1440 > 0
- bear: close < ma200 und ma200_slope_1440 < 0
- side: sonst

regime_v2:

- geglättetes regime_v1
- min_state_bars = 720
- optional kein direkter bull/bear flip

Gates:

allow_long:

- regime_v1 >= 0
- ADX >= 15

allow_short:

- regime_v1 == -1
- ADX >= 20

Bewertung:

Für Paper-Runs korrekt.

Für echten Live-Betrieb muss diese Logik online repliziert werden.

Priorität:

P1 für späteren Live-Betrieb.

---

## GAP 3 - Fee / Net-PnL Alignment

Aktueller Zustand:

GS Backtests:

- fee_roundtrip wird vom Return abgezogen

Live-L1 Paper Execution:

- fee_roundtrip wird geloggt
- pnl bleibt Brutto-PnL

Bewertung:

Kein Bug.

Aber Vergleichbarkeitslücke zwischen GS und Live-L1 Paper.

Empfohlene spätere Erweiterung:

- gross_pnl
- fee_cost
- net_pnl
- gross_pnl_pct
- net_pnl_pct

Bestehende pnl-Semantik nicht still ändern.

Priorität:

P2.

---

## GAP 4 - Execution Parameter zentral konfigurierbar machen

Aktuell hardcoded in execution.py:

- TP = 5.0 %
- SL = 1.5 %
- LONG_TIME_STOP_SEC = 3600
- SHORT_TIME_STOP_SEC = 3600

Bewertung:

Aktuell korrekt und dokumentiert.

Aber langfristig sollte dies zentral konfigurierbar werden.

Priorität:

P2.

---

## GAP 5 - Loss Cluster State Persistenz

Aktueller Zustand:

Loss-Cluster-Gate:

- 5 Verluste aus 10 Trades
- blockiert 35 Entry-Versuche

State:

- globales Prozessobjekt
- nicht persistiert
- geht bei Neustart verloren

Bewertung:

Für Paper-Runs akzeptabel.

Für robusten Live-Betrieb später nicht ausreichend.

Priorität:

P3.

---

## GAP 6 - Passive Signale und ungenutzte Daten

Aktuell aktiv genutzt:

- rsi_signal
- bollinger_signal
- stoch_signal
- cci_signal
- ma200_signal
- mfi_signal
- atr_signal

Aktuell passiv transportiert:

- macd_signal
- ema50_signal
- adx_signal
- obv_signal
- roc_signal
- open
- high
- low
- volume
- regime_v2

Bewertung:

Kein Fehler.

Aber potenzieller späterer Verbesserungshebel.

Priorität:

P3/P4.

---

## GAP 7 - TP Effektivität

Reale Exit-Verteilung aus 556 Trades:

- CLOSE_LONG: 322
- CLOSE_SHORT: 154
- SHORT_TIME_STOP: 63
- SL_LONG: 8
- SL_SHORT: 7
- LONG_TIME_STOP: 2
- TP_LONG: 0
- TP_SHORT: 0

Bewertung:

Strategie ist aktuell Score-Exit-getrieben.

TP ist derzeit faktisch nur ein Fallback.

Priorität:

P3 Forschungsthema.

---

## GAP 8 - Dokumentationskonsistenz

Korrigiert:

- execution.py Kommentar: Loss-Cluster blockiert 35 Entry-Versuche, nicht 25
- execution.py Kommentar: TP=5.0 %, SL=1.5 %

Offen:

Ältere Dokumente können weiterhin historische Zwischenstände enthalten.

Regel:

Code ist Source of Truth.

---

## Empfohlene Entwicklungsreihenfolge

1. Aktuellen Audit-Stand einfrieren.
2. Keine sofortigen Strategieänderungen.
3. Online Signal Builder designen.
4. Online Regime/Gate Builder designen.
5. Net-PnL-Erweiterung designen.
6. Erst danach produktive Codeänderungen mit Mini-Test und Validierungssequenz.

---

## Gesamtfazit

Live-L1 ist nach aktueller Bestandsaufnahme stabil, konsistent und produktionsnah.

Die offenen Punkte sind keine akuten Fehler.

Es handelt sich um Live-Readiness-, Konfigurations-, Vergleichbarkeits- und Erweiterungsgaps.
