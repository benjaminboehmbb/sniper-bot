LIVE_DESIGN_L1_FREEZE_AND_OPERATIONAL_GUARD

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: verbindlich
Zweck: Absicherung von Betrieb & Scope

================================================================
0) Ziel dieses Dokuments
================================================================
Dieses Dokument sichert L1 gegen unbeabsichtigte
Scope-Erweiterung, Design-Drift und operative Fehlgriffe ab.

Es erlaubt aktives Arbeiten,
ohne L1 zu verletzen.

================================================================
1) Verbindlicher Freeze-Status
================================================================
Die folgenden Dokumente sind READ-ONLY:

- LIVE_DESIGN_L1B_OPERATIONAL_CHECKLIST.md
- LIVE_DESIGN_L1D_RESTART_AND_RECOVERY_SOP.md
- LIVE_DESIGN_L1_CONTINUOUS_OPERATION_MONITORING_CHECKLIST.md
- LIVE_DESIGN_L1_EXIT_AND_REVIEW_PROTOCOL.md

Änderungen sind verboten.
Abweichungen erfordern neues Mandat.

================================================================
2) Erlaubte Tätigkeiten (AKTIV)
================================================================
In L1 ausdrücklich erlaubt:

- Betrieb von L1 Paper Trading
- Log-Analyse
- Abgleich mit Checklisten
- Restart gemäß L1-D SOP
- Dokumentation von Beobachtungen
- Klassifikation von Fehlern (ohne Fix)

================================================================
3) Verbotene Tätigkeiten (HART)
================================================================
In L1 ausdrücklich verboten:

- Code-Änderungen
- Guard-Änderungen
- Policy-Erweiterungen
- Performance-Auswertung
- GS-Vergleiche
- „Nur kurz testen“-Aktionen
- implizite Übergänge zu L2

================================================================
4) Arbeitsmodus-Regel (Operator-Regel)
================================================================
Während L1 gilt:

BEOBACHTEN > DOKUMENTIEREN > STOPPEN

EINGREIFEN nur bei:
- RED-Ereignis
- Invarianten-Verletzung
- Observability-Lücke

================================================================
5) Stopp-Regel (Selbstschutz)
================================================================
Wenn Unsicherheit entsteht, gilt:

- KEINE Interpretation
- KEIN Fix
- KEINE Erweiterung

→ Betrieb stoppen
→ Beobachtung dokumentieren
→ später analysieren

================================================================
6) Tagesstart-Frage (Pflicht)
================================================================
Vor jeder Arbeit an L1 beantworte ich:

- Arbeite ich am BETRIEB oder am DESIGN?
- Ist das, was ich tun will, explizit erlaubt?

Wenn nicht eindeutig:
→ nicht tun.

================================================================
7) Übergangsregel
================================================================
Ein Übergang zu L2 ist nur erlaubt bei:

- abgeschlossenem L1 Exit & Review
- dokumentierter Freigabe
- explizitem L2-Mandat

Alles andere ist Scope-Verletzung.

================================================================
8) Abschluss
================================================================
Dieses Dokument schützt L1 vor mir selbst.

Stabilität schlägt Fortschritt.
Disziplin schlägt Tempo.

ENDE L1 FREEZE & OPERATIONAL GUARD
