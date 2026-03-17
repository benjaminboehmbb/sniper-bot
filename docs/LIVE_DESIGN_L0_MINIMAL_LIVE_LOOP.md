# LIVE DESIGN — L0 MINIMAL LIVE LOOP
Projekt: Sniper-Bot  
Datum: 2026-01-10  
Status: VERBINDLICH (L0)

---

## Zweck dieses Dokuments

Dieses Dokument definiert den minimalen, zulässigen Ablauf eines Live-Systems
auf Basis des validierten GS-Fundaments.

Der Loop beschreibt **nur den Ablauf**, keine Implementierung,
keine Optimierung und keine Simulation.

---

## Grundsatz

Der Live-Loop ist:
- deterministisch im Ablauf
- defensiv im Verhalten
- jederzeit unterbrechbar
- vollständig guard-gesteuert

Kein Schritt darf implizit übersprungen werden.

---

## Minimaler Live-Loop (verbindliche Reihenfolge)

### Schritt 1 — Systemstart

- Lade Konfiguration
- Initialisiere State (S2, S4)
- Setze Kill-Level = NONE
- Warte auf ersten validen Market Snapshot

Kein Trading vor Abschluss dieses Schritts.

---

### Schritt 2 — Market Snapshot erfassen (S1)

- Empfange Marktpreis
- Empfange Signale
- Validiere Datenintegrität
- Setze data_valid Flag

Bei data_valid == false → zurück zu Schritt 2

---

### Schritt 3 — Policy Evaluation (L1)

- Lies aktuellen State
- Bewerte Regeln
- Erzeuge maximal einen Intent (S3)

Keine Order-Erzeugung in diesem Schritt.

---

### Schritt 4 — Guard & Risk Check (L2)

- Prüfe Kill-Level
- Prüfe Limits
- Prüfe Cooldowns
- Prüfe Anomalien

Bei Verstoß → Kill-Level erhöhen, Intent verwerfen

---

### Schritt 5 — Execution Attempt (L3)

- Übersetze Intent → Order
- Sende Order
- Warte auf Response

Keine Retry-Logik.

---

### Schritt 6 — State Update

- Aktualisiere Position State (S2)
- Aktualisiere Risk State (S4)
- Aktualisiere Health State (S5)

State-Updates sind atomar.

---

### Schritt 7 — Persistenz

- Persistiere S2 (Position)
- Persistiere S4 (Risk)
- Keine Persistenz anderer States

---

### Schritt 8 — Loop Delay

- Warte bis nächster Decision-Tick
- Kein Busy-Wait
- Kein Zeit-Sprung

---

## Abbruchbedingungen

Der Loop endet sofort bei:
- Kill-Level == HARD
- Kill-Level == EMERGENCY
- System Health Fehler
- explizitem manuellen Stop

Kein automatischer Neustart.

---

## Verbotene Abkürzungen

- Überspringen von Guard-Checks
- Zusammenfassen von Schritten
- Implizite Retries
- State-Mutation außerhalb des Loops
- GS-Aufrufe im Loop

---

## Zentrale Invariante

Jede Order muss erklärbar sein
durch eine Sequenz aus:

Market Snapshot → Intent → Guard Check → Execution → State Update

Alles andere ist ein Designfehler.

---

## Abschluss

Mit diesem Loop ist definiert:
- wann Entscheidungen entstehen
- wann Orders erlaubt sind
- wann das System stoppt

Der Loop ist minimal, defensiv
und schützt das GS-Fundament vollständig.
