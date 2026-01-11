# LIVE_DESIGN_L2_DECISION_MATRIX.md

## Zweck

Diese Entscheidungsmatrix definiert die minimalen, klaren Regeln,
nach denen L2 eine bestehende GS-Strategie im Live-Kontext
entweder freigibt (ALLOW) oder blockiert (BLOCK).

L2 ist rein beratend und führt keine Trades aus.

---

## 1. Entscheidungsobjekt

L2 bewertet ausschließlich:
- GS-Strategien (FINAL, READ-ONLY)
  - LONG_FINAL_CANONICAL
  - SHORT_FINAL

Keine neuen Strategien, keine Variationen, keine Anpassungen.

---

## 2. Entscheidungsdimensionen

L2 prüft jede GS-Strategie entlang der folgenden Dimensionen:

### D1 – Regime-Konsistenz
- Passt das aktuelle Marktregime zur GS-Strategieannahme?

### D2 – Marktkontext-Konsistenz
- Keine extreme Abweichung von GS-Referenzbedingungen
  (z. B. Volatilitäts- oder Liquiditätsausreißer)

### D3 – Betriebsstabilität
- L1 zeigt keine Alarme
- Health-Check ist stabil

### D4 – Strategische Integrität
- GS-Strategie unverändert
- Referenzdaten vollständig und konsistent

---

## 3. Entscheidungsregeln (binär)

### ALLOW
Eine GS-Strategie wird freigegeben, wenn:

- D1 erfüllt
- D2 erfüllt
- D3 erfüllt
- D4 erfüllt

→ **Alle Dimensionen müssen erfüllt sein**

---

### BLOCK
Eine GS-Strategie wird blockiert, wenn:

- mindestens eine Dimension nicht erfüllt ist

BLOCK ist immer die sichere Default-Entscheidung.

---

## 4. Entscheidungsoutput

L2 erzeugt ausschließlich:

- Entscheidung: ALLOW oder BLOCK
- Begründung:
  - welche Dimension(en) nicht erfüllt sind
- Zeitstempel
- Referenz auf Strategie-ID

Keine Gewichtungen, keine Scores, keine Wahrscheinlichkeiten.

---

## 5. Prinzipien

- BLOCK > ALLOW bei Unsicherheit
- Keine Heuristik ohne Dokumentation
- Keine impliziten Annahmen
- Jede Entscheidung ist reproduzierbar

---

## 6. Abbruchregel

L2 wird sofort deaktiviert, wenn:
- Entscheidungen nicht reproduzierbar sind
- Inkonsistenzen zwischen GS und Live auftreten
- L1 einen Alarm meldet

---

## 7. Status

Dokumentstatus: ENTWURF  
Implementierung: nicht begonnen  
Aktivierung: erst nach bestandenem L1 Exit & Review

---
ENDE
