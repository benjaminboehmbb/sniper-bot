LIVE_DESIGN_L1_EXIT_AND_REVIEW_PROTOCOL

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: verbindlich
Scope: Exit & Review
Kein Code, keine Optimierung, keine Performance-Kennzahlen

================================================================
0) Zweck & Grundsatz
================================================================
Dieses Dokument definiert den verbindlichen Ablauf
zum Beenden von L1 (Paper Trading) sowie die formale
Review- und Freigabeentscheidung.

Ziel:
- kontrollierter Abschluss von L1
- objektive Betriebsbewertung
- Vermeidung impliziter Übergänge
- saubere Entscheidungsgrundlage für nächste Phasen

================================================================
1) Zulässige Exit-Trigger
================================================================
Ein L1-Exit ist NUR zulässig bei:

- geplantem Session-Ende
- erfolgreichem Dauerlauf über definierten Zeitraum
- wiederholten L1-B / L1-D Verstößen
- externer Notwendigkeit (System, Wartung)

Nicht zulässig:
- Exit zur Performance-Bewertung
- Exit zur Strategie-Optimierung
- Exit zur Vorbereitung von L2 ohne Review

================================================================
2) Exit-Ablauf (verbindlich)
================================================================
2.1 Kontrollierter Stopp
- Prozess manuell beenden
- kein paralleler Neustart

2.2 Abschluss-Logs prüfen
- system_stop vorhanden
- letzter Tick vollständig
- keine offenen Execution-Ereignisse

2.3 Freeze des Betriebs
- keine weiteren Starts von L1
- Logs & State-Dateien read-only behandeln

================================================================
3) Review-Vorbereitung
================================================================
Für das Review heranziehen:

- vollständige L1-Logs des Zeitraums
- Restart-Historie (system_start / system_stop)
- State-Dateien S2 und S4
- Notizen aus Dauerlauf-Überwachung

Keine anderen Daten zulässig.

================================================================
4) Review-Checkliste (Pflicht)
================================================================

4.1 Observability
- jeder Tick rekonstruierbar
- keine Log-Lücken
- alle Pflichtfelder vorhanden

4.2 Loop-Integrität
- Soll-Sequenz pro Tick eingehalten
- keine impliziten Übergänge
- kein Schritt übersprungen

4.3 State-Invarianten
- S2 immer FLAT
- S4 Kill-Level monoton
- keine State-Leaks über Runs

4.4 Restart-Verhalten
- jeder Restart erklärbar
- neue system_state_id pro Run
- Restart-Smoke-Test bestanden

4.5 Persistenz
- append-only eingehalten
- keine Überschreibungen
- keine kaputten JSONL-Zeilen

================================================================
5) Review-Ergebnis (formale Entscheidung)
================================================================
Nach Abschluss des Reviews MUSS genau eine
der folgenden Entscheidungen getroffen werden:

[ ] L1 FREIGEGEBEN
    - Betrieb war stabil
    - keine strukturellen Defekte
    - Übergang zu L2 DARF beantragt werden

[ ] L1 HALTEN
    - kleinere Defekte
    - erneuter L1-Betrieb erforderlich
    - kein Übergang zu L2

[ ] L1 GESTOPPT
    - strukturelle Fehler
    - L1 nicht fortsetzbar
    - Analyse außerhalb des Betriebs notwendig

================================================================
6) Dokumentationspflicht
================================================================
Das Review MUSS dokumentiert enthalten:

- Zeitraum des L1-Betriebs
- Anzahl der Runs
- Anzahl der Restarts
- festgestellte Abweichungen
- finale Entscheidung (Freigabe / Halten / Stop)

Keine Performance-Daten aufnehmen.

================================================================
7) Übergangsregeln
================================================================
- Ohne dokumentierte Freigabe KEIN Übergang zu L2
- L2 erfordert separates Mandat
- L1-Dokumente bleiben unverändert (Freeze)

================================================================
8) Definition erfolgreicher L1-Abschluss
================================================================
L1 gilt als erfolgreich abgeschlossen, wenn:

- Betrieb vollständig erklärbar war
- keine kritischen Invarianten verletzt wurden
- Review formal dokumentiert ist
- klare Entscheidung getroffen wurde

ENDE L1 EXIT & REVIEW PROTOKOLL
