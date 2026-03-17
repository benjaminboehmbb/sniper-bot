# LIVE DESIGN — L0 PAPER TRADING BOUNDARY
Projekt: Sniper-Bot  
Datum: 2026-01-10  
Status: VERBINDLICH (L0)

---

## Zweck dieses Dokuments

Dieses Dokument definiert die verbindliche Grenze zwischen:
- Live-Design (L0)
- Paper Trading Design (L1)

Es legt fest, unter welchen Bedingungen Paper Trading begonnen werden darf
und welche Anforderungen zwingend erfüllt sein müssen.

Paper Trading ist der erste betriebliche Modus,
aber weiterhin KEIN echtes Trading.

---

## Grundsatz

Paper Trading ist:
- ein Live-System ohne reale Kapitalwirkung
- ein Execution-Test, kein Performance-Test
- ein Stabilitäts- und Kontrolltest

Paper Trading dient NICHT der Optimierung,
nicht der Renditebewertung und nicht dem Lernen.

---

## Verbindliche Abgrenzung

### Was Paper Trading IST

- Nutzung des vollständigen Live-Loops (L0-E)
- Nutzung realer Markt-Feeds
- Nutzung realer Zeit
- Nutzung echter Guards & Kill-Switches
- Nutzung des vollständigen State-Modells

### Was Paper Trading NICHT IST

- kein Backtest
- keine Simulation
- kein Ersatz für GS
- keine Performance-Evaluierung
- keine Strategieauswahl

---

## Verbotene Aktivitäten im Paper Trading

- Vergleich mit GS-ROI
- Bewertung von Profitabilität
- Parametertuning
- Anpassung von Schwellenwerten
- Entfernen oder Abschwächen von Guards
- „Quick Fixes“ bei unerwartetem Verhalten

Paper Trading darf abbrechen,
aber nicht angepasst werden.

---

## Verbindliche Anforderungen vor Start von L1

Alle folgenden Punkte müssen erfüllt sein.

### Architektur
- L0-A bis L0-E vollständig dokumentiert
- keine offenen Design-Fragen
- keine impliziten Übergänge

### Guards & Sicherheit
- alle Kill-Switches implementiert
- manuelles Emergency-Stop vorhanden
- kein Auto-Recovery

### State
- Persistenz von S2 und S4 getestet
- Neustart-Szenarien geprüft
- kein State-Leak

### Beobachtbarkeit
- vollständiges Logging
- Order-Intent nachvollziehbar
- Kill-Switch-Auslösungen sichtbar

---

## Abbruchkriterien für Paper Trading

Paper Trading MUSS sofort beendet werden bei:

- ungeklärtem Order-Verhalten
- unerklärbarem Intent
- Guard-Fehlfunktion
- State-Inkonsistenz
- Health-Fehler
- manueller Entscheidung

Abbruch ist Erfolg, kein Scheitern.

---

## Explizite Nicht-Ziele

Paper Trading beantwortet NICHT:

- „Ist die Strategie profitabel?“
- „Ist das besser als GS?“
- „Kann man das skalieren?“
- „Ist das optimal?“

Diese Fragen sind ausdrücklich ausgeschlossen.

---

## Übergang zu L1 (Paper Trading Design)

L1 darf erst starten, wenn:

- dieses Dokument akzeptiert ist
- alle L0-Dokumente versioniert vorliegen
- ein expliziter Startbeschluss getroffen wurde

Kein impliziter Übergang ist erlaubt.

---

## Zentrale Invariante

Wenn im Paper Trading eine Entscheidung
nur mit Simulationsergebnissen erklärbar ist,
ist das Design ungültig.

---

## Abschluss

Mit L0-F ist der Übergang von Design zu Betrieb
formal abgesichert.

L0 gilt damit als vollständig abgeschlossen.
