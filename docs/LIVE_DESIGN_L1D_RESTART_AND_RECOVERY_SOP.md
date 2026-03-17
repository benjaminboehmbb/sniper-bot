LIVE_DESIGN_L1D_RESTART_AND_RECOVERY_SOP

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: verbindlich
Scope: Betrieb – Restart & Recovery
Kein Code, kein Design, keine Optimierung

================================================================
0) Zweck & Grundsatz
================================================================
Diese SOP definiert den einzig zulässigen Restart- und Recovery-
Ablauf für L1 Paper Trading.

Ziel:
- kontrollierter Neustart
- kein State-Leak
- vollständige Nachvollziehbarkeit
- deterministisches Verhalten

Jeder Restart ist ein Betriebsereignis
und muss vollständig erklärbar sein.

================================================================
1) Zulässige Restart-Auslöser
================================================================
Ein Restart ist NUR erlaubt bei:

- manuellem Operator-Stop
- geplantem Session-Ende
- L1-B Verstoß mit klarer Diagnose
- Systemneustart (OS / WSL)

Nicht zulässig:
- automatischer Restart
- Restart zur „Fehlerbehebung“
- Restart zur Performance-Verbesserung

================================================================
2) Vorbedingungen für Restart
================================================================
Vor jedem Restart MUSS geprüft sein:

- aktueller Run ist beendet ODER bewusst gestoppt
- kein laufender Live-Prozess
- Logfile und State-Dateien sind zugreifbar
- letzter Run zeigt entweder:
  - system_stop
  - oder klaren Abbruchpunkt

Wenn unklar → Restart NICHT durchführen.

================================================================
3) Restart-Ablauf (verbindliche Reihenfolge)
================================================================
3.1 Alt-Run beenden
- Prozess explizit stoppen
- keine parallelen Instanzen zulassen

3.2 Log-Check (kurz)
- letzter Eintrag erklärbar
- kein offenes Execution-Ereignis
- keine halbfertigen State-Updates

3.3 Neustart durchführen
- neuer Prozessstart
- neue system_state_id MUSS erzeugt werden

================================================================
4) Erwartetes Verhalten nach Restart
================================================================
Direkt nach Restart MUSS gelten:

- erstes Log-Ereignis: system_start
- neue system_state_id
- Kill-Level initial: NONE
- S2 Position: FLAT
- keine Alt-Intents
- keine Alt-Order-Referenzen

Wenn eines davon nicht erfüllt ist:
→ Restart FEHLGESCHLAGEN

================================================================
5) Persistenz-Invarianten
================================================================
Nach Restart MUSS gelten:

- Logfile ist append-only
- State-Dateien (S2, S4):
  - alte Zeilen bleiben erhalten
  - neue Zeilen kommen hinzu
- keine Überschreibung
- keine Leereinträge

Jede Verletzung ist ein L1-D Defekt.

================================================================
6) Restart-Smoke-Test (Pflicht)
================================================================
Nach jedem Restart:

- mindestens 1 vollständiger Tick
- vollständige Tick-Sequenz:
  snapshot → validation → intent → guards →
  execution_stub → state_update → persist → delay

Wenn der erste Tick unvollständig ist:
→ sofort stoppen

================================================================
7) Recovery-Regeln
================================================================
Recovery bedeutet in L1 AUSSCHLIESSLICH:

- Neustart mit leerem Entscheidungszustand
- keine Wiederaufnahme alter Logik
- keine Rekonstruktion vergangener Entscheidungen

Nicht erlaubt:
- Replay
- State-Reparatur
- manuelles „Glattziehen“

================================================================
8) Wiederholte Fehler
================================================================
Wenn derselbe Fehler nach Restart erneut auftritt:

- Betrieb aussetzen
- Fehler als strukturell klassifizieren
- KEINE weiteren Restarts

Erst Analyse außerhalb des Betriebs.

================================================================
9) Dokumentationspflicht
================================================================
Jeder Restart MUSS nachvollziehbar sein durch:

- system_stop (alt)
- system_start (neu)
- neue system_state_id
- saubere Tick-Sequenz

Fehlt eines:
→ Restart nicht gültig

================================================================
10) Definition erfolgreicher Restart
================================================================
Ein Restart gilt als erfolgreich, wenn:

- neue system_state_id aktiv
- erster Tick vollständig
- keine State-Leaks
- Persistenz korrekt
- Kill-Level stabil

ENDE L1-D RESTART & RECOVERY SOP
