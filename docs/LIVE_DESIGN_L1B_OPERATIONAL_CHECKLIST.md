L1-B BETRIEBSCHECKLISTE — PAPER TRADING (NORMALBETRIEB)

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Gültigkeit: verbindlich
Scope: Betrieb & Beobachtung – kein Code, kein Design

================================================================
0) Geltungsbereich & Stop-Regel
================================================================
- Gilt ausschließlich für L1 Paper Trading
- Keine echten Orders
- Wenn Systemverhalten nicht ausschließlich per Logs erklärbar ist:
  → Betrieb sofort stoppen (L1-B Verstoß)

================================================================
1) Pre-Flight vor jedem Start
================================================================
1.1 Environment
- WSL aktiv
- venv aktiv
- korrektes Projektroot
- nur eine L1-Instanz läuft

1.2 Log- & State-Pfade
- Logfile append-only
- State-Dateien (S2, S4) append-only
- keine Rotation, kein Überschreiben

1.3 Erwartung
- Execution nur Stub
- erwartetes Event: order_not_sent

================================================================
2) Normalbetrieb pro Tick (Soll-Sequenz)
================================================================
Ein gültiger Tick ist vollständig rekonstruierbar als:

Snapshot
→ Validation
→ Intent
→ Guards
→ Execution (Stub)
→ State Update
→ Persistenz
→ Loop Delay

Pflicht-Events pro Tick (Minimum):
- L2 snapshot_received
- L2 data_valid ODER data_invalid
- L3 intent_created (nur wenn data_valid)
- L5 order_not_sent (nur wenn Intent erlaubt)
- L6 state_update
- L6 state_persisted
- L1 loop_delay

Pflichtfelder je Log:
- timestamp_utc
- category
- event
- severity
- system_state_id
- intent_id (falls Intent existiert)

================================================================
3) Normalbetrieb pro Run
================================================================
- Run startet mit: system_start
- Run endet mit: system_stop
- system_state_id ist während des Runs konstant
- Nach Restart: neue system_state_id
- Keine State- oder Intent-Übernahme über Runs hinweg

================================================================
4) Abweichungen & Sofortmaßnahmen
================================================================

4.1 Log-Lücken
Symptome:
- fehlende Events im Tick
- keine loop_delay Events
- kein system_stop

Maßnahme:
- sofort stoppen
- Klassifikation: Observability-Defekt

---------------------------------------------------------------

4.2 State-Drift (S2 / S4)
Symptome:
- S2 != FLAT
- Kill-Level nicht monoton
- Persistenz fehlt oder stoppt

Maßnahme:
- sofort stoppen
- maximal ein Restart-Smoke-Test erlaubt

---------------------------------------------------------------

4.3 Kill-Level-Anomalien
Symptome:
- Kill-Level-Wechsel ohne erklärenden Log-Kontext
- Rücksprung des Kill-Levels
- Kill-Level-Flapping

Maßnahme:
- sofort stoppen
- Klassifikation: Guard-/Observability-Defekt

---------------------------------------------------------------

4.4 Intent-/Execution-Inkonsistenz
Symptome:
- Execution ohne Intent
- mehrere Intents pro Tick
- Intent ohne Snapshot-Bezug

Maßnahme:
- sofort stoppen
- Klassifikation: Traceability-Verlust

---------------------------------------------------------------

4.5 Zeit- & Monotoniefehler
Symptome:
- timestamp_utc nicht monoton
- Clock-Drift
- Out-of-order Snapshots

Maßnahme:
- sofort stoppen
- Systemzeit prüfen

================================================================
5) Restart-Checks (Pflicht)
================================================================
Ein Restart ist nur gültig, wenn:
- neuer system_start
- neue system_state_id
- S2 = FLAT
- Kill-Level = NONE
- keine Alt-Intents
- Persistenz bleibt append-only

Wenn nicht erfüllt → Stop

================================================================
6) Daily Minimum Checks
================================================================
- system_start / system_stop vorhanden
- Stichprobe von mindestens 3 Ticks:
  - vollständige Sequenz
  - keine fehlenden Pflichtfelder
- State-Dateien wachsen weiter
- keine kaputten JSONL-Zeilen

================================================================
7) Betriebsampel
================================================================
GREEN:
- vollständige Tick-Sequenzen
- erklärbare Kill-Level
- stabile Persistenz

YELLOW:
- gelegentlich data_invalid
- SOFT Kill-Level erklärbar
- kein Flapping

RED:
- Log-Lücke
- nicht erklärbarer Kill-Level
- State-Drift
- fehlende Pflichtfelder

================================================================
8) Definition Normalbetrieb
================================================================
L1 gilt als korrekt betrieben, wenn:
- jeder Tick rekonstruierbar ist
- jede Blockierung begründet ist
- kein kritisches Ereignis ungeloggt bleibt

ENDE L1-B BETRIEBSCHECKLISTE
