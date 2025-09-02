
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
- **start_env**  
  Skript für Python-Umgebungsstart.

---

### 📄 Hauptdaten
- **price_data_with_signals.xlsx**  
  Historische Kursdaten BTC/USDT (5-Minuten) mit allen Signalen.

---

### 📂 Ergebnisordner
- **deep_out_7A**  
  Deep-Dive-Ergebnisse (7er, optimiert, Backups).
- **deep_out_ALL**  
  Komplette Deep-Dive-Ergebnisse.
- **summary_out**  
  Zusammenfassungen von Analyseergebnissen.
- **out_Xer_fast_full / out_Xer_full / out_Xer_fast_bench**  
  Verschiedene Lauf- und Benchmark-Ergebnisse (Xer-Strategien).

---

### 📂 Clean-Ordner
#### 🔸 `2er_clean`
- **analyze_strategies_2er_v2.py** – Analyse 2er-Kombinationen.  
- **price_data_with_signals.csv** – Kursdaten für 2er-Analyse.  
- **simtrader.py** – Simulationsengine.  
- **strategies_2er_all.csv** – Alle 2er-Kombinationen.  
- **analysis_output_2er** – Ergebnisordner für 2er.

#### 🔸 `3er_clean`
- **analyze_strategies_3er.py** – Analyse 3er-Kombinationen.  
- **generate_strategies_3er.py** – CSV-Generator für 3er-Strategien.  
- **strategies_3er_full.csv** – Vollständige 3er-Kombis.  
- **strategy_analysis_output_3er** – Ergebnisse.

#### 🔸 `4er_clean`
- **analyze_strategies_4er_mp_v2.py** – Multiprocessing-Analyse 4er.  
- **analyze_strategies_4er_sequential.py** – Sequentielle 4er-Analyse.  
- **strategies_4er_10k.csv** – Test-Subset 10k Strategien.  
- **strategies_4er_fine.csv** – Feinkombis für 4er.

#### 🔸 `5er_clean`
- **analyze_strategies_5er_mp_v2.py** – Multiprocessing-Analyse 5er.  
- **generate_strategies_5er_fine.py** – Generator für Feinkombis.  
- **strategies_5er_10k.csv** – 10k Teststrategie-Subset.  
- **strategies_5er_fine.csv** – Feinkombis für 5er.

#### 🔸 `6er_clean`
- **analyze_strategies_6er_mp_v2.py** – Multiprocessing-Analyse 6er.  
- **generate_strategies_6er_fine.py** – Generator für Feinkombis.  
- **strategies_6er_10k.csv** – 10k Teststrategie-Subset.  
- **strategies_6er_fine.csv** – Feinkombis für 6er.

#### 🔸 `7er_clean`
- **analyze_strategies_7er_mp_v2.py** – Multiprocessing 7er-Analyse.  
- **analyze_strategies_restartable_mp_v2.py** – Neustartbare Version.  
- **generate_strategies_7er_finetune_from_top.py** – Generator für Fine-Tuning Top-Strategien.  
- **generate_strategies_7er_coarse.py** – Grobkombinationen.  
- **strategies_7er_10k.csv** – 10k Subset.  
- **strategies_7er_coarse.csv** – Grobkombis.  
- **strategies_7er_finetune_A/B.csv** – Feintuning-Kombis A & B.

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
