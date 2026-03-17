LIVE_DESIGN_L1_CONTINUOUS_OPERATION_MONITORING_CHECKLIST

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: verbindlich
Scope: Dauerbetrieb & Überwachung
Kein Code, kein Design, keine Optimierung

================================================================
0) Zweck & Grundsatz
================================================================
Diese Checkliste definiert die Überwachung von L1
während des fortlaufenden Betriebs (Dauerlauf).

Ziel:
- frühzeitige Fehlererkennung
- Vermeidung schleichender Defekte
- Sicherstellung der Observability
- kontrollierter, stabiler Dauerbetrieb

Kein Eingriff, solange GREEN.
Sofortiger Stop bei RED.

================================================================
1) Überwachungsfenster & Rhythmus
================================================================
- Kurzcheck: alle 15–30 Minuten
- Detailcheck: 1× pro Session / Tag
- Ad-hoc-Check: bei Warnsignalen oder Bauchgefühl

================================================================
2) Laufende Kernindikatoren (Live-Beobachtung)
================================================================

2.1 Prozess & Loop
- Prozess läuft stabil
- keine Hänger
- loop_delay Events erscheinen regelmäßig
- keine Tick-Staus

Warnsignal:
- loop_delay fehlt oder verzögert
→ sofort prüfen

---------------------------------------------------------------

2.2 Logging-Kontinuität
- Logs wachsen kontinuierlich
- keine längeren Zeiträume ohne Einträge
- Kategorien L1–L6 erscheinen erwartungsgemäß

Warnsignal:
- Log-Stillstand bei laufendem Prozess
→ RED

---------------------------------------------------------------

2.3 Tick-Struktur (Stichprobe)
- Stichprobe von 1–2 Ticks:
  - vollständige Soll-Sequenz vorhanden
  - keine fehlenden Pflicht-Events
  - intent_id nur bei Intent

Warnsignal:
- unvollständiger Tick
→ RED

================================================================
3) State-Überwachung (S2 / S4)
================================================================

3.1 Position State (S2)
- Position bleibt FLAT
- Size = 0
- kein Wechsel erlaubt

Abweichung:
→ sofort stoppen

---------------------------------------------------------------

3.2 Risk State (S4)
- Kill-Level monoton
- keine Rücksprünge
- kein Flapping

Warnsignal:
- mehrfacher Wechsel ohne Kontext
→ Stop & Diagnose

================================================================
4) Kill-Level-Überwachung
================================================================
Erwartetes Verhalten:
- NONE im Normalbetrieb
- SOFT nur erklärbar (z.B. data_invalid)
- kein HARD / EMERGENCY in L1 Normalbetrieb

Warnsignale:
- unerklärte Eskalation
- Kill-Level bleibt erhöht
- häufige Wechsel

Maßnahme:
- RED → sofort stoppen

================================================================
5) Persistenz-Überwachung
================================================================
- State-Dateien wachsen weiter
- jede State-Aktualisierung wird persistiert
- keine kaputten JSONL-Zeilen

Warnsignale:
- Persistenz-Event fehlt
- Datei wächst nicht weiter
- Schreibfehler

Maßnahme:
- sofort stoppen

================================================================
6) Zeit- & Monotonie-Checks
================================================================
- timestamp_utc monoton steigend
- keine Zeit-Sprünge
- keine Clock-Drift-Warnungen

Warnsignal:
- Zeitinkonsistenz
→ Stop & Systemzeit prüfen

================================================================
7) Restart-Indikatoren im Dauerlauf
================================================================
Unerwartete Restart-Zeichen:
- system_start ohne Operator-Aktion
- neue system_state_id ohne geplanten Restart

Maßnahme:
- sofort stoppen
- als kritisches Ereignis klassifizieren

================================================================
8) Betriebsampel (Entscheidungslogik)
================================================================
GREEN:
- vollständige Logs
- stabile Tick-Sequenz
- Kill-Level NONE oder erklärbar
- Persistenz stabil

YELLOW:
- gelegentliche data_invalid
- kurze Warnungen, erklärbar
- keine strukturellen Abweichungen

RED:
- Log-Lücke
- State-Drift
- Kill-Level-Anomalie
- Zeit-/Persistenzfehler

Bei RED:
- Betrieb sofort stoppen
- kein automatischer Restart

================================================================
9) Dokumentationspflicht
================================================================
Bei Auffälligkeiten festhalten:
- Uhrzeit
- system_state_id
- Kategorie / Event
- eigene Beobachtung

Keine Interpretation während Betrieb.

================================================================
10) Definition stabiler Dauerlauf
================================================================
L1 gilt als stabil im Dauerbetrieb, wenn:
- über längere Zeiträume keine RED-Ereignisse auftreten
- alle Abweichungen erklärbar sind
- Logs den gesamten Betrieb vollständig abbilden

ENDE L1 DAUERLAUF-ÜBERWACHUNGSCHECKLISTE
