LIVE_DESIGN_L1_DAILY_OPERATION_ROUTINE

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: verbindlich
Zweck: Strukturierte Tagesroutine für stabilen L1-Betrieb
Kein Code, keine Optimierung, keine Performance-Bewertung

================================================================
0) Grundsatz der Tagesroutine
================================================================
Diese Routine stellt sicher, dass L1:
- stabil betrieben wird
- frühzeitig Abweichungen erkennt
- nicht unbemerkt aus dem Scope driftet

Die Routine ist verbindlich.
Abkürzungen sind nicht erlaubt.

================================================================
1) MORNING ROUTINE (Tagesstart)
================================================================
Ziel:
- sicherer Start oder sichere Fortsetzung von L1
- Verifikation des Ausgangszustands

---------------------------------------------------------------
1.1 Kontext-Check
---------------------------------------------------------------
- Ist heute ein L1-Betriebstag? (ja/nein)
- Wird KEINE neue Phase gestartet?
- Liegt kein offenes RED-Ereignis vom Vortag vor?

Wenn RED offen:
→ L1 NICHT starten

---------------------------------------------------------------
1.2 Prozess- & Run-Status
---------------------------------------------------------------
- Läuft L1 bereits?
  - ja: system_state_id notieren
  - nein: kontrollierter Start gemäß L1-D SOP

- Keine parallelen Instanzen

---------------------------------------------------------------
1.3 Log-Startprüfung
---------------------------------------------------------------
- letzter system_start erklärbar
- keine ungeplanten Restarts
- Logfile wächst

---------------------------------------------------------------
1.4 State-Startprüfung
---------------------------------------------------------------
- S2 = FLAT
- S4 Kill-Level = NONE
- Persistenz-Dateien intakt

Wenn Abweichung:
→ STOP

---------------------------------------------------------------
1.5 Kurz-Stichprobe (1 Tick)
---------------------------------------------------------------
- vollständige Tick-Sequenz
- keine Log-Lücken
- loop_delay vorhanden

Ergebnis:
[ ] GREEN
[ ] YELLOW
[ ] RED (→ Stop)

================================================================
2) MIDDAY ROUTINE (laufender Betrieb)
================================================================
Ziel:
- Sicherstellen, dass L1 stabil weiterläuft
- Früherkennung schleichender Fehler

---------------------------------------------------------------
2.1 Prozess-Check
---------------------------------------------------------------
- Prozess läuft
- keine Hänger
- loop_delay regelmäßig

---------------------------------------------------------------
2.2 Logging-Kontinuität
---------------------------------------------------------------
- Logs wachsen weiter
- keine längeren Stillstände

---------------------------------------------------------------
2.3 Tick-Stichprobe (1–2 Ticks)
---------------------------------------------------------------
Prüfen:
- Soll-Sequenz vollständig
- max. ein Intent pro Tick
- Execution nur Stub
- state_update + state_persisted vorhanden

---------------------------------------------------------------
2.4 Kill-Level-Check
---------------------------------------------------------------
- Kill-Level = NONE oder erklärbar
- kein Flapping
- keine Rücksprünge

---------------------------------------------------------------
2.5 Entscheidung
---------------------------------------------------------------
[ ] GREEN → weiterlaufen
[ ] YELLOW → beobachten, dokumentieren
[ ] RED → sofort stoppen

================================================================
3) END-OF-DAY ROUTINE (Tagesabschluss)
================================================================
Ziel:
- sauberer Abschluss
- klare Ausgangslage für nächsten Tag

---------------------------------------------------------------
3.1 Abschlussentscheidung
---------------------------------------------------------------
Heute L1:
[ ] weiterlaufen lassen
[ ] kontrolliert stoppen

Wenn stoppen:
- manueller Stop
- system_stop prüfen

---------------------------------------------------------------
3.2 Abschluss-Logprüfung
---------------------------------------------------------------
- letzter Tick vollständig
- keine offenen Execution-Ereignisse
- kein halbfertiger State

---------------------------------------------------------------
3.3 State-Prüfung
---------------------------------------------------------------
- S2 = FLAT
- S4 konsistent
- State-Dateien append-only, intakt

---------------------------------------------------------------
3.4 Tageszusammenfassung (kurz)
---------------------------------------------------------------
Notieren (stichpunktartig):
- Datum
- system_state_id(s)
- Anzahl Starts / Stops
- besondere Beobachtungen
- Ampelstatus am Tagesende

Keine Interpretation.
Keine Bewertung.

---------------------------------------------------------------
3.5 Übergabefrage
---------------------------------------------------------------
Könnte ich morgen ohne Kontextverlust
mit L1 weiterarbeiten?

Wenn NEIN:
→ Notiz hinterlassen
→ L1 nicht automatisch starten

================================================================
4) Tagesampel (verbindlich)
================================================================
GREEN:
- keine Abweichungen
- vollständige Observability

YELLOW:
- erklärbare Warnungen
- keine Invarianten-Verletzung

RED:
- Log-Lücke
- State-Drift
- Kill-Level-Anomalie
- Zeit-/Persistenzfehler

Bei RED:
- L1 stoppen
- kein Restart ohne SOP

================================================================
5) Abschluss
================================================================
Diese Routine schützt L1 vor:
- schleichender Instabilität
- Operator-Fehlern
- unbewusstem Scope-Drift

Disziplin pro Tag
ist wichtiger als Fortschritt.

ENDE L1 TAGESROUTINE
