# Sniper-Bot Projektstruktur
Stand: 2025-09-02

---

## 🔹 Hauptverzeichnis `sniper-bot`

### 📄 Hauptskripte
- **deep_dive_analysis_mp_resume.py**  
  Multiprocessing Deep-Dive-Skript, fortsetzbar.
- **deep_dive_analysis_mp_resume1.py**  
  Alternative Resume-Version.
- **deep_dive_analysis.py**  
  Ursprungsversion Deep-Dive.
- **recompute_strategy_metrics.py**  
  Berechnet Strategiekennzahlen neu (ROI, Winrate, etc.).
- **fix_combined_for_deepdive.py**  
  Repariert kombinierte CSV-Dateien für Deep-Dive.
- **preclean_combined.py**  
  Vorverarbeitung kombinierter Ergebnisse.
- **postprocess_results.py**  
  Auswertung & Nachbearbeitung von Ergebnissen.
- **plot_performance.py**  
  Erstellung von Performance-Diagrammen.
- **simtrader.py / simtrader_fast.py**  
  Simulationsengine (Standard- und Schnell-Version).
- **analyze_unified.py**  
  Einheitliches Skript für 2er–7er Analysen mit automatischem Backup, Logging, Zeitstempeln.
- **start_env**  
  Skript für Python-Umgebungsstart.

---

### 📄 Hauptdaten
- **price_data_with_signals.xlsx / .csv**  
  Historische Kursdaten BTC/USDT (5-Minuten) mit allen Signalen.

---

### 📂 Ergebnisordner
- **deep_out_7A**  
  Deep-Dive-Ergebnisse (7er, optimiert, Backups).
- **deep_out_ALL**  
  Komplette Deep-Dive-Ergebnisse.
- **summary_out**  
  Zusammenfassungen von Analyseergebnissen.
- **analysis_output_Xer**  
  Standard-Ausgabeordner für Analysen mit `analyze_unified.py`.

---

### 📂 Clean-Ordner
#### 🔸 `2er_clean`
- **strategies_2er_all.csv** – Alle 2er-Kombinationen.
- Ergebnisordner: `analysis_output_2er/`

#### 🔸 `3er_clean`
- **strategies_3er_full.csv** – Vollständige 3er-Kombinationen.
- Ergebnisordner: `analysis_output_3er/`

#### 🔸 `4er_clean`
- **strategies_4er_fine.csv** – Feinkombinationen 4er.
- Ergebnisordner: `analysis_output_4er/`

#### 🔸 `5er_clean`
- **strategies_5er_fine.csv** – Feinkombinationen 5er.
- Ergebnisordner: `analysis_output_5er/`

#### 🔸 `6er_clean`
- **strategies_6er_fine.csv** – Feinkombinationen 6er.
- Ergebnisordner: `analysis_output_6er/`

#### 🔸 `7er_clean`
- **strategies_7er_finetune_A.csv** – Fine-Tuning A.
- **strategies_7er_finetune_B.csv** – Fine-Tuning B.
- Ergebnisordner: `analysis_output_7er/`

---

### 📂 Beispiel Ergebnisordner `deep_out_7A`
- **combined_clean.csv** – Vorverarbeitete kombinierte Ergebnisse.  
- **combined_fixed.csv** – Gefixte Datei für Deep-Dive.  
- **combined_recomputed.csv** – Neu berechnete Ergebnisse.  
- **metrics.csv** – Berechnete Kennzahlen.  
- **metrics_backup_*.csv** – Backups.  
- **strategy_results.csv** – Hauptresultate.  
- **strategy_results_backup_*.csv** – Backups der Hauptresultate.  
- **errors_backup_*.csv** – Fehlerlogs.

---

### 📂 Systemordner
- **.venv** – Virtuelle Python-Umgebung.  
- **__pycache__** – Automatischer Python-Cache.  
- **.gitignore** – Ignoriert Analyse-Outputs und große Dateien.

---

## 🔹 Best-Practice Routine (Backup & Checks)

Um Datenverlust und Fehler zu vermeiden, **immer folgende Schritte** durchführen:

1. **Vor jedem großen Skript-Run (Deep-Dive, 2er–7er, ML-Export):**
   - `python check_csv_structure.py` ausführen → prüft alle CSVs.  
   - Bei **CRITICAL/WARN** sofort handeln.

2. **Danach Backup erstellen:**
   ```bash
   python backup_project.py --dest "D:\sniper-bot-backups"

