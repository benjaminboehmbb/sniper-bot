# LONG FINAL — Gold-Standard (Frozen) am 09012026

## Inhalt
Autoritative Auswahl von **250 LONG-Strategien** aus dem abgeschlossenen
**K12 LONG FULL** Lauf. Diese Datei ist **eingefroren** und darf nicht
nachträglich verändert werden.

---

## Quelle
- Input: `results/GS/k12_long/strategy_results_GS_k12_long_FULL_2026-01-09_15-46-13.csv`
- Final Output: `strategies_GS_k12_long_TOP250_FINAL_2026-01-09_16-01-51.csv`

---

## Selektionskriterium (verbindlich)
- **Robustheitsmaß:** `roi_fee_p25` (25%-Quantil über Offsets)
- **Gate:** `roi_fee_p25 >= -3.1788`
- **Ranking:**  
  1) `roi_fee_p25` (desc)  
  2) `roi_fee_mean` (desc)

Zielgröße: **Top-250** (kein Informationsverlust, gate-kalibriert).

---

## Evaluations-Setup (fix)
- **Instrument:** BTCUSDT
- **Zeiteinheit:** 1 Minute
- **Zeitraum:** 2017–2025
- **Fenstergröße:** 200,000 Rows
- **Offsets:** 0, 500,000, 1,000,000, 1,500,000
- **Fee (roundtrip):** 0.0004
- **Engine:** `engine/simtraderGS.py`
- **Regime-Gate:** aktiv (asymmetrisch)

---

## Interpretation
- Negative `roi_fee_mean` ist **erwartbar** bei K12 unter strengen
  Robustheits-Gates und Gebühren.
- Die Entscheidungsgröße ist **Stabilität über Offsets** (`roi_fee_p25`),
  nicht der Einzel-ROI.
- Das Set zeigt **keine Degeneration** (Trade-Last im engen Band,
  keine Ausreißer).

---

## Status
**FROZEN — DO NOT MODIFY**

Änderungen, Nachselektionen oder Neu-Gates sind unzulässig.
Dieses Set dient als **LONG-Fundament** für alle weiteren Projektphasen.
