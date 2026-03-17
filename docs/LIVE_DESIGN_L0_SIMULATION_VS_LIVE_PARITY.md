# LIVE DESIGN — L0 SIMULATION VS LIVE PARITY
Projekt: Sniper-Bot  
Datum: 2026-01-10  
Status: VERBINDLICH (L0)

---

## Zweck dieses Dokuments

Dieses Dokument definiert verbindlich:
- welche Eigenschaften zwischen GS-Simulation und Live-System identisch sein MÜSSEN
- welche Eigenschaften bewusst unterschiedlich sind
- welche Vermischungen strikt verboten sind

Ziel ist der Schutz der GS-Integrität bei gleichzeitiger Live-Tauglichkeit.

---

## Grundsatz

Simulation beantwortet: „Was würde passieren?“  
Live beantwortet: „Was darf passieren?“

Parity bedeutet Vergleichbarkeit, nicht Gleichheit.

---

## MUSS identisch sein (HARTE PARITY)

Die folgenden Eigenschaften müssen zwischen GS und Live logisch identisch bleiben.

### Entscheidungsbasis
- diskrete *_signal-Werte (-1 / 0 / +1)
- gewichtete Linearkombination (Score)
- gleiche Entry- und Exit-Schwellenlogik (enter_z / exit_z)
- gleiche Richtungssemantik (LONG / SHORT)

### Semantik
- +1 = bullish
- -1 = bearish
- 0 = neutral

### Zeitliche Interpretation
- Entscheidung basiert auf abgeschlossener Kerze
- keine Intrabar-Interpretation

---

## DARF unterschiedlich sein (EXPLIZIT ERLAUBT)

Die folgenden Aspekte sind bewusst NICHT identisch.

### Execution
- Order-Fills (partial / delayed)
- Slippage real
- Fees real
- Order-Rejects
- Rate-Limits

### Zeit
- Latenz
- Clock Drift
- Netzwerkverzögerungen

### Kapital
- Positionsgröße
- Exposure-Limits
- Kapital-Allokation
- Margin-Regeln

Diese Unterschiede werden durch Guards abgefedert, nicht durch Logik.

---

## DARF NICHT existieren (VERBOTENE PARITY)

Die folgenden Konzepte dürfen live NICHT aus GS abgeleitet werden.

- GS-ROI im Live-State
- GS-Sharpe
- erwartete Rendite
- Erfolgswahrscheinlichkeit
- Score-Magnitude-Optimierung
- GS-Backtest-Aufruf im Live-Loop

Live darf GS niemals evaluieren oder rekonstruieren.

---

## Verbotene Annahmen

- dass Live besser sein muss als GS
- dass GS Live-Fehler „ausgleicht“
- dass mehr Information bessere Entscheidungen bedeutet
- dass Simulation Realität approximiert

GS ist Referenz, nicht Wahrheit.

---

## Parity-Grenze (verbindlich)

#GS endet bei: Decision Semantik
#Live beginnt bei: Execution Realität


Diese Grenze darf nicht überschritten werden.

---

## Zentrale Invariante

Live-Verhalten darf erklärbar bleiben,
ohne Zugriff auf GS-Ergebnisse.

Wenn eine Live-Entscheidung nur mit GS-ROI erklärbar ist,
ist das Design ungültig.

---

## Abschluss

Mit L0-D ist definiert:
- was vergleichbar bleiben muss
- was bewusst abweicht
- wo jede Vermischung endet

Damit ist die Grundlage für Paper-Trading (L1) geschaffen,
ohne die GS-Integrität zu gefährden.
