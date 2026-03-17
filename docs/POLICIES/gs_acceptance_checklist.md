# Sniper-Bot – GS Acceptance Checklist

## Zweck

Diese Checkliste ist die **verbindliche Abnahmeprüfung** für alle
Strategien, Modelle und Experimente im Sniper-Bot-Projekt.

Eine Strategie gilt **nur dann als GS-akzeptiert**, wenn **alle Pflichtpunkte**
mit **JA** beantwortet werden.

Nicht erfüllte Punkte bedeuten:
- keine Weiterverfolgung,
- kein Vergleich,
- keine Archivierung als GS-Ergebnis.

---

## Abschnitt A – Allgemeine Angaben (Pflicht)

- [ ] Strategie-ID / Name eindeutig definiert
- [ ] Datum & Zeitstempel des Runs dokumentiert
- [ ] Code-Version (Commit / Hash) dokumentiert
- [ ] Datensatz-Version eindeutig referenziert
- [ ] Parameter-Set vollständig dokumentiert

**Wenn ein Punkt fehlt → STOP**

---

## Abschnitt B – Backtest-Integrität (Pflicht)

### Zeitliche Integrität
- [ ] Kein Look-Ahead Bias nachweisbar
- [ ] Entscheidungszeitpunkt klar von Ausführung getrennt
- [ ] Signal basiert ausschließlich auf Daten ≤ Entscheidungszeitpunkt
- [ ] Ausführung frühestens t+1 oder explizit modelliert

### Datenintegrität
- [ ] Point-in-Time-Daten verwendet
- [ ] Keine Survivorship-Bereinigung ohne Kennzeichnung
- [ ] Missing-Data-Handling explizit definiert
- [ ] Keine implizite Interpolation

### Kosten & Execution
- [ ] Transaktionskosten enthalten
- [ ] Slippage/Spread modelliert oder konservativ angenommen
- [ ] Keine impliziten Mid-Price-Fills ohne Begründung

**Wenn ein Punkt NEIN → GS-Ablehnung**

---

## Abschnitt C – Kapital & Risiko (Pflicht)

- [ ] Kapitalbindung korrekt modelliert
- [ ] Keine Mehrfachverwendung desselben Kapitals
- [ ] Positionsgrößen explizit und reproduzierbar
- [ ] Leverage klar definiert oder ausgeschlossen
- [ ] Drawdowns vollständig sichtbar (keine Glättung)

---

## Abschnitt D – Statistik & Robustheit (Pflicht)

- [ ] Ausreichende Laufzeit des Backtests
- [ ] Ausreichende Anzahl unabhängiger Trades
- [ ] Ergebnis nicht von Einzelereignissen dominiert
- [ ] In-Sample / Out-of-Sample getrennt
- [ ] Walk-Forward oder vergleichbare Robustheitsprüfung

---

## Abschnitt E – Baseline- & Vergleichstests (Pflicht)

- [ ] Vergleich gegen triviale Baseline (Buy&Hold / Flat / Random)
- [ ] Vergleich gegen bestehende GS-Referenzen
- [ ] Überlegenheit reproduzierbar über mehrere Zeitfenster
- [ ] Kein Cherry Picking einzelner Zeiträume

---

## Abschnitt F – ML-spezifisch (nur wenn ML verwendet)

### ML-Grundlagen
- [ ] Regelbasierte GS-Baseline existiert
- [ ] ML-Modell explizit als Verbesserung definiert
- [ ] Feature-Horizont, Label-Horizont und Trading-Horizont konsistent

### Features & Labels
- [ ] Alle Features point-in-time korrekt
- [ ] Keine globale Normalisierung
- [ ] Label sauber definiert (Forward-Return etc.)
- [ ] Kein Re-Labeling nach Ergebnis

### Validation
- [ ] Zeitbewusste CV-Methode (Walk-Forward / Purged CV / CPCV)
- [ ] Embargo-Zonen korrekt implementiert
- [ ] Hyperparameter-Tuning nur im Trainingsfenster

### Overfitting-Checks
- [ ] Performance stabil über CV-Splits
- [ ] Negativtest mit Random-Labels durchgeführt
- [ ] Komplexeres Modell schlägt einfacheres robust

**Wenn ein ML-Punkt NEIN → ML-Ergebnis ungültig**

---

## Abschnitt G – Reproduzierbarkeit & Dokumentation (Pflicht)

- [ ] Run deterministisch reproduzierbar
- [ ] Random-Seeds dokumentiert
- [ ] Ergebnisse versioniert abgelegt
- [ ] Alle relevanten Artefakte gespeichert (Logs, CSVs)

---

## Abschnitt H – Abschlussentscheidung

- [ ] **ALLE Pflichtpunkte erfüllt**

Wenn **JA**:
> Strategie darf als **GS-akzeptiert** markiert werden.

Wenn **NEIN**:
> Strategie ist **nicht GS-fähig** und wird nicht weitergeführt.

---

## Hinweis

Diese Checkliste ist **kein Vorschlag**, sondern ein **Gate**.

Abweichungen sind nur zulässig, wenn:
- sie explizit dokumentiert,
- fachlich begründet,
- und als **bewusste Ausnahme** gekennzeichnet sind.

---

## Status

Gültig für:
- GS-Phase (Pre-Live)
- alle Strategie- und ML-Experimente

Bezieht sich auf:
- `backtest_integrity_policy.md`
- `ml_validation_policy.md`

Letzte Aktualisierung: 2026-01
