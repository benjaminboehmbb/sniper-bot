# LIVE DESIGN — L1-C GUARD & KILL-SWITCH RULES
Projekt: Sniper-Bot
Datum: 2026-01-10
Status: VERBINDLICH (L1)

---

## Zweck dieses Dokuments

Dieses Dokument definiert die verbindlichen Regeln
für Guards und Kill-Switches im Paper Trading (L1).

Es beschreibt WANN Guards greifen,
WAS sie auslösen
und WAS sie ausdrücklich nicht tun dürfen.

Keine Implementierung, keine Optimierung.

---

## Grundsatz

Guards schützen das System,
nicht die Strategie.

Bei Unsicherheit gilt:
BLOCK > PAUSE > STOP > EXIT

Kein Guard darf Entscheidungen „reparieren“.

---

## Guard-Kategorien (verbindlich)

### G1 — Daten-Guards

Schützen vor fehlerhaften Markt- oder Signal-Daten.

Auslöser:
- data_valid == false
- Zeitstempel nicht monoton
- fehlende Pflichtfelder
- ungültige Signalwerte

Reaktion:
- Blockiere Intent
- Setze Systemstatus = DEGRADED
- Kein Kill-Level-Anstieg beim ersten Auftreten

---

### G2 — Intent-Guards

Schützen vor inkonsistenter Policy-Ausgabe.

Auslöser:
- gleichzeitige BUY & SELL-Intents
- Intent ohne gültigen Snapshot
- Intent außerhalb erlaubter Marktphase

Reaktion:
- Intent verwerfen
- anomaly_counter++
- bei Schwelle → Kill-Level = SOFT

---

### G3 — Risk-Guards

Schützen vor Regel- und Limitverletzungen.

Auslöser:
- Trade-Limit überschritten
- Cooldown aktiv
- Verlust-Limit erreicht

Reaktion:
- Blockiere Order
- Kill-Level = SOFT oder HARD (je nach Regel)
- keine automatische Rücknahme

---

### G4 — Execution-Guards

Schützen vor fehlerhafter Orderausführung.

Auslöser:
- Order-Reject
- Timeout
- Partial Fill (nicht explizit erlaubt)

Reaktion:
- Kill-Level = HARD
- sofortiger Trading-Stop
- manuelles Reset erforderlich

---

### G5 — System-Guards

Schützen vor technischer Instabilität.

Auslöser:
- Heartbeat-Ausfall
- Resource-Limit
- Clock Drift
- Prozess-Fehler

Reaktion:
- Kill-Level = EMERGENCY
- Prozess-Exit
- kein Auto-Restart

---

## Kill-Switch-Regeln (verbindlich)

### Kill-Level

- NONE: Normalbetrieb
- SOFT: keine neuen Orders
- HARD: Trading-Loop stoppen
- EMERGENCY: Prozess beenden

---

### Kill-Level-Übergänge

- Kill-Level dürfen nur steigen
- kein automatisches Senken
- Rücksetzung nur manuell und explizit

---

## Manuelle Eingriffe

Erlaubt:
- manueller SOFT-Kill
- manueller HARD-Kill
- manueller EMERGENCY-Kill

Nicht erlaubt:
- manuelles Umgehen einzelner Guards
- selektives Deaktivieren von Kill-Switches
- „temporäre Ausnahmen“

---

## Logging-Pflichten

Jeder Guard-Trigger MUSS loggen:
- Guard-Typ
- Auslöser
- vorheriges Kill-Level
- neues Kill-Level
- Zeitstempel

Kein Guard darf still auslösen.

---

## Verbotene Praktiken

- Guard-basierte Strategieanpassung
- dynamische Limitanpassung
- automatische Recovery
- Retry-Logik
- Guard-Bypass im Betrieb

---

## Erfolgskriterium (L1-C)

L1-C gilt als erfüllt, wenn:
- jeder Guard deterministisch reagiert
- jeder Kill-Level-Wechsel erklärbar ist
- kein Guard unbemerkt bleibt
- kein Guard Logik beeinflusst

---

## Zentrale Invariante

Guards dürfen den Fluss stoppen,
aber niemals den Inhalt verändern.

---

## Abschluss

Mit diesen Regeln sind Guards
ein defensives Sicherheitsnetz,
kein Steuerungsinstrument.

Jede Abweichung ist ein Designfehler.
