# Deep-Dive (Long) – Auswertungs-Checkliste
Stand: 2025-09-03

Ziel: **sehr viele Kandidaten behalten** (Start z. B. Top **5 000**) und dann **in klaren, reproduzierbaren Stufen** filtern – mit maximaler Transparenz.  
Rechenintensive Schritte sind als **[Workstation]** markiert.

---

## 0) Grundsätze & Hygiene

1. **Nichts überschreiben.** Alle Ergebnisse in neue, datierte Ordner schreiben:
   - `results/reports/<YYYY-MM-DD_HH-MM-SS>/...`
2. **Backups & Versionierung (immer):**
   - Nach jedem erfolgreichen Run: `python backup_project.py --dest "<Backup-Pfad>"`
   - Danach commit & push (Git).
3. **Benennungskonvention (Beispiel):**
   - `strategy_results_7er_<RUNID>.csv`
   - `report_stage1_top5000_7er_<RUNID>.csv`
   - `trade_history_<STRATID>_<RUNID>.csv`

---

## 1) Datengrundlage

- Primärdatei: **`strategy_results.csv`** (Spalten: `idx, Combination, roi, num_trades, winrate`)
- Optional vorhanden:
  - `metrics*.csv` (aggregierte Kennzahlen)
  - `combined_*.csv` (aufbereitete Ergebnisse, ggf. mit Zeitbezug)
  - `errors*.csv` (Fehlerprotokolle)
- Speicherort (Beispiele):
  - `deep_out_7A/` oder `analysis_output_7er/<RUNID>/`  
  - **Backups:** `out_7er_fast_full_fine_A_backup/`, `..._B_backup/`

Vor jedem Schritt: **CSV-Check**  
```bash
python check_csv_structure.py
