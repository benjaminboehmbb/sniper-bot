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
(… wie bisher …)

---

### 📂 Beispiel Ergebnisordner `deep_out_7A`
(… wie bisher …)

---

### 📂 Systemordner
- **.venv** – Virtuelle Python-Umgebung.  
- **__pycache__** – Automatischer Python-Cache.  

---

## 🔹 Best-Practice Routine (Backup & Checks)

Um Datenverlust und Fehler zu vermeiden, **immer folgende Schritte** durchführen:

1. **Vor jedem großen Skript-Run (Deep-Dive, 2er–7er, ML-Export):**
   - `python check_csv_structure.py` ausführen → prüft alle CSVs.  
   - Bei **CRITICAL/WARN** sofort handeln.

2. **Danach Backup erstellen:**
   ```bash
   python backup_project.py --dest "D:\sniper-bot-backups"
