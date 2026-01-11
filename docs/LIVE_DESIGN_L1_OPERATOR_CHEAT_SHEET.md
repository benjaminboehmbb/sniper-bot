LIVE_DESIGN_L1_OPERATOR_CHEAT_SHEET

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Zweck: Schnelle Orientierung für den täglichen Betrieb
Kein Code, keine Optimierung, keine Performance-Bewertung

============================================================
A) OPERATOR-GRUNDSATZ
============================================================
Beobachten > Dokumentieren > Stoppen

Wenn Verhalten nicht ausschließlich per Logs erklärbar ist:
→ STOP

============================================================
B) WAS IST ERLAUBT / VERBOTEN
============================================================
ERLAUBT
- L1 betreiben
- Logs lesen
- Checklisten anwenden
- Restart nach SOP
- Beobachtungen notieren

VERBOTEN
- Code ändern
- Guards/Policy erweitern
- Performance analysieren
- GS vergleichen
- „Nur kurz testen“

============================================================
C) NORMALER TICK (SOLL)
============================================================
snapshot_received
→ data_valid / data_invalid
→ intent_created (nur bei data_valid)
→ order_not_sent
→ state_update
→ state_persisted
→ loop_delay

Fehlt ein Schritt:
→ STOP

============================================================
D) RUN-REGELN
============================================================
- system_start am Anfang
- system_stop am Ende
- system_state_id bleibt im Run gleich
- neue system_state_id nach Restart

============================================================
E) STATE-INVARIANTEN (L1)
============================================================
S2:
- Position = FLAT
- Size = 0

S4:
- Kill-Level initial NONE
- Kill-Level monoton
- kein Rücksprung

Abweichung:
→ STOP

============================================================
F) KILL-LEVEL QUICK CHECK
============================================================
OK:
- NONE
- SOFT mit Kontext (z.B. data_invalid)

NICHT OK:
- Eskalation ohne Kontext
- Rücksprung
- Flapping

→ STOP

============================================================
G) TRACEABILITY
============================================================
- Execution nur mit Intent
- Intent nur mit Snapshot
- max. 1 Intent pro Tick

Verstoß:
→ STOP

============================================================
H) ZEIT & RHYTHMUS
============================================================
- timestamp_utc monoton
- loop_delay regelmäßig
- keine langen Log-Pausen

Verstoß:
→ STOP

============================================================
I) RESTART QUICK CHECK
============================================================
Nach Restart MUSS:
- system_start
- neue system_state_id
- S2 = FLAT
- Kill-Level = NONE
- erster Tick vollständig

Nicht erfüllt:
→ STOP

============================================================
J) AMPEL
============================================================
GREEN
- alles erklärbar
- keine Invarianten-Verletzung

YELLOW
- erklärbare Warnungen
- weiter beobachten

RED
- Log-Lücke
- State-Drift
- Kill-Level-Anomalie
- Zeit-/Persistenzfehler

Bei RED:
→ L1 stoppen
→ dokumentieren
→ nicht eingreifen

============================================================
K) ABSCHLUSSFRAGE
============================================================
Kann ich das beobachtete Verhalten
ausschließlich anhand der Logs erklären?

Wenn NEIN:
→ L1 nicht sicher betrieben

============================================================
ENDE L1 OPERATOR CHEAT-SHEET
