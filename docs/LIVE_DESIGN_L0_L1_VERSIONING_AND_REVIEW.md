# LIVE DESIGN — L0/L1 VERSIONING & REVIEW
Projekt: Sniper-Bot
Datum: 2026-01-10
Status: VERBINDLICH — ABSCHLUSS L0/L1

---

## Zweck dieses Dokuments

Dieses Dokument schließt die Phasen
- Live-Design L0
- Paper-Trading-Design L1

formal ab.

Es definiert:
- Review-Vorgehen
- Versionierungsregeln
- Änderungsverbote
- Freigabezustand

Nach diesem Dokument gelten L0 und L1 als
architektonisch eingefroren.

---

## Dokumentenumfang (verbindlich)

### L0 — Live-Design
- LIVE_DESIGN_L0_ARCHITECTURE.md
- LIVE_DESIGN_L0_FAILURE_MODES.md
- LIVE_DESIGN_L0_STATE_MODEL.md
- LIVE_DESIGN_L0_SIMULATION_VS_LIVE_PARITY.md
- LIVE_DESIGN_L0_MINIMAL_LIVE_LOOP.md
- LIVE_DESIGN_L0_PAPER_TRADING_BOUNDARY.md

### L1 — Paper Trading Design
- LIVE_DESIGN_L1_PAPER_TRADING_OVERVIEW.md
- LIVE_DESIGN_L1A_OPERATIONAL_GOALS_AND_METRICS.md
- LIVE_DESIGN_L1B_LOGGING_AND_OBSERVABILITY.md
- LIVE_DESIGN_L1C_GUARD_AND_KILLSWITCH_RULES.md
- LIVE_DESIGN_L1D_RESTART_AND_RECOVERY_PROTOCOL.md
- LIVE_DESIGN_L1E_PAPER_TRADING_EXIT_AND_REVIEW.md

---

## Review-Checkliste (Pflicht)

Jedes Dokument MUSS geprüft sein auf:

### Architektur
- keine Vermischung mit GS/Post-GS
- klare Systemgrenzen
- keine impliziten Übergänge

### Sicherheit
- Guards deterministisch
- Kill-Switches monoton
- kein Auto-Recovery

### State
- minimal
- invariant
- keine Performance-Daten

### Betrieb
- vollständige Observability
- erklärbarer Ablauf
- manuelle Kontrollierbarkeit

Wenn ein Punkt nicht erfüllt ist,
ist das Dokument nicht freigegeben.

---

## Review-Ergebnis

Nach erfolgreichem Review gilt:

- L0 = ARCHITEKTUR-FREEZE
- L1 = DESIGN-FREEZE

Alle Inhalte gelten als verbindliche Referenz.

---

## Versionierungsregeln (streng)

- Dokumente erhalten KEINE stillen Änderungen
- jede Änderung erfordert:
  - neues Dokument ODER
  - explizite neue Phase
- keine Inline-Korrekturen
- keine „kleinen Anpassungen“

---

## Änderungsverbote

Nach Freigabe ist verboten:

- semantische Änderung bestehender Regeln
- Abschwächung von Guards
- Erweiterung von Live-Rechten
- implizite Optimierung
- Performance-basierte Argumentation

---

## Freigabeerklärung

Mit diesem Dokument gilt:

- Live-Design L0 abgeschlossen
- Paper-Trading-Design L1 abgeschlossen
- System bereit für kontrollierten Start von L1

Ein Übergang zu L2 oder Exploration
erfordert ein neues, explizites Mandat.

---

## Zentrale Invariante

Wenn später Unsicherheit entsteht,
gilt immer dieses Dokument
als letzte verbindliche Referenz.

---

## Abschluss

Dieses Dokument markiert
den strukturellen Abschluss
der Design-Phase vor Betrieb.

Ab hier beginnt Umsetzung,
nicht Diskussion.
