# Sniper-Bot – ML Validation Policy

## Zweck dieses Dokuments

Diese Policy definiert die **verbindlichen Regeln** für den Einsatz von
Machine-Learning-Methoden im Sniper-Bot-Projekt.

Ziel ist es, sicherzustellen, dass:
- ML-Modelle **keine implizite Zukunftsinformation nutzen**,
- Ergebnisse **statistisch belastbar** sind,
- ML **nicht als Black Box** oder Ersatz für sauberes Research eingesetzt wird,
- ML-Ergebnisse **reproduzierbar, vergleichbar und erklärbar** bleiben.

Diese Policy gilt für:
- alle ML-basierten Strategien,
- alle hybriden (regelbasiert + ML) Strategien,
- alle GS- und Pre-Live-Phasen.

---

## Grundsatz

> **Machine Learning ist ein Werkzeug zur Signalverdichtung –  
> kein Beweis für eine Edge.**

Ein ML-Modell ist nur dann akzeptabel, wenn es:
- gegen einfache Baselines besteht,
- unter strengen zeitlichen Restriktionen validiert wurde,
- auch scheitern durfte.

---

## 1. ML nur auf GS-Baseline aufbauend

### 1.1 Baseline-Pflicht
- ML darf **nur** eingesetzt werden, wenn:
  - eine regelbasierte oder triviale GS-Baseline existiert,
  - diese Baseline dokumentiert ist,
  - ML explizit als *Verbesserung* gegen diese Baseline getestet wird.

**Verboten**
- ML ohne Vergleich zu:
  - Buy & Hold
  - Flat / Random
  - einfacher regelbasierter Strategie

---

## 2. Daten- und Feature-Integrität

### 2.1 Point-in-Time-Features
- Alle Features müssen:
  - zum Entscheidungszeitpunkt verfügbar sein,
  - explizit gelaggt (lagged) sein,
  - zeitlich eindeutig referenziert werden.

**Verboten**
- Rolling-Features ohne saubere Lag-Definition
- Globale Normalisierung über den gesamten Datensatz

---

### 2.2 Feature-Selektion
- Feature-Auswahl darf:
  - **nicht** auf Test- oder OOS-Daten basieren,
  - **nicht** iterativ „nach Ergebnis“ erfolgen.

Zulässig:
- Auswahl im Trainingsfenster
- Domänengetriebene Feature-Sets

---

## 3. Labeling-Regeln

### 3.1 Label-Definition
- Labels müssen:
  - zeitlich eindeutig definiert sein (z. B. Forward-Return über Horizon H),
  - unabhängig von späteren Trades berechnet werden.

**Verboten**
- Labels, die implizit Trade-Entscheidungen vorwegnehmen
- Dynamisches Re-Labeling nach Ergebnisqualität

---

### 3.2 Horizon-Konsistenz
- Feature-Horizont, Label-Horizont und Trading-Horizont
  müssen **konsistent** sein.

Inkonsistente Horizonte gelten als Designfehler.

---

## 4. Cross-Validation für Finanzzeitreihen

### 4.1 Verbot klassischer CV
- Klassische k-Fold-CV ist **nicht zulässig** für Finanzzeitreihen.

---

### 4.2 Zulässige CV-Methoden
Erlaubt sind ausschließlich zeitbewusste Verfahren:
- Walk-Forward Validation
- Purged k-Fold CV
- Combinatorial Purged CV (CPCV)
- Embargo-Zonen zwischen Train/Test

---

### 4.3 Embargo
- Zwischen Trainings- und Testfenstern muss
  ein explizites Embargo liegen, um Leakage zu vermeiden.

---

## 5. Modell- und Hyperparameter-Disziplin

### 5.1 Hyperparameter-Tuning
- Hyperparameter-Tuning darf:
  - nur im Trainingsfenster erfolgen,
  - nicht iterativ auf Test-Ergebnisse reagieren.

**Verboten**
- „Weiterdrehen“, bis das Ergebnis gut aussieht

---

### 5.2 Modellkomplexität
- Komplexere Modelle müssen:
  - einen klaren Mehrwert gegenüber einfacheren Modellen zeigen,
  - stabilere Ergebnisse liefern, nicht nur bessere Punktwerte.

Komplexität ohne Robustheitsgewinn ist abzulehnen.

---

## 6. Bewertung & Akzeptanzkriterien

### 6.1 Metriken
ML-Modelle werden **nicht** primär anhand klassischer ML-Metriken akzeptiert.

Relevant sind:
- Netto-ROI (nach Kosten)
- Drawdown
- Stabilität über Zeitfenster
- Performance-Konsistenz über CV-Splits

Accuracy, AUC oder RMSE sind **sekundär**.

---

### 6.2 Overfitting-Checks
Pflichtprüfungen:
- Performance-Verteilung über CV-Splits
- Vergleich gegen Random-Labels
- Robustheit bei leicht veränderten Parametern

Ein einzelner „Top-Run“ ist bedeutungslos.

---

## 7. Integration in Backtests

### 7.1 Trennung von Training und Trading
- Modelle dürfen:
  - **nicht** kontinuierlich auf denselben Daten nachtrainiert werden,
  - ohne explizite Re-Train-Logik.

---

### 7.2 Re-Training
- Re-Training ist nur zulässig, wenn:
  - Zeitpunkt
  - Datenfenster
  - Versionierung

klar definiert sind.

---

## 8. Vergleich & Baseline-Gates

### 8.1 Pflichtvergleich
Ein ML-Modell wird nur akzeptiert, wenn es:
- eine einfache Baseline **klar und reproduzierbar** schlägt,
- dies über mehrere Zeitfenster hinweg tut.

---

### 8.2 Negativtests
Pflicht:
- Test mit Random-Features oder Random-Labels
- Erwartung: keine signifikante Performance

Wenn doch: Leakage-Verdacht.

---

## 9. Transparenz & Reproduzierbarkeit

### 9.1 Dokumentation
Jeder ML-Run muss dokumentieren:
- Feature-Set
- Label-Definition
- CV-Methode
- Hyperparameter
- Seed
- Datenfenster

---

### 9.2 Reproduzierbarkeit
- ML-Ergebnisse müssen:
  - deterministisch reproduzierbar sein (Seeds, Versionen),
  - versioniert abgelegt werden.

---

## 10. Verbotene Praktiken (Null-Toleranz)

Explizit verboten:
- Training auf Testdaten
- Feature-Engineering über gesamte Zeitreihen
- CV ohne zeitliche Trennung
- Auswahl „nach bestem Ergebnis“
- Black-Box-Modelle ohne Diagnose

---

## 11. Durchsetzung

Diese Policy ist **verbindlich**.

ML-Ergebnisse, die gegen diese Regeln verstoßen:
- gelten als ungültig,
- werden nicht weiter analysiert,
- fließen nicht in Strategieentscheidungen ein.

---

## Status

Gültig für:
- GS-Phase (Pre-Live)
- alle ML-Experimente
- alle hybriden Strategien

Diese Policy ergänzt und erweitert:
- `backtest_integrity_policy.md`

Letzte Aktualisierung: 2026-01
