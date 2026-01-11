LIVE_DESIGN_L1_ALARM_CRITERIA_FINAL

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: FINAL / EINGEFROREN
Zweck: Definition harter Alarm-Kriterien für automatischen L1-Health-Check
Scope: rein lesend, kein Eingriff, keine Umsetzung im Core

================================================================
0) Grundsatz
================================================================
Dieses Dokument definiert die finalen Alarm-Kriterien
für den L1-Betrieb.

Die Kriterien werden:
- einmal festgelegt
- automatisiert geprüft
- nicht manuell täglich abgearbeitet

Der Operator reagiert ausschließlich auf das
Vorhandensein eines Alarms.

================================================================
1) Alarm-Semantik (verbindlich)
================================================================
- Es gibt nur zwei Zustände: OK oder ALARM
- Kein Warnstatus
- Kein Scoring
- Kein Interpretationsspielraum

Ein einziges erfülltes Kriterium genügt für ALARM.

================================================================
2) Alarm-Kategorie A: Log-Integrität
================================================================
ALARM, wenn eines zutrifft:

A1) Kein system_start im aktuellen oder letzten Run
A2) Kein system_stop nach Prozessende
A3) Unvollständiger Tick
    (fehlendes Pflicht-Event:
     snapshot / validation / intent /
     execution_stub / state / persist / delay)

================================================================
3) Alarm-Kategorie B: State-Invarianten
================================================================
ALARM, wenn eines zutrifft:

B1) S2.position != FLAT
B2) S2.size != 0
B3) S4.kill_level != NONE ohne erklärendes Log

================================================================
4) Alarm-Kategorie C: Kill-Level-Logik
================================================================
ALARM, wenn eines zutrifft:

C1) Kill-Level springt rückwärts
C2) Kill-Level flapped
    (mehrfacher Wechsel ohne Kontext)
C3) Kill-Level != NONE über längere Zeit
    ohne data_invalid-Ursache

================================================================
5) Alarm-Kategorie D: Zeit & Rhythmus
================================================================
ALARM, wenn eines zutrifft:

D1) timestamp_utc nicht monoton
D2) Keine neuen Log-Einträge über definierte Zeit
    (Empfehlung: 2 × decision_tick × Sicherheitsfaktor,
     typischerweise 5–10 Minuten)

================================================================
6) Alarm-Kategorie E: Persistenz
================================================================
ALARM, wenn eines zutrifft:

E1) state_persisted fehlt nach state_update
E2) State-Dateien wachsen nicht weiter
E3) Ungültige oder kaputte JSONL-Zeilen

================================================================
7) Alarm-Kategorie F: Traceability
================================================================
ALARM, wenn eines zutrifft:

F1) Execution-Event ohne Intent
F2) Intent ohne Snapshot
F3) Mehr als ein Intent pro Tick

================================================================
8) Alarm-Auslösung (final)
================================================================
Wenn irgendein Kriterium aus A–F zutrifft:

→ ALARM

ALARM bedeutet:
- L1 stoppen
- Logs lesen
- keine Fixes im Betrieb
- keine automatische Recovery

================================================================
9) Operator-Pflicht bei Alarm
================================================================
Der Operator MUSS:

- den L1-Betrieb stoppen
- den Alarm dokumentieren
- Analyse außerhalb des Betriebs durchführen

Der Operator DARF NICHT:

- Alarme ignorieren
- im Betrieb fixen
- Kriterien abschwächen

================================================================
10) Freeze-Hinweis
================================================================
Dieses Dokument ist eingefroren.

Änderungen sind nur zulässig mit:
- neuem Mandat
- neuem Dokument
- expliziter Freigabe

================================================================
ENDE L1 ALARM CRITERIA FINAL
