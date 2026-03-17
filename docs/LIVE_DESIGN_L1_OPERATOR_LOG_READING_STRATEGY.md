LIVE_DESIGN_L1_OPERATOR_LOG_READING_STRATEGY

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: verbindlich
Zweck: Strukturierte, sichere Log-Analyse aus Operator-Sicht
Kein Code, keine Interpretation, keine Optimierung

================================================================
0) Grundsatz (Operator-Haltung)
================================================================
Logs werden gelesen, nicht bewertet.

Ziel ist:
- Nachvollziehbarkeit
- Früherkennung von Abweichungen
- Verifikation des Normalbetriebs

Nicht Ziel:
- Performance-Bewertung
- Ursachenanalyse auf Code-Ebene
- Verbesserungsdiskussion

================================================================
1) Lesereihenfolge (immer gleich)
================================================================
Logs werden IMMER in dieser Reihenfolge gelesen:

1) Run-Ebene
2) Tick-Ebene
3) Guard- & Kill-Level-Ebene
4) State- & Persistenz-Ebene
5) Zeit- & Rhythmus-Ebene

Keine Abkürzungen.
Keine Sprünge.

================================================================
2) Run-Ebene (Makro-Check)
================================================================
Zuerst prüfen:

- Gibt es genau einen system_start?
- Gibt es ein system_stop ODER läuft der Prozess noch?
- Bleibt system_state_id innerhalb des Runs konstant?
- Gibt es unerwartete system_start-Ereignisse?

Warnsignal:
- system_start ohne Operator-Aktion
- fehlendes system_stop nach Beendigung

Maßnahme:
- bei Unklarheit → STOP

================================================================
3) Tick-Ebene (Strukturprüfung)
================================================================
Stichprobe: 1–3 repräsentative Ticks

Für jeden Tick prüfen:

Soll-Sequenz:
- snapshot_received
- data_valid ODER data_invalid
- intent_created (nur wenn data_valid)
- order_not_sent (nur wenn Intent erlaubt)
- state_update
- state_persisted
- loop_delay

Pflicht:
- keine ausgelassenen Schritte
- keine doppelten Events
- maximal ein Intent pro Tick

Warnsignal:
- fehlender Schritt
- Reihenfolge verletzt

Maßnahme:
- STOP

================================================================
4) Intent- & Traceability-Prüfung
================================================================
Für jeden Intent gilt:

- intent_created hat snapshot-Bezug
- intent_id ist eindeutig
- intent_id erscheint nur in:
  - Guards
  - Execution
  - State-Kontext

Nicht erlaubt:
- Execution ohne Intent
- Intent ohne Snapshot
- mehrere Intents pro Tick

Warnsignal:
- Traceability-Lücke

Maßnahme:
- STOP

================================================================
5) Guard- & Kill-Level-Lesestrategie
================================================================
Kill-Level wird nur LESEND geprüft:

Erwartung:
- initial NONE
- monotone Eskalation
- keine Rücksprünge

Prüfen:
- gibt es einen erklärenden Kontext vor Eskalation?
- tritt Kill-Level-Flapping auf?

Warnsignale:
- Eskalation ohne Kontext
- Rücksprung
- häufige Wechsel

Maßnahme:
- STOP

================================================================
6) State- & Persistenz-Prüfung
================================================================
State-Logs prüfen auf:

S2 (Position):
- immer FLAT
- size = 0

S4 (Risk):
- Kill-Level konsistent
- cooldown nur wenn erklärt

Persistenz:
- state_persisted erscheint nach state_update
- State-Dateien wachsen weiter
- keine kaputten JSONL-Zeilen

Warnsignal:
- fehlende Persistenz
- State-Drift

Maßnahme:
- STOP

================================================================
7) Zeit- & Rhythmus-Prüfung
================================================================
Zeit wird ausschließlich formal geprüft:

- timestamp_utc monoton
- loop_delay regelmäßig
- kein Tick-Stau
- keine Zeit-Sprünge

Warnsignal:
- Zeitinkonsistenz
- lange Pausen ohne loop_delay

Maßnahme:
- STOP

================================================================
8) Umgang mit data_invalid
================================================================
data_invalid ist erlaubt, wenn:

- korrekt geloggt
- erklärbar
- Guard reagiert deterministisch

Nicht erlaubt:
- stilles Ignorieren
- fehlende Reaktion
- Inkonsistenz im Folgetick

Warnsignal:
- data_invalid ohne Konsequenz

Maßnahme:
- STOP

================================================================
9) Operator-Notizen (Pflicht bei Auffälligkeit)
================================================================
Wenn etwas auffällt, notieren:

- Uhrzeit
- system_state_id
- Event / Kategorie
- kurze Beschreibung

Keine Interpretation.
Keine Lösungsvorschläge.

================================================================
10) Abschlussfrage (nach jeder Log-Session)
================================================================
Kann ich den gesamten beobachteten Ablauf
ausschließlich anhand der Logs erklären?

Wenn NEIN:
→ L1 nicht sicher betrieben

================================================================
11) Operator-Regel
================================================================
Lesen ≠ Verstehen ≠ Eingreifen

Eingreifen nur bei:
- RED-Ereignis
- Invarianten-Verletzung
- Observability-Lücke

================================================================
ENDE L1 OPERATOR LOG-LESESTRATEGIE
