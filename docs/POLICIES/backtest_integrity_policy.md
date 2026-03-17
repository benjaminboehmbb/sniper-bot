# Sniper-Bot – Backtest Integrity Policy

## Zweck dieses Dokuments

Diese Policy definiert die **verbindlichen Regeln** für alle Backtests im Sniper-Bot-Projekt.

Ziel ist es, systematisch zu verhindern, dass:
- Backtests unrealistisch gute Ergebnisse liefern,
- implizite Annahmen unbemerkt in die Simulation eingehen,
- Ergebnisse entstehen, die im Live-Betrieb nicht reproduzierbar sind.

Diese Policy gilt für:
- regelbasierte Strategien,
- ML-basierte Strategien,
- hybride Ansätze,
- alle GS- und Pre-Live-Phasen.

---

## Grundsatz

> **Ein Backtest ist nur dann akzeptabel, wenn er strukturell so gebaut ist,  
> dass er auch im Live-Betrieb scheitern könnte.**

Ein Backtest, der **nicht scheitern kann**, ist wertlos.

---

## 1. Zeitliche Integrität (Time Integrity)

### 1.1 Kein Look-Ahead Bias
- Entscheidungen dürfen ausschließlich auf Informationen basieren,  
  die **zum Entscheidungszeitpunkt verfügbar waren**.
- Jegliche Nutzung zukünftiger Preise, Kerzen, Indikatoren oder Labels ist verboten.

**Pflichtmaßnahmen**
- Klare Trennung zwischen:
  - Beobachtungsfenster
  - Entscheidungszeitpunkt
  - Ausführungszeitpunkt
- Explizite Zeitstempel-Logik (UTC, eindeutig definiert).

---

### 1.2 Entscheidungs- und Ausführungsreihenfolge
Die Reihenfolge ist verbindlich:

1. Marktbeobachtung (Daten bis *t*)
2. Signal-/Entscheidungslogik
3. Order-Erzeugung
4. Ausführung (frühestens *t+1* oder definierter Delay)

**Verboten**
- Ausführung in derselben Kerze, aus der das Signal berechnet wurde,
  sofern nicht explizit modelliert und begründet.

---

## 2. Datenintegrität (Data Integrity)

### 2.1 Point-in-Time-Daten
- Alle Daten müssen **point-in-time korrekt** sein.
- Keine nachträglichen Revisionen, Survivorship-bereinigten Universen
  oder „bereinigten“ historischen Datensätze ohne explizite Kennzeichnung.

---

### 2.2 Fehlende und fehlerhafte Daten
- Fehlende Daten dürfen **nicht stillschweigend interpoliert** werden.
- Jeder Fallback (z. B. Skip, Hold, Flat) muss explizit definiert sein.

**Pflicht**
- Dokumentierte Regeln für:
  - Missing Candles
  - Outliers
  - Null-Volumen-Perioden

---

## 3. Kosten- und Ausführungsrealismus

### 3.1 Transaktionskosten
- Jede Simulation **muss** Transaktionskosten enthalten.
- Mindestens:
  - Maker/Taker Fee oder pauschale Fee
  - Round-Trip-Betrachtung

Backtests ohne Kosten gelten als **diagnostisch**, nicht als Entscheidungsgrundlage.

---

### 3.2 Slippage & Spread
- Slippage darf nicht ignoriert werden.
- Entweder:
  - explizites Slippage-Modell
  - konservative pauschale Annahme

**Verboten**
- Implizite Annahme von Mid-Price-Fills ohne Begründung.

---

## 4. Kapital- und Risikoabbildung

### 4.1 Kapitalbindung
- Positionen binden Kapital.
- Gleichzeitige Positionen dürfen Kapital **nicht mehrfach verwenden**.

---

### 4.2 Positionsgröße & Leverage
- Positionsgrößen müssen:
  - explizit berechnet
  - deterministisch reproduzierbar
  - dokumentiert sein

Unbegrenztes oder implizites Leverage ist verboten.

---

### 4.3 Drawdown-Realismus
- Backtests müssen Drawdowns vollständig abbilden.
- Keine nachträgliche Glättung oder Filterung.

---

## 5. Statistik- und Bewertungsintegrität

### 5.1 Mindestanforderungen an Backtests
Ein Backtest ist **nicht bewertbar**, wenn:
- die Laufzeit zu kurz ist,
- die Anzahl unabhängiger Trades zu gering ist,
- die Ergebnisse von einzelnen Extremereignissen dominiert werden.

---

### 5.2 Overfitting-Prävention
- Ergebnisse müssen:
  - mindestens In-Sample / Out-of-Sample getrennt
  - besser: Walk-Forward geprüft sein

Ein einzelner „guter Lauf“ ist **kein Beweis**.

---

### 5.3 Kennzahlen
Mindestens zu betrachten:
- Netto-ROI (nach Kosten)
- Drawdown
- Trefferquote
- Trade-Anzahl
- Stabilität über Zeit

Kennzahlen ohne Kontext sind wertlos.

---

## 6. Vergleich & Reproduzierbarkeit

### 6.1 Reproduzierbarkeit
- Jeder Backtest muss:
  - deterministisch reproduzierbar sein
  - eindeutig versioniert werden (Code, Daten, Parameter)

---

### 6.2 Baseline-Vergleich
- Jede neue Strategie wird gegen:
  - einfache Baselines
  - bestehende GS-Referenzen

verglichen.

Besser als „nichts“ reicht nicht.

---

## 7. Verbotene Praktiken (Null-Toleranz)

Explizit verboten sind:
- Look-Ahead Bias in jeglicher Form
- In-Sample-Optimierung ohne OOS-Bestätigung
- Entfernen „schlechter Phasen“ aus dem Datensatz
- Ergebnis-Selektion („Cherry Picking“)
- Parameter-Tuning bis es „gut aussieht“

---

## 8. Durchsetzung

Diese Policy ist **verbindlich**.

Backtests, die gegen diese Regeln verstoßen:
- werden nicht weiterverfolgt,
- werden nicht verglichen,
- werden nicht in Entscheidungsprozesse einbezogen.

---

## Status

Gültig für:
- GS-Phase (Pre-Live)
- alle Strategie-Experimente
- alle Analyse-Pipelines

Letzte Aktualisierung: 2026-01
