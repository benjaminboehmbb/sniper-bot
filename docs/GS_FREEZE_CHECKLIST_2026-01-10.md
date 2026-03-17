# GS Freeze-Checkliste — Sniper-Bot (simtraderGS)
Datum: 2026-01-10  
Status: CHECKLISTE (verbindlich vor jedem Weitergehen)

---

## Zweck
Diese Checkliste stellt sicher, dass der Gold-Standard-Fundamentstand:
- unveraendert,
- reproduzierbar,
- versioniert,
- und vor versehentlichem Ueberschreiben geschuetzt ist,

**bevor** weitere Analysen oder Strukturarbeiten erfolgen.

---

## A) Code-Integritaet (Engine)

- [ ] `engine/simtraderGS.py` existiert **einmalig** im Repo.
- [ ] Keine zweite `simtrader*.py` mit GS-Logik an anderem Ort.
- [ ] `evaluate_strategy(price_df, comb, direction)` ist die **einzige** Entry-Signatur.
- [ ] Keine Parameter-Leichen (`offset`, `rows`, `fee`) in der Signatur.
- [ ] Determinismus verifiziert (identische Inputs → identische Outputs).

**Gate A bestanden:** ☐

---

## B) Daten-Integritaet

- [ ] Preis-CSV existiert exakt unter:
  - `data/btcusdt_1m_2026-01-07/simtraderGS/`
- [ ] Dateiname exakt:
  - `btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv`
- [ ] Datei wird **nirgendwo** im Projekt dupliziert.
- [ ] Keine temporären oder alternativen Preis-CSVs aktiv.

**Gate B bestanden:** ☐

---

## C) FINAL-Artefakte (Write-Protect logisch)

### C1) Strategien
- [ ] `strategies/GS/LONG_FINAL_CANONICAL/` nur **eine** CSV (N=1).
- [ ] `strategies/GS/SHORT_FINAL/` nur **eine** CSV (N=1).
- [ ] Keine Skripte schreiben in diese Ordner.
- [ ] Keine Umbenennungen oder Re-Saves erfolgt.

### C2) Ergebnisse
- [ ] `results/GS/k12_long/` enthaelt **nur** `*_FULL_CANONICAL_*.csv`.
- [ ] `results/GS/k12_short/` enthaelt **nur** `*_FULL_CANONICAL_*.csv`.
- [ ] `results/GS/meta/` enthaelt nur Meta-Reports (CSV + MD).

**Gate C bestanden:** ☐

---

## D) Struktur & Naming

- [ ] Aktive Ordner sind minimal:
  - `engine/`, `data/`, `strategies/GS/`, `results/GS/`, `tools/`, `scripts/`
- [ ] Alle anderen Artefakte liegen unter `archive/GS_2026-01-10/`.
- [ ] Keine Skript-Namen mit `_v2`, `_new`, `_test`, `_final`.
- [ ] Ergebnisdateien tragen Zeitstempel im Namen.

**Gate D bestanden:** ☐

---

## E) Git-Status (verbindlich)

- [ ] `git status` zeigt **keine** ungeplanten Aenderungen.
- [ ] Archiv-Verschiebungen sind committed.
- [ ] Snapshot-Docs sind committed.
- [ ] Commit-Message klar (z. B. `GS freeze: canonical finals + meta + archive`).

**Gate E bestanden:** ☐

---

## F) Environment-Sicherheit

- [ ] Alle Analysen liefen in **WSL**.
- [ ] Kein Run in Git Bash / Windows-Python.
- [ ] Keine parallelen Deep-Runs aktiv.
- [ ] Aktives Geraet (G15 / Workstation) bewusst gesetzt.

**Gate F bestanden:** ☐

---

## G) Wiederherstellbarkeit (Smoke)

- [ ] Repo frisch geklont → `simtraderGS` importierbar.
- [ ] Preis-CSV ladbar.
- [ ] `build_GS_k12_long_FINAL_CANONICAL.py` **nicht** mehr benoetigt fuer Repro.
- [ ] Meta-Report lesbar ohne Re-Run.

**Gate G bestanden:** ☐

---

## Abschluss

- [ ] Alle Gates A–G bestanden.
- [ ] Gold-Standard-Fundament gilt als **eingefroren**.
- [ ] Weiterarbeit erfolgt **nur read-only** oder nach expliziter Entfrierung.

**Freeze bestaetigt am:** ____________  
**Bestaetigt von:** __________________

---

## Naechster Schritt (nach bestandenem Freeze)

**Schritt 4: Regime-Analyse-Vertiefung (read-only)**  
- Keine neuen Runs.
- Nur Auswertung vorhandener Canonical-Results.
- Ziel: Verstehen, **wann** LONG vs SHORT strukturell traegt.
