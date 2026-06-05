# LIVE L1 DATA AUDIT
Date: 2026-06-05

## Ziel

Audit der Datenpipeline des produktiven Live-L1 Systems.

Untersucht:

- CSV Input
- Market Feed
- FeatureSnapshot
- Signalnutzung
- Ungenutzte Daten
- Datenfluss bis zur Entscheidungslogik

---

## Datenfluss

Aktueller Pfad:

CSV

↓

CSVMarketFeed

↓

MarketSnapshot

↓

FeatureSnapshot

↓

Intent

↓

Intent Fusion

↓

Execution

---

## CSVMarketFeed

Datei:

live_l1/io/market.py

CSVMarketFeed liest pro Tick exakt eine Zeile.

Preisbasis:

price = close

Damit erfolgen alle Entscheidungen auf Basis des Close-Preises.

---

## Geladene Signale

Der Feed lädt exakt folgende 12 Signale:

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

Dies entspricht dem bekannten 12er-Signalset des Projekts.

---

## Weitere geladene Daten

Zusätzlich werden geladen:

- timestamp_utc
- open
- high
- low
- close
- volume

sowie:

- allow_long
- allow_short
- regime_v2

---

## Aktiv genutzte Signale

Aktuell direkt relevant für die Entscheidungslogik:

Score-Komponenten:

- rsi_signal
- bollinger_signal
- stoch_signal
- cci_signal

Entry-Gates:

- ma200_signal
- mfi_signal
- atr_signal

Somit werden aktuell 7 Signale aktiv genutzt.

---

## Passiv transportierte Signale

Im aktuellen Produktionspfad vorhanden, aber nicht direkt für Entry oder Exit verwendet:

- macd_signal
- ema50_signal
- adx_signal
- obv_signal
- roc_signal

Diese Signale werden geladen und transportiert, beeinflussen die aktuelle Strategie jedoch nicht.

---

## OHLCV Nutzung

Vorhanden:

- open
- high
- low
- close
- volume

Tatsächlich genutzt:

- close

Aktuell werden open/high/low/volume nicht für Entscheidungen verwendet.

---

## Regime Nutzung

Transportiert:

- regime_v2

Aktueller Produktionsstatus:

- keine aktive Nutzung für Entry
- keine aktive Nutzung für Exit
- keine aktive Nutzung für Position Sizing

Verwendung:

- Monitoring
- Logging
- Diagnostik

---

## Allow Gates

Transportiert:

- allow_long
- allow_short

Aktuelle Beobachtung:

Diese Werte werden in die Fusion-Logik übernommen und protokolliert.

Die aktuelle asymmetrische Fusion verwendet sie jedoch nicht mehr als harte Blockierungsmechanismen.

---

## Architekturbewertung

Die Datenpipeline ist sauber.

Keine Datenverluste zwischen:

CSV
→ MarketSnapshot
→ FeatureSnapshot

festgestellt.

---

## Wichtigste Erkenntnis

Das System transportiert deutlich mehr Information als aktuell genutzt wird.

Aktiv genutzt:

- 7 Signale

Passiv vorhanden:

- 5 Signale
- regime_v2
- open/high/low/volume

Dadurch existieren zukünftige Erweiterungsmöglichkeiten ohne Änderungen an der Datenpipeline.

---

## Potenzielle spätere Erweiterungen

Mögliche Kandidaten:

- MACD-basierte Zusatzfilter
- EMA50 Trendfilter
- ADX Qualitätsfilter
- OBV Volumenfilter
- ROC Momentumfilter

Diese Daten sind bereits vollständig verfügbar.

---

## Gesamtbewertung

LIVE_L1_DATA_AUDIT_2026-06-05

Status: BESTANDEN

Kritische Probleme:

- keine gefunden

Architektur:

- konsistent
- deterministisch
- vollständig nachvollziehbar

Wichtigste Erkenntnis:

Die aktuelle Live-L1 Strategie nutzt nur einen Teil der bereits verfügbaren Informationen.
Die Datenpipeline besitzt deutlich mehr Potenzial als aktuell ausgeschöpft wird.
