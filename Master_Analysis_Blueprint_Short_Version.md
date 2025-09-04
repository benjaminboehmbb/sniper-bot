# Master Analysis Blueprint

## 1. Einleitung & Zielsetzung

Dieses Dokument ist die **zentrale Blaupause** für alle Analyse- und Evaluationsschritte im Sniper-Bot Projekt.  
Es definiert die **Methodik, Prinzipien und Erweiterungen**, die sicherstellen, dass jede getestete Strategie nachvollziehbar, versioniert und reproduzierbar bleibt.  

### Warum?
- **Hohe Selektivität & Präzision:** Der Bot soll nur wenige, aber besonders renditestarke Trades ausführen („Sniper-Prinzip“).  
- **Robustheit & Langlebigkeit:** Strategien sollen nicht nur in der Vergangenheit funktionieren, sondern auch in verschiedenen Marktphasen stabil bleiben.  
- **Vorbereitung für Machine Learning:** Alle Ergebnisse werden so strukturiert, dass später Feature-Engineering und Modell-Training direkt möglich sind.  
- **Kapitalmanagement:** Durch Marktregime- und Volumenanalysen soll das eingesetzte Kapital dynamisch gesteuert werden.  

### Baukasten-Prinzip
Der Sniper-Bot ist bewusst als **modulares Baukastensystem** aufgebaut:  
- **Indikatoren-Module** (z. B. RSI, MACD, Bollinger, Volumen-Features) können einzeln oder in Kombination getestet werden.  
- **Regime-Module** (Bull/Bear/Seitwärts, Volatilität) bestimmen, wie Strategien auf die Marktlage reagieren.  
- **Strategie-Module** (2er–7er Kombinationen, Gewichtungen) bilden flexible Bausteine, die beliebig erweiterbar sind.  
- **Output-Module** (Trade-Historien, Kapitalverläufe, Kennzahlen) liefern Daten für Auswertungen und ML-Training.  

Alle Module sind **austauschbar, kombinierbar und erweiterbar**. Dadurch ist es jederzeit möglich:  
- neue Elemente zu **integrieren**,  
- alte Elemente zu **entfernen oder zu deaktivieren**,  
- bestehende Elemente zu **re-konfigurieren**.  

Dies erlaubt eine **kontinuierliche Weiterentwicklung**, ohne das System neu aufbauen zu müssen.  

### Endziel
Ein **vollständig adaptiver Trading-Bot**, der:  
1. Auf Basis historischer Daten optimiert wurde.  
2. Laufend neu trainiert und getestet wird (Walk-Forward).  
3. Kapital dynamisch auf Long- und Short-Strategien verteilt (abhängig von Marktregime).  
4. In Echtzeit robuste Entscheidungen trifft.  

### Vorgehensweise
- **Iterativ:** Alle Erweiterungen werden Schritt für Schritt dokumentiert und getestet.  
- **Modular:** Indikatoren, Strategien, Regime-Labels und Volumen-Features werden einzeln kombiniert und später als Ganzes ausgewertet.  
- **Versioniert:** Jede Änderung wird per Git getrackt; Ergebnisse werden mit Zeitstempel gesichert.  
- **Langfristig:** Rechenintensive Analysen (lokal oder auf Vast.ai/Workstation) sind eingeplant und akzeptiert, um eine maximale Ergebnisqualität zu erreichen.  

---

## 2. Grundprinzipien

### 2.1 Selektivität
- Der Bot soll im Schnitt nur **~200 Trades pro Jahr (±100)** ausführen.  
- Selektivität wird durch **Filterlogik** erreicht (z. B. RSI, MACD, Bollinger, Marktregime).  
- Ziel: **Qualität vor Quantität** – wenige, aber renditestarke Signale.  
- Strategien mit zu vielen Trades (Overtrading) werden systematisch aussortiert.  

### 2.2 Backups & Versionierung
- **Automatische Backups**:  
  - Vor jedem neuen Skriptlauf prüft das System, ob eine `strategy_results.csv` existiert.  
  - Falls ja → wird automatisch mit Zeitstempel gesichert (z. B. `strategy_results_backup_2025-09-04_11-35.csv`).  
- **GitHub-Versionierung:**  
  - Alle Skripte und wichtigen Ergebnisdateien werden regelmäßig committet und gepusht.  
  - Branches können für große Experimente genutzt werden (z. B. `deep-dive`, `multi-coin`).  
- **Ordnerstruktur:**  
  - Jede Analyse (2er, 3er, 4er …) hat einen eigenen Ordner.  
  - Ergebnisse, Logs und Plots liegen klar getrennt.  
  - Keine Überschreibung ohne Backup.  

### 2.3 Reproduzierbarkeit
- Alle Skripte laufen mit **fixierten Parametern** (z. B. Fees, Slippage, Seeds für Randomness).  
- Jede Analyse ist später **1:1 nachvollziehbar**.  
- **Parameter-Logs:** Jedes Skript speichert seine Laufparameter in einer `run_config.json`.  

### 2.4 Langläufe akzeptieren
- Analysen sind bewusst **rechenintensiv** (mehrere Tage bis Wochen).  
- Strategie: **lange Läufe statt Schnelltests**, um **vollständige, robuste Ergebnisse** zu erhalten.  
- Workstation (Ryzen 9950X3D + 128GB RAM) wird so ausgelegt, dass diese Läufe dauerhaft parallel möglich sind.  
- Optional: externe Rechenressourcen (Vast.ai, Cloud) werden genutzt, wenn lokale Ressourcen blockiert sind.  

### 2.5 Fehlerprävention
- **Spaltennamen-Konsistenz:** Alle CSV-Dateien werden vor Analyse auf erwartete Spalten geprüft (`Combination`, `open_time`, `close`, `volume` …).  
- **Robustes Error-Handling:** Fehler pro Strategie werden gesammelt und am Ende ausgegeben (kein Abbruch des gesamten Laufs).  
- **Redundanz-Vermeidung:** Keine wiederholten Fehler pro Zeile – einmal erkannt → in einem zentralen Log notiert.  
- **Validierungs-Checks:**  
  - Minimum an Trades (≥5) pro Strategie.  
  - Winrate und ROI dürfen nicht NaN sein.  
  - Falls Kennzahlen fehlen → Strategie wird übersprungen und geloggt.  

### 2.6 Erweiterbarkeit
- Alles ist **modular** aufgebaut (Baukastenprinzip).  
- Neue Features (z. B. Volumen, Marktregime, Multi-Coin) lassen sich **einschalten oder deaktivieren**, ohne die Grundarchitektur zu zerstören.  
- Jedes Modul hat klar definierte Ein- und Ausgaben (Inputs: Kursdaten/Signale, Outputs: Kennzahlen/CSV).  

---

## 3. Analyse-Pipeline

Die Analyse-Pipeline beschreibt den **Workflow vom Rohsignal bis zur Strategie-Evaluation**.  
Sie ist modular aufgebaut und erlaubt schrittweise Erweiterungen (Baukastensystem).

---

### 3.1 Signal-Generierung
- Basisindikatoren: **RSI, MACD, Bollinger, MA200, Stochastik, ATR, EMA50**.  
- Erweiterungen: **Volumen-Features (OBV, MFI, Spikes, VWAP)**, **Marktregime-Labels** (Bull/Bear/Seitwärts), **Cross-Market-Features** (ETH, SOL, …).  
- Einheitliches Signal-Format: –1 (Short), 0 (Neutral), +1 (Long).  

**Signalkonflikte**:  
- Falls mehrere Indikatoren widersprüchliche Signale liefern, entscheidet die **gewichtete Kombination**.  
- Falls Gesamtsignal = 0 → **keine Aktion** (Flat bleiben).  

---

### 3.2 Strategiekombinationen
- Strategien bestehen aus gewichteten Kombinationen der Indikatoren.  
- Ebenen: **2er, 3er, … bis 7er-Kombinationen**.  
- Gewichtungen: **0.1 bis 1.0 in 0.1er-Schritten**.  
- Ziel: **alle denkbaren Varianten** systematisch durchtesten.  
- **Clustering**: Ähnliche Strategien (nahezu gleiche Gewichtungen) können im Postprocessing zusammengefasst werden.  

---

### 3.3 SimTrading
- Kursdaten: historische BTCUSDT (5-Minuten).  
- Optional: Erweiterung auf weitere Coins (ETH/USDT, SOL/USDT …).  
- Simulation berücksichtigt:  
  - **Fees** (z. B. 0.05 %)  
  - **Slippage** (z. B. 0.02 %)  
  - **Orderausführung** zum nächsten Close nach Signal.  
- **Positionsgrößen:**  
  - Standard: fester Einsatz (1 Einheit pro Trade).  
  - Erweiterung: dynamische Allokation nach Marktregime (z. B. Bull-Modus = 80 % Long, 20 % Short).  
- Ergebnis pro Strategie: **Trade-Liste + Kennzahlen**.  

---

### 3.4 Ergebnis-Speicherung
- **strategy_results.csv**  
  - Spalten: `id, Combination, roi, winrate, sharpe, trades, max_drawdown, profit_factor, …`.  
- **Trade-Historien pro Strategie**  
  - Gespeichert als `trades_<id>.csv`.  
- **Equity-Verläufe** (optional):  
  - Gespeichert als Plots (`equity_<id>.png`) oder CSV (`equity_<id>.csv`).  

---

### 3.5 Deep-Dive Analysen
- **Top-N-Filterung** (z. B. Top 300 000 nach ROI oder Sharpe).  
- **Feintuning um Top-Strategien**: Gewichtungen ±0.1/±0.2/±0.3.  
- **Batch-Processing:**  
  - Strategien werden in Blöcken (z. B. 5 000) verarbeitet.  
  - Zwischenergebnisse sofort gespeichert → kein Datenverlust bei Abbruch.  
- **Multiprocessing:**  
  - Parallelisierung über NUM_PROCS (lokal: 14, Workstation: 32+).  

---

### 3.6 Postprocessing & Auswertung
- **Ranking:** nach ROI, Sharpe Ratio, Winrate, Sortino, Profit Factor.  
- **Filter:** Mindestanzahl Trades ≥5, Winrate ≥50 %.  
- **Clustering:** Strategien mit ähnlichen Gewichtungen oder identischem Trade-Profil werden gruppiert.  
- **Robustheitsprüfung:** Walk-Forward-Test, Crash-Szenarien, Hochvolatilität vs. Seitwärts.  
- **Survivorship-Bias-Prüfung:** Strategien, die nur in einer Periode gut liefen, werden markiert.  

---

### 3.7 Selektivitätsziel
- Der Bot soll **~200 Trades pro Jahr (±100)** auslösen.  
- Übermäßiges Overtrading wird als Risiko bewertet.  
- Selektivität wird durch **Kombination mehrerer Filter** erreicht.  
- Ergebnisse außerhalb des Zielkorridors werden im Postprocessing markiert.  

---

## 4. Metriken & statistische Varianten

### 4.1 Deep-Dive Metriken
Direkt während des Backtests berechnet und gespeichert:  
- ROI  
- Winrate  
- Anzahl Trades  
- Maximaler Drawdown  
- Sharpe Ratio  
- Profit Factor  

---

### 4.2 Postprocessing Metriken
Aus gespeicherten Trade-Historien oder Equity-Verläufen abgeleitet:  
- Sortino Ratio  
- Calmar Ratio  
- Drawdown-Duration  
- Recovery Factor  
- Rolling-Volatilität  
- Clustering-Maße  

---

### 4.3 Statistische Varianten
- Verteilungen (ROI, Winrate, Sharpe).  
- Korrelationen zwischen Indikatoren.  
- Robustheits-Checks (Walk-Forward, Split-Tests).  
- Benchmark-Vergleich (Buy&Hold BTC).  
- Clustering nach ähnlichen Parametern/Ergebnissen.  

---

## 5. Erweiterungen: Marktregime & Volumen-Features

### 5.1 Marktregime-Labels
(Bull / Bear / Seitwärts; siehe Definitionen und Handlungslogik oben)

### 5.2 Volumen-Features
(OBV, MFI, Spikes, VWAP; siehe Details)

### 5.3 Fazit
(Marktregime = Makro, Volumen = Verstärker, Seitwärts = Schutz)

### 5.4 Multi-Coin-Analyse
(Cross-Market Confirmation BTC ↔ ETH, SOL, …)

### 5.5 Spezifische Kennzahlen für Marktregime & Volumen
- Regime-angepasster ROI, Sharpe, Stabilitäts-Score.  
- Volumen-gewichteter Profit Factor.  
- VWAP-Deviation, Spikes-Effizienz.  

### 5.6 Fazit (erweitert)
Regime + Volumen werden nicht nur als Filter genutzt, sondern auch als **eigene Auswertungsebenen**.  

---

## 6. Next Steps

Phasen-Roadmap von Konsolidierung → Feature-Erweiterung → Multi-Coin → Deep-Dive mit neuen Metriken → ML → Kapital-Allokation → High-End-Daten.  

---

## 7. Fazit

### 7.1 Zentrale Prinzipien
- Baukasten-System  
- Selektivität  
- Backups & Versionierung  
- Robustheit  
- Langläufe akzeptieren  

### 7.2 Phasen-Roadmap (Kurzüberblick)
(Phasen 1–7, siehe oben)

### 7.3 Endziel
Ein voll adaptiver Trading-Bot mit Marktregime, Volumen, Cross-Market, dynamischer Allokation und ML-Unterstützung.  

### 7.4 Fazit in einem Satz
Der Sniper-Bot ist kein starres System, sondern ein **dynamischer, modularer Baukasten**, der mit jedem Schritt präziser wird – von klassischen Filtern über Volumen & Marktregime bis hin zu Machine Learning und adaptiver Kapitalsteuerung.  

---

## 8. Datenbasis

### 8.1 Aktuelle Daten (Phase 1 – jetzt)
BTC/USDT 5-Minuten (Binance Spot).  

### 8.2 Erweiterte Daten (Phase 2 – mittelfristig)
ETH, SOL 5-Minuten + BTC/ETH/SOL 1-Minute.  

### 8.3 Hochauflösende Daten (Phase 3 – langfristig)
Futures-Volumen, Tick-Daten, Orderbuchdaten.  

### 8.4 Roadmap
Phase 1: BTC 5m → Phase 2: Multi-Coin 5m + 1m → Phase 3: Hochauflösende Daten.  

### 8.5 Fazit
Die Datenbasis ist **schrittweise erweiterbar** und deckt jetzt → mittelfristig → langfristig alle Bedürfnisse ab.  
