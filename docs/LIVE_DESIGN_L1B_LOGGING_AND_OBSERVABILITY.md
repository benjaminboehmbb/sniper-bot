# LIVE DESIGN — L1-B LOGGING & OBSERVABILITY
Projekt: Sniper-Bot
Datum: 2026-01-10
Status: VERBINDLICH (L1)

---

## Zweck dieses Dokuments

Dieses Dokument definiert die verbindlichen Anforderungen
an Logging und Observability für L1 (Paper Trading).

Ziel ist vollständige Nachvollziehbarkeit
jedes Systemverhaltens ohne Rückgriff auf GS-Ergebnisse.

---

## Grundsatz

Alles Relevante muss beobachtbar sein.
Nicht-Beobachtbares Verhalten ist ein Fehler.

Logs erklären Verhalten,
sie rechtfertigen es nicht.

---

## Logging-Prinzipien (verbindlich)

- strukturierte Logs (key=value)
- zeitlich monoton (UTC)
- deterministische Reihenfolge
- keine stillen Fehler
- kein Log-Level-Unterdrücken kritischer Events

Keine Logs mit:
- ROI
- Winrate
- Performance-Begriffen
- GS-Referenzen

---

## Log-Kategorien (Pflicht)

### L1 — Lifecycle
- Systemstart
- Konfigurationsladung
- Systemstop
- manueller Stop
- Restart

---

### L2 — Market & Data
- Snapshot empfangen
- data_valid true/false
- Zeitstempel-Abweichungen
- fehlende Daten

---

### L3 — Policy & Intent
- Intent erzeugt (BUY/SELL/HOLD/CLOSE)
- Intent verworfen (inkl. Grund)
- Intent-ID & Timestamp

Keine Logikbewertung, nur Feststellung.

---

### L4 — Guards & Risk
- Guard ausgelöst (Typ, Ursache)
- Kill-Level-Wechsel
- Cooldown-Start/-Ende
- Limit-Überschreitung

---

### L5 — Execution
- Order gesendet
- Order blockiert
- Execution-Response
- Reject / Timeout

Keine Retry-Logs.

---

### L6 — State
- State-Update (S2, S4)
- Persistenz erfolgreich / fehlgeschlagen
- Restart-State geladen

---

### L7 — Health
- Heartbeat OK / FAIL
- Resource-Warnung
- Clock Drift erkannt
- Prozess-Exit

---

## Pflichtfelder je Log-Eintrag

- timestamp_utc
- category
- event
- severity
- system_state_id
- intent_id (falls vorhanden)

---

## Observability-Anforderungen

### Nachvollziehbarkeit
- jede Order ist auf einen Intent zurückführbar
- jeder Intent ist auf einen Market Snapshot zurückführbar
- jede Blockierung ist begründet

### Rekonstruierbarkeit
- kompletter Ablauf eines Decision-Ticks rekonstruierbar
- Reihenfolge eindeutig
- keine impliziten Übergänge

---

## Verbotene Praktiken

- Silent Fail
- zusammengefasste Multi-Events
- Log-Mutation im Nachhinein
- Log-Filterung während des Betriebs
- „Debug-Only“-Pfad ohne Logs

---

## Aufbewahrung & Zugriff

- Logs append-only
- kein automatisches Löschen
- Zugriff read-only während Betrieb
- Auswertung nur offline

---

## Erfolgskriterium (L1-B)

L1-B gilt als erfüllt, wenn:
- ein kompletter Trading-Tag vollständig erklärbar ist
- jede Entscheidung ohne GS erklärbar ist
- kein kritisches Ereignis ungeloggt bleibt

---

## Zentrale Invariante

Wenn eine Frage zum Systemverhalten
nicht ausschließlich mit Logs beantwortet werden kann,
ist die Observability unzureichend.

---

## Abschluss

Logging ist kein Hilfsmittel,
sondern ein Sicherheitsmechanismus.

Ohne vollständige Observability
darf L1 nicht fortgesetzt werden.
