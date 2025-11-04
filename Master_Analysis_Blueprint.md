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

### 2.7 Risikomanagement & Kapitalsteuerung

**Ziel:** Kapital schützen, Verluste begrenzen, Positionsgrößen konsistent steuern. Regeln gelten für alle Strategien/Timeframes.

#### 2.7.1 Positionsgröße (Risk per Trade)
- **Risk per Trade:** max. `RISK_PER_TRADE = 1–2 %` des Kontos pro Trade.
- **Max. Positionsgröße:** `MAX_POS_PCT = 5 %` des Gesamtkapitals (Hard Cap).
- **Formel (vereinfacht):** Position = (Kontogröße × RISK_PER_TRADE) / Stop-Distanz.
- **Kelly-Ansatz (optional):** nur als Obergrenze; im Betrieb auf ≤ ½-Kelly begrenzen.

#### 2.7.2 Hebel (Leverage)
- **Standard:** kein/geringer Hebel (Spot bzw. 1×).
- **Erlaubt bis `LEVERAGE_LIMIT = 2–3×`**, nur wenn:
  - Mehrheits-Regime **Bull**/**Bear** (Kap. 5) **und** Volumen-Bestätigung (5.2),
  - keine Seitwärtsphase (5.1) und Spread/Slippage < Schwellwert.
- In **Seitwärtsphasen:** Hebel **deaktiviert**.

#### 2.7.3 Stop-Loss & Exit
- **Fixer Stop:** z. B. `STOP_PCT = 1.5–3 %`.
- **ATR-Stop (empfohlen):** `STOP = k × ATR(period)`, Standard: `ATR_PERIOD = 14`, `ATR_K = 2.0`.
- **Trailing-Stop:** enger von { fester Trailing-% , `ATR_TRAIL_K × ATR` }.
- **Break-Even-Shift:** nach Gewinn von `≥ 1.0R` Stop auf Einstand.
- **Time-Stop (optional):** Exit nach N Kerzen ohne Fortschritt.

#### 2.7.4 Portfolio-Sicht & Korrelation
- **Coin-Cap:** je Asset max. `ASSET_CAP = 20–40 %` des Kapitals.
- **Korrelation:** wenn ρ(BTC, Alt) > `0.8`, gemeinsame Exposures reduzieren (z. B. –30 %).
- **Netto-Exposure:** durch Regime-Score (Kap. 5) begrenzt:
  - `LONG_CAP = f(score)`, `SHORT_CAP = 1 − LONG_CAP`
  - Beispiel: Score ≥ +2 ⇒ `LONG_CAP ≈ 0.8–0.9`, Score ≤ −2 ⇒ `SHORT_CAP ≈ 0.8–0.9`.

#### 2.7.5 Drawdown-Kontrolle (Kontoschutz)
- **Max. Portfolio-DD:** `MAX_DD = 20–30 %`.
- **Stufenplan bei DD-Überschreitung:**
  1. Risk per Trade halbieren (`RISK_PER_TRADE ÷ 2`).
  2. Nur Trades **mit** Volumen-Bestätigung zulassen.
  3. Bei anhaltendem DD: **Pause** neuer Einstiege bis Erholung um `RECOVERY_PCT = 5–10 %`.

#### 2.7.6 Ausführungs-Risiken
- **Fees & Slippage** immer einpreisen (Baseline: 0.05 % / 0.02 %).
- **Liquidität:** Mindest-Volumen pro Kerze prüfen; bei dünnem Markt Positionsgröße drosseln.

#### 2.7.7 Parameter (Konstanten / Config)
`RISK_PER_TRADE=0.01–0.02`, `MAX_POS_PCT=0.05`, `LEVERAGE_LIMIT=2`,  
`ATR_PERIOD=14`, `ATR_K=2.0`, `ATR_TRAIL_K=1.5`, `STOP_PCT=0.02`,  
`ASSET_CAP=0.3`, `CORR_THRESHOLD=0.8`, `MAX_DD=0.25`, `RECOVERY_PCT=0.07`.

**Hinweis:** Diese Regeln werden in SimTrader/Execution-Layer abgebildet (Positionsgröße, Stops, Leverage-Check) und im Postprocessing überwacht (DD-Kontrolle).



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
- Falls mehrere Indikatoren widersprüchliche Signale liefern, entscheidet die **gewichtete Kombination** (z. B. RSI Long 0.7, MACD Short 0.3 → Gesamtsignal Long 0.4).  
- Falls Gesamtsignal = 0 → **keine Aktion** (Flat bleiben).  

---

### 3.2 Strategiekombinationen
- Strategien bestehen aus gewichteten Kombinationen der Indikatoren.  
- Ebenen: **2er, 3er, … bis 7er-Kombinationen**.  
- Gewichtungen: **0.1 bis 1.0 in 0.1er-Schritten** (keine Restriktion auf Summe = 1).  
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
  - Enthält eine Zeile pro Strategie.  
- **Trade-Historien pro Strategie**  
  - Gespeichert als `trades_<id>.csv`.  
  - Spalten: `timestamp, price, signal, pnl`.  
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
  - Fortschritts-Log im Terminal (z. B. „25 % | 12h elapsed | ETA 36h“).  

---

### 3.6 Postprocessing & Auswertung
- **Ranking:** nach ROI, Sharpe Ratio, Winrate, Sortino, Profit Factor.  
- **Filter:** Mindestanzahl Trades ≥5, Winrate ≥50 %.  
- **Clustering:** Strategien mit ähnlichen Gewichtungen oder identischem Trade-Profil werden gruppiert → Vermeidung von Doppelzählung.  
- **Robustheitsprüfung:**  
  - Aufteilung in mehrere Zeitfenster (Walk-Forward-Test).  
  - Überprüfung auf Konsistenz in Crash-Phasen (z. B. März 2020, FTX-Crash).  
  - Stresstests in Hochvolatilität vs. Seitwärtsphasen.  
- **Survivorship-Bias-Prüfung:**  
  - Strategien, die nur in einer Periode gut liefen, werden markiert.  
  - Nur Strategien mit stabiler Performance über mehrere Zeiträume gelten als robust.  

---

### 3.7 Selektivitätsziel
- Der Bot soll **~200 Trades pro Jahr (±100)** auslösen.  
- Übermäßiges Overtrading wird als Risiko bewertet.  
- Selektivität wird durch **Kombination mehrerer Filter** erreicht (z. B. RSI+MACD+Volumen+Regime).  
- Ergebnisse außerhalb des Zielkorridors werden im Postprocessing markiert.  

---

### 3.8 Beispiel-Workflow (von Signal bis Kennzahlen)

1. **Signal-Generierung:**  
   - RSI liefert +1 (Long), MACD liefert +1 (Long), Bollinger liefert 0 (Neutral).  
   - Gesamtsignal = +1.0 × 0.6 (RSI) + +1.0 × 0.3 (MACD) + 0 × 0.1 (Bollinger) = +0.9 → Long.

2. **Strategiekombination:**  
   - Gewichtung dieser Strategie: {RSI=0.6, MACD=0.3, Bollinger=0.1}.  
   - Kombination wird in der Strategien-Liste gespeichert.

3. **SimTrading:**  
   - Trade wird zum nächsten Candle-Close eröffnet.  
   - Position = (Kapital × 1 %) / ATR-Stop.  
   - Fees & Slippage werden berücksichtigt.  
   - Stop-Loss & Take-Profit nach Kap. 2.7 aktiv.

4. **Ergebnis-Speicherung:**  
   - Trade landet in `trades_<id>.csv`.  
   - Kapitalverlauf wird in Equity-Kurve geschrieben.

5. **Postprocessing:**  
   - ROI, Sharpe, Sortino, Calmar etc. werden berechnet.  
   - Strategie kommt in `strategy_results.csv`.  
   - Falls robust über mehrere Segmente → Kandidat für ML/Forward-Testing.


---

## 4. Metriken & statistische Varianten

Die Qualität einer Strategie wird anhand mehrerer Kennzahlen bewertet.  
Wir unterscheiden **Deep-Dive Metriken** (direkt im Backtest berechenbar) und **Postprocessing Metriken** (aus Trades/Equity abgeleitet).

---

### 4.1 Deep-Dive Metriken

#### ROI (Return on Investment)
- **Formel:**  
  \[
  ROI = \frac{Equity_{End} - Equity_{Start}}{Equity_{Start}}
  \]
- **Beispiel:** Start 1000 USDT, Ende 1200 USDT → ROI = (1200−1000)/1000 = **0.20 (20 %)**.

#### Winrate
- **Formel:**  
  \[
  Winrate = \frac{\text{#Gewinn-Trades}}{\text{#Gesamt-Trades}}
  \]
- **Beispiel:** 55 von 100 Trades positiv → Winrate = 55 %.

#### Anzahl Trades
- Absolute Zahl der abgeschlossenen Trades.  
- Selektivitäts-Check: Ziel ≈ 200 pro Jahr (±100).

#### Maximaler Drawdown (MDD)
- **Formel:**  
  \[
  MDD = \max_{t} \left( \frac{Peak_{t} - Equity_{t}}{Peak_{t}} \right)
  \]
- **Beispiel:** Peak = 1500, später Equity = 1200 → MDD = (1500−1200)/1500 = **20 %**.

#### Sharpe Ratio
- **Formel:**  
  \[
  Sharpe = \frac{E[R_p - R_f]}{\sigma_p}
  \]
  wobei \(R_p\) = Strategie-Rendite, \(R_f\) = risikoloser Zins (≈0), \(\sigma_p\) = Standardabweichung der Renditen.
- **Beispiel:** ROI = 15 %, Volatilität = 10 % → Sharpe = 0.15 / 0.10 = **1.5**.

#### Profit Factor (PF)
- **Formel:**  
  \[
  PF = \frac{\sum Gewinne}{|\sum Verluste|}
  \]
- **Beispiel:** Gewinne = 1500, Verluste = −1000 → PF = 1500 / 1000 = **1.5**.  
- Interpretation: >1 = profitabel; <1 = Verluststrategie.

#### Omega Ratio (vereinfachte Version)
- **Formel:**  
  \[
  Omega = \frac{\sum (R_i > 0)}{|\sum (R_i < 0)|}
  \]
  (Anteil positiver Renditen zu negativen Renditen, Basislinie = 0 %).
- **Beispiel:** Gewinne = 1800, Verluste = −1200 → Omega = 1800 / 1200 = **1.5**.

---

### 4.2 Postprocessing Metriken

Diese Kennzahlen erfordern gespeicherte Trade-Historien oder Equity-Kurven.

#### Sortino Ratio
- **Formel:**  
  \[
  Sortino = \frac{E[R_p - R_f]}{\sigma_{Downside}}
  \]
  wobei \(\sigma_{Downside}\) = Standardabweichung nur der negativen Renditen.
- Vorteil: Bestraft nur Abwärtsvolatilität.  

#### Calmar Ratio
- **Formel:**  
  \[
  Calmar = \frac{ROI_{annual}}{MDD}
  \]
- Beispiel: Jahres-ROI = 30 %, MDD = 15 % → Calmar = 2.0.

#### Ulcer Index (UI)
- Misst kumulierte Drawdowns über Zeit.  
- **Formel:**  
  \[
  UI = \sqrt{\frac{1}{n}\sum_{t=1}^{n} DD_t^2}
  \]
- **Ulcer Performance Index (UPI):**  
  \[
  UPI = \frac{ROI}{UI}
  \]

#### Skewness & Kurtosis (Trade-PnL-Verteilung)
- **Skewness:** Richtung der Verteilung. Positiv = viele kleine Verluste, wenige große Gewinne.  
- **Kurtosis:** „Fettigkeit“ der Tails. Hoch = Extremereignisse wahrscheinlicher.

#### Drawdown-Duration
- Dauer der längsten Phase, bis ein altes Equity-Peak wieder überschritten wird.  
- Wichtig für Kapitalbindung und Investor-Perspektive.

#### Rolling-Kennzahlen
- Rolling-Volatilität (z. B. 30 Tage).  
- Rolling-Sharpe/Sortino → Robustheit über Zeit prüfen.

---

### 4.3 Statistische Varianten
- **Verteilungen:** Histogramme von ROI, Sharpe, Winrate.  
- **Korrelationen:** Indikatoren ↔ Ergebnisse.  
- **Robustheits-Checks:** Walk-Forward, Split-Tests.  
- **Benchmark-Vergleich:** Jede Strategie vs. Buy&Hold BTC.  
- **Clustering:** Ähnliche Strategien gruppieren.


  

---

## 5. Erweiterungen: Marktregime & Volumen-Features

### 5.1 Marktregime-Labels (Bull / Bear / Seitwärts)

#### Definition
Marktregime werden über **mehrere Zeitebenen** (minütlich, stündlich, täglich, wöchentlich, monatlich) analysiert.  
Die Klassifizierung basiert auf folgenden Kriterien:

- **Bull-Markt:** 
  - Kurs oberhalb des MA200 (auf der jeweiligen Zeitebene).  
  - Folge von höheren Hochs und höheren Tiefs.  
  - ATR- oder Bollinger-Bänder zeigen steigende Volatilität.  

- **Bear-Markt:**  
  - Kurs unterhalb des MA200.  
  - Folge von niedrigeren Hochs und Tiefs.  
  - ATR- oder Bollinger-Bänder zeigen steigende Volatilität.  

- **Seitwärts-Markt (Range):**  
  - Kurs bewegt sich innerhalb eines Bandes ±5–10 % um den MA200.  
  - ATR niedrig, Bollinger-Band-Breite gering.  
  - Kein klarer Trend in Hoch-/Tief-Struktur.  
  - Optional: RSI oszilliert oft zwischen 40 und 60.

#### Mehrheitslogik
- Jede Zeitebene liefert ein Label (Bull = +1, Bear = –1, Seitwärts = 0).  
- **Gesamt-Score = Summe aller Timeframe-Werte.**  
  - Beispiel: Monatlich Bull (+1), Wöchentlich Bull (+1), Täglich Seitwärts (0), Stündlich Bear (–1), Minütlich Bear (–1) → Gesamt-Score = 0 → Neutral/Seitwärts.  

#### Handlungslogik
- **Bull-Modus (Score ≥ +2):**
  - Long-Strategien priorisieren.  
  - Kapitalallokation: 70–90 % Long, Rest für Short-Situationen.  
  - Short-Signale in Intraday ggf. ignorieren oder kleiner gewichten.  

- **Bear-Modus (Score ≤ –2):**
  - Short-Strategien priorisieren.  
  - Kapitalallokation: 70–90 % Short.  
  - Long-Signale in Intraday nur für sehr kurze Trades.  

- **Seitwärts-Modus (Score zwischen –1 und +1):**
  - Positionsgrößen stark reduzieren (max. 20–30 % des Kapitals).  
  - Fokus auf Mean-Reversion-Strategien (z. B. RSI-Extremwerte, Bollinger-Band-Kanten).  
  - Trendfolgende Strategien pausieren.  
  - Ziel: Kapitalschutz, Minimierung unnötiger Whipsaws.  

---

#### 5.2 Mehrdimensionale Regime-Analyse (Kurz-, Mittel-, Langfrist)

Um kurzfristige Impulse mit längerfristigen Trends zu verbinden, bewertet der Bot künftig **mehrere Zeitebenen parallel**:

| Zeitebene | Zeitraum | Bedeutung | Beispiel-Nutzung |
|------------|-----------|------------|------------------|
| **Kurzfristig** | 1 Minute – 1 Stunde | Mikro-Trend / Entry-Timing | Momentum-Erkennung für präzise Einstiege |
| **Mittelfristig** | 4 Stunden – 1 Tag | Trendrichtung / Filter | Tagestrend bärisch → Long-Signale abwerten |
| **Langfristig** | 1 – 30 Tage | Makro-Regime / Kapitalsteuerung | Bullmarkt → höhere Long-Allokation |

Jede Ebene erzeugt ein eigenes Label (`+1 = Bull`, `0 = Side`, `–1 = Bear`).  
Daraus entsteht ein kombinierter **Regime-Score**:

\[
R = \sum_i w_i \times r_i
\]

wobei \(r_i\) das Label und \(w_i\) das Gewicht der Zeitebene ist  
(z. B. w₁ = 0.5 für kurzfristig, w₂ = 0.3 für mittelfristig, w₃ = 0.2 für langfristig).

**Interpretation:**
- **R ≫ 0 → Bullisch:** Long-Trades bevorzugen.  
- **R ≈ 0 → Neutral:** Positionsgröße reduzieren.  
- **R ≪ 0 → Bärisch:** Short-Trades bevorzugen oder Longs früh schließen.

Dieser Mechanismus erlaubt z. B.:
- kurzfristig bullische, aber langfristig bärische Phasen zu erkennen,  
- Long-Positionen bei bärischem Tagestrend früh zu beenden,  
- Kapitalgewichtungen dynamisch an den kombinierten Regime-Score anzupassen.

Die Werte können zusätzlich in den **Trade-Historien** gespeichert werden  
(`market_regime_short`, `market_regime_mid`, `market_regime_long`, `regime_score`),  
um spätere ML-Analysen über Regime-Wechsel und Trade-Performance zu ermöglichen.


---

### 5.3 Volumen-Features (erweitert)

#### Datenquellen
- **Kurzfristig (jetzt):**  
  - Binance OHLCV-Daten (Spot) – enthalten bereits Volumen pro Kerze.  
  - Diese Daten sind in `price_data_with_signals.csv` vorhanden.  
- **Mittelfristig:**  
  - Zusätzliche Coins über Binance/CCXT laden (ETH/USDT, SOL/USDT, etc.), jeweils mit Volumen.  
  - Gleicher Zeitintervall (z. B. 5-Minuten oder 1-Minute) zur Synchronisation mit BTC.  
- **Langfristig:**  
  - Binance Futures API: liefert detaillierteres Volumen (z. B. Taker Buy vs. Taker Sell Volume).  
  - Tick-/Orderbuchdaten (Level 2) für hochauflösende Analysen: Orderflow, Imbalance, Cumulative Volume Delta (CVD).  

#### Berechnungen (jetzt sofort umsetzbar)
- **OBV (On-Balance-Volume):** misst Akkumulation vs. Distribution.  
- **MFI (Money Flow Index):** volumenadjustierter RSI.  
- **Volumen-Spikes:** aktuelles Volumen > 2× Durchschnitt der letzten 20 Perioden → Hinweis auf Marktimpuls.  
- **VWAP (Volume Weighted Average Price):** intraday zur Bestimmung von Support/Resistance.  

#### Erweiterte Berechnungen (später)
- **Taker Buy vs. Sell Volume:** Marktteilnehmer-Aktivität im Futures-Orderbuch.  
- **CVD (Cumulative Volume Delta):** misst Nettofluss aggressiver Käufer vs. Verkäufer.  
- **Orderbuch-Imbalance:** Verhältnis von Bid/Ask im Level-2-Orderbuch.  

#### Einsatz
- **Signal-Filter:** Nur handeln, wenn Signal durch Volumen bestätigt ist.  
- **Signal-Gewichtung:** Volumen multipliziert Signalkraft (z. B. RSI Long 0.7 × Volumenfaktor 1.2 = 0.84).  
- **Regime-Kombination:**  
  - Bull-Regime + Volumenanstieg = Long-Trade stark priorisieren.  
  - Bear-Regime + Volumenanstieg = Short-Trade stark priorisieren.  
  - Seitwärts-Regime + Volumenspitze = Range-Breakout → aggressiv handeln.  
- **Cross-Market Confirmation:** BTC-Signal + paralleler Volumenanstieg bei ETH → Signalverstärkung.  

#### Roadmap
1. **Phase 1 (jetzt):** Binance Spot-Volumen nutzen (OBV, MFI, Spikes, VWAP).  
2. **Phase 2 (nach Deep-Dive):** Multi-Coin-Volumen ergänzen (ETH, SOL, etc. via CCXT oder CSV).  
3. **Phase 3 (Workstation/ML):** Futures-Volumen und Orderbuchdaten einbinden.  


---

### 5.4 Fazit
Durch Marktregime-Labels und Volumen-Features entsteht ein **dynamisches Steuerungssystem**:  
- **Makro bestimmt die Kapitalrichtung (Bull/Bear/Seitwärts).**  
- **Volumen entscheidet über Stärke und Gewichtung einzelner Trades.**  
- **Seitwärtsphasen werden aktiv erkannt und abgesichert**, sodass Kapital nicht durch unnötige Trendfolgesignale verloren geht.  

---

### 5.5 Multi-Coin-Analyse (Cross-Market Confirmation)

#### Idee
Neben Bitcoin (BTC/USDT) sollen langfristig auch **weitere Kryptowährungen** (z. B. ETH, SOL, LTC) parallel analysiert werden.  
Ziel ist es, **Markttrends über mehrere Coins hinweg zu bestätigen** und so die Signalgüte zu erhöhen.  

#### Nutzen
- **Signal-Verstärkung:** Wenn BTC ein Long-Signal liefert und gleichzeitig ETH & SOL ebenfalls bullisch sind → höheres Vertrauen.  
- **Früherkennung:** Bestimmte Altcoins reagieren manchmal schneller (z. B. ETH zeigt den Ausbruch Sekunden/Minuten vor BTC).  
- **Signal-Filterung:** Wenn BTC ein Signal gibt, aber die Mehrheit der Altcoins gegensätzlich läuft → Trade vermeiden oder Position kleiner wählen.  
- **Diversifikation:** Später kann der Bot nicht nur BTC, sondern auch andere Coins direkt handeln.  

#### Umsetzung
- Erweiterung des PriceFeeds: mehrere CSV-Dateien (BTC, ETH, SOL, …) mit synchronisierten Timestamps.  
- Cross-Market-Features:  
  - **Korrelation** (BTC vs. Altcoin-Bewegungen).  
  - **Relative Stärke** (Coin X outperformt BTC über Zeitraum Y).  
  - **Trend-Delay** (ein Coin bricht zuerst aus, andere folgen).  
- Flexible Integration ins Baukastensystem:  
  - Cross-Market-Filter **optional aktivierbar**.  
  - Gewichtungen möglich (z. B. BTC 0.6, ETH 0.2, SOL 0.2).  


#### Fazit
Die Multi-Coin-Analyse dient als **Signal-Bestätigungsschicht**.  
Sie reduziert Fehlsignale, verbessert das Timing und schafft die Möglichkeit, Trends über den gesamten Markt hinweg zuverlässiger auszunutzen.  


### 5.6 Spezifische Kennzahlen für Marktregime & Volumen

#### Marktregime-Kennzahlen
- **Regime-angepasster ROI**: ROI getrennt nach Bull-, Bear- und Seitwärtsphasen → zeigt, ob eine Strategie in allen Märkten stabil ist.  
- **Regime-Sensitivität**: Wie stark verändert sich die Performance einer Strategie beim Wechsel des Marktregimes?  
- **Stabilitäts-Score**: Anteil der Regime, in denen eine Strategie profitabel bleibt.  
- **Regime-angepasster Sharpe/Sortino**: Risiko-adjustierte Rendite pro Marktphase.  
- **Kapital-Allokations-Effizienz**: misst, wie gut eine dynamische Anpassung (z. B. 80/20 im Bull-Modus) im Vergleich zu statischer Allokation abschneidet.  

#### Volumen-Kennzahlen
- **Volumen-gewichteter Profit Factor**: Gewinne/Verluste, gewichtet nach Handelsvolumen.  
- **Volumen-Bestätigungsscore**: Anteil der Trades, die bei hohem Volumen (z. B. >1.5× Durchschnitt) profitabel waren.  
- **Volumen-Divergenz-Score**: misst, ob Signale häufiger scheitern, wenn Preis- und Volumenrichtung auseinanderlaufen.  
- **VWAP-Deviation**: durchschnittlicher Abstand eines Trades vom Volume Weighted Average Price → misst „Qualität des Einstiegs“.  
- **Spikes-Effizienz**: wie oft Volumenspikes zu profitablen Breakouts führten.  

---

### 5.7 Extreme-Volatility-Regime

#### Definition
- Tritt auf, wenn ATR oder Realisierte Volatilität > 3 × Langfristdurchschnitt.  
- Oder wenn Preisbewegung > 10 % in weniger als 1 Stunde.  
- Beispiele: Corona-Crash März 2020, FTX-Kollaps.

#### Handlungslogik
- **Kapital-Reduktion:** Positionen auf 25–50 % Normalgröße reduzieren.  
- **Priorität:** nur Strategien mit Volumen-Bestätigung handeln.  
- **Fallback:** in extremen Fällen → Neutral-Modus, Trading-Pause.  

#### Nutzen
- Schutz vor Black-Swan-Verlusten.  
- Erkennen von Sonderphasen, in denen normale Regeln nicht gelten.  
- Separate Auswertung von Strategien in „Normal“ vs. „Extreme-Volatility“-Umgebungen.


### 5.8 Übersicht: Regime-Entscheidungslogik

Die Marktregime werden durch Kombination von **Trendindikator** (z. B. MA200, MACD) und **Volatilitätsindikator** (z. B. ATR, Bollinger-Bandbreite) definiert.

| Trendindikator | Volatilität niedrig/mittel | Volatilität hoch | Ergebnis-Regime |
|----------------|----------------------------|------------------|-----------------|
| Über MA200 / MACD > 0 | Stabil | - | **Bull-Markt** |
| Unter MA200 / MACD < 0 | Stabil | - | **Bear-Markt** |
| ± nahe MA200 / MACD ≈ 0 | Niedrig | - | **Seitwärts-Markt** |
| Über oder unter MA200 | Sehr hoch (ATR > 3×, >10 % Crash in <1h) | Ja | **Extreme-Volatility** |

#### Handlungslogik (Zusammenfassung)
- **Bull-Markt:** Long-Strategien bevorzugt, Kapitalallokation 70–90 % Long.  
- **Bear-Markt:** Short-Strategien bevorzugt, Kapitalallokation 70–90 % Short.  
- **Seitwärts-Markt:** Kapital stark reduziert (≤30 %), Fokus auf Mean-Reversion.  
- **Extreme-Volatility:** Positionen stark reduziert (25–50 % Normalgröße) oder Neutral-Modus.  

#### Nutzen
- Einheitliche, systematische Logik für alle Zeitebenen (1m, 1h, 1d, 1w, 1M).  
- Vermeidet subjektive Einschätzungen.  
- Grundlage für **dynamische Kapital-Allokation** (Kapitel 6.6).



---

## 6. Next Steps

Dieses Kapitel beschreibt die geplanten nächsten Schritte und Meilensteine.  
Sie sind bewusst in **Phasen** gegliedert, um eine saubere, nachvollziehbare Entwicklung sicherzustellen.

---

### 6.1 Phase 1 – Konsolidierung (jetzt - also September 2025)
- **Master-Blueprint fertigstellen** (diese Datei).  
- Sicherstellen, dass **Backups & Versionierung** zuverlässig funktionieren.  
- Aktuelle BTC/USDT 5-Minuten-Daten vollständig prüfen und sichern.  
- Deep-Dive-Analysen mit Standardmetriken (ROI, Winrate, Sharpe, Profit Factor).  
- Ergebnisse speichern: `strategy_results.csv`, Trade-Historien, Equity-Kurven.  

---

### 6.2 Phase 2 – Feature-Erweiterung (mittelfristig)
- **Volumen-Features aktivieren** (OBV, MFI, Spikes, VWAP).  
- Erste **Regime-Labels** implementieren (Bull/Bear/Seitwärts via MA200 + ATR/Bollinger).  
- **Neue Kennzahlen einführen:**  
  - Regime-angepasster ROI & Sharpe  
  - Volumen-Bestätigungsscore  
  - VWAP-Deviation  
- Strategien vergleichen: mit vs. ohne Volumen/Regime → Nutzen quantifizieren.  
- **Walk-Forward-Vorbereitung:**  
  - Daten in Segmente teilen (z. B. 3 Jahre Training, 6 Monate Test).  
  - Sicherstellen, dass alle Module (Signals, SimTrader) **Segment-basiert** lauffähig sind.  
  - Erste Mini-Walk-Forward-Läufe mit Top-Strategien testen.  

---

### 6.3 Phase 3 – Multi-Coin-Analyse
- Datenbasis um ETH/USDT & SOL/USDT erweitern (5m).  
- Cross-Market-Features einführen:  
  - Korrelation BTC ↔ ETH/SOL  
  - Trend-Delay-Analyse (führt Altcoin BTC an?)  
- Neue Kennzahlen:  
  - Cross-Market-Confirmation-Score (Anteil der Trades mit parallelem Signal bei mehreren Coins).  
- Bewertung: verbessert die Multi-Coin-Ebene die Robustheit?  

---

### 6.4 Phase 4 – Deep-Dive mit erweiterten Kennzahlen
- Erneute Top-N-Analyse inkl. **erweiterter Metriken**:  
  - Sortino, Calmar, Ulcer, UPI  
  - Regime-angepasste Kennzahlen  
  - Volumen-Kennzahlen  
- **Clustering & Survivorship-Bias** aktiv anwenden → stabile Strategien isolieren.  

#### Walk-Forward-Optimierung
- Schema: „Trainieren auf Periode A → Test auf Periode B“.  
- Perioden rollierend verschieben (z. B. 2017–2019 trainieren, 2020 testen; 2018–2020 trainieren, 2021 testen).  
- Ziel: Strategien identifizieren, die **nicht nur auf einer Zeitspanne** funktionieren, sondern robust durch mehrere Segmente hindurch.  

#### Forward Testing (Paper Trading)
- Top-Strategien im SimTrader auf den **neuesten, noch ungenutzten Daten** laufen lassen.  
- Ergebnisse vergleichen mit Deep-Dive.  
- Ziel: Fehlsignale oder Overfitting früh erkennen.  

#### Robustheitsprüfungen
- **Stabilitätsmatrix:** Performance-Metriken (ROI, Sharpe, Winrate) pro Jahr oder Quartal in einer Heatmap.  
- **Out-of-Sample-Checks:** Strategien, die nur in 1–2 Teilperioden gut laufen, werden ausgeschlossen.  
- **Monte-Carlo-Simulationen:**  
  - Trades permutieren oder in zufälliger Reihenfolge ziehen.  
  - Ziel: prüfen, ob Performance robust gegenüber zufälligen Sequenzen ist.  
- **Bootstrap-Analysen:** Equity-Kurven mit Resampling neu zusammensetzen, um Schwankungsbreiten von ROI/Sharpe abzuschätzen.  


---

### 6.5 Phase 5 – Machine Learning Vorbereitung
- Export von **Features & Labels**:  
  - Features = Indikatoren, Volumen, Regime, Cross-Market.  
  - Labels = Trade Ja/Nein, Profit >0 oder <0.  
- Erste Klassifikatoren testen (Random Forest, XGBoost).  
- ML-Output vergleichen mit klassischen Strategien.  
- Integration: ML als zusätzlicher Filter für Signale.  

---

### 6.6 Phase 6 – Kapital-Allokation & Live-Vorbereitung

#### Kapital-Allokation
- **Regime-abhängige Verteilung:**  
  - Bull: 70–90 % Long, 10–30 % Short.  
  - Bear: 70–90 % Short, 10–30 % Long.  
  - Seitwärts: max. 20–30 % Kapital, Fokus auf Mean-Reversion.  
- **Dynamische Anpassung:** Kapital wird rollierend nach Regime-Scores (Kap. 5) verschoben.  
- **Portfolio-Ebene:** Verteilung auf BTC/ETH/SOL etc. mit Korrelation-Check.  

#### Monitoring-System
- **Tägliche Reports:** ROI, Winrate, offene Positionen, Drawdown.  
- **Echtzeit-Alerts:**  
  - via Telegram/Discord/Email bei Überschreitung kritischer Schwellen (z. B. Drawdown > 15 %, Abweichung vom Benchmark > 10 %).  
- **Health-Checks:** prüfen, ob alle Module (PriceFeed, SimTrader, Signal-Engine) aktiv laufen.  

#### Fallback-Strategien
- **Neutral-Modus:** Keine neuen Trades, wenn Regime unklar oder Daten fehlen.  
- **Backup-Strategie:** Einfache Buy&Hold- oder Mean-Reversion-Strategie bei Hauptsystem-Ausfall.  
- **Graceful Shutdown:** Bei kritischen Fehlern laufende Positionen schließen und System pausieren.  

#### Not-Aus-Logik (Black-Swan-Schutz)
- **Max. Verlust pro Tag:** `DAILY_LOSS_CAP` (z. B. –5 %).  
- **Max. Verlust pro Woche:** `WEEKLY_LOSS_CAP` (z. B. –10 %).  
- **Global Circuit Breaker:** Bei >20 % Kurssturz in <1h → Trading sofort stoppen.  

#### Update-Frequenz
- **Re-Optimierung:** Strategien regelmäßig (z. B. wöchentlich/monatlich) gegen neue Daten testen.  
- **Walk-Forward-Routine:** kontinuierlich laufen lassen, um Strategien frisch zu halten.  
- **Automatisiertes Deployment:** nur geprüfte Strategien in den Live-Bot übernehmen.  

#### Ziel
- Sicherstellen, dass der Bot im **Live-Betrieb stabil, transparent und abgesichert** läuft.  
- Minimierung von Katastrophenrisiken durch klare Not-Aus-Mechanismen.  
- Maximale Nachvollziehbarkeit durch Monitoring und Alerts.
 

---

### 6.7 Phase 7 – Langfristige Erweiterungen
- Datenbasis auf 1m-Intervalle erweitern (BTC, ETH, SOL).  
- Futures-Volumen und ggf. Tick-/Orderbuchdaten einbinden.  
- ML-Modelle regelmäßig neu trainieren (Walk-Forward).  
- Ziel: **vollständig adaptiver Bot**, der auf Marktregime, Volumen und Cross-Market-Signale reagiert und Kapital intelligent allokiert.  
  

---

### 6.8 Phasenübersicht (kompakt)

| Phase | Fokus | Hauptaufgaben | Output |
|-------|-------|---------------|--------|
| **1. Konsolidierung** | Basis schaffen | Blueprint finalisieren, Daten/Backups prüfen, Standardmetriken (ROI, Winrate, Sharpe, PF) berechnen | Erste strategy_results.csv + Trade-Historien |
| **2. Feature-Erweiterung** | Volumen & Regime | OBV, MFI, VWAP, Regime-Labels (Bull/Bear/Sideways) implementieren, erste Regime-Kennzahlen | Vergleich mit/ohne Volumen+Regime |
| **3. Multi-Coin-Analyse** | Cross-Market | ETH, SOL Daten einbinden, Cross-Market-Features, Trend-Delay | Cross-Market-Confirmation-Score |
| **4. Deep-Dive mit erweiterten Metriken** | Robustheit & Kennzahlen | Sortino, Calmar, Ulcer, Monte-Carlo, Walk-Forward-Optimierung, Paper Testing | Top-N Strategien mit Robustheits-Siegel |
| **5. ML-Vorbereitung** | Feature/Label Export | Signale, Volumen, Regime, Cross-Market → Features; Trade Ja/Nein → Labels; erste Modelle (RF, XGBoost) | ML-Datensatz + erste Klassifikator-Ergebnisse |
| **6. Kapital-Allokation & Live-Vorbereitung** | Deployment & Schutz | Regime-abhängige Kapitalverteilung, Monitoring, Alerts, Fallback, Not-Aus-Logik | Simulierte Live-Strategien mit Schutzmechanismen |
| **7. Langfristige Erweiterungen** | High-End Daten & ML | 1m-Daten, Futures-Volumen, Tick/Orderbuch, regelmäßiges Re-Training, adaptiver Bot | Voll adaptives System mit Re-Optimierung |


---

### 7.1 Zentrale Prinzipien
- **Baukasten-System:** Alle Module (Indikatoren, Regime, Volumen, Multi-Coin, ML) sind einzeln kombinierbar, deaktivierbar oder erweiterbar.  
- **Selektivität:** Ziel sind ca. **200 Trades pro Jahr (±100)** – Qualität statt Quantität.  
- **Backups & Versionierung:** Jede Analyse ist reproduzierbar und mit Zeitstempel gesichert.  
- **Robustheit:** Strategien werden nicht nach Einzelergebnissen, sondern nach stabiler Performance über verschiedene Marktphasen bewertet.  
- **Langläufe akzeptieren:** Rechenintensive Analysen sind Teil des Prozesses – Workstation & ggf. Cloud-Ressourcen sind dafür eingeplant.  

---

### 7.2 Phasen-Roadmap (Kurzüberblick)
1. **Phase 1:** Konsolidierung & Standardmetriken.  
2. **Phase 2:** Volumen-Features + Regime-Labels.  
3. **Phase 3:** Multi-Coin-Analyse.  
4. **Phase 4:** Deep-Dive mit erweiterten Kennzahlen.  
5. **Phase 5:** ML-Vorbereitung (Features & Labels, erste Modelle).  
6. **Phase 6:** Kapital-Allokation & Forward Testing.  
7. **Phase 7:** Hochauflösende Daten, ML-Re-Training, adaptiver Bot.  

---

### 7.3 Endziel
Ein **vollständig adaptiver Trading-Bot**, der:  
- **Marktregime erkennt** (Bull, Bear, Seitwärts, Volatilitätsspitzen).  
- **Volumenbewegungen interpretiert** (OBV, MFI, VWAP, Spikes).  
- **Cross-Market-Signale nutzt** (BTC + ETH + SOL …).  
- **Strategien dynamisch auswählt und Kapital allokiert** (z. B. 80/20 im Bull, 90/10 im Bear).  
- **Laufend verbessert wird** durch Backtests, Deep-Dives und Machine Learning.  
- **Robust im Live-Betrieb** arbeitet und Monitoring/Alerts für Sicherheit bietet.  

---

### 7.4 Fazit in einem Satz
Der Sniper-Bot ist kein starres System, sondern ein **dynamischer, modularer Baukasten**, der mit jedem Schritt präziser wird – von klassischen Filtern über Volumen & Marktregime bis hin zu Machine Learning und adaptiver Kapitalsteuerung.


---

### 8.1 Aktuelle Daten (Phase 1 – jetzt)
- **BTC/USDT 5-Minuten-Daten (Binance Spot)**  
  - Enthalten in `price_data_with_signals.csv`.  
  - Spalten: `open_time, open, high, low, close, volume`.  
  - Zeitraum: ab ca. 2017 bis heute.  
- **Einsatz:**  
  - Hauptbasis für Backtests und Deep-Dive-Analysen.  
  - Berechnung aller klassischen Indikatoren (RSI, MACD, Bollinger, MA200, …).  
  - Volumen-Features (OBV, MFI, Spikes, VWAP) sind direkt nutzbar.  

---

### 8.2 Erweiterte Daten (Phase 2 – mittelfristig)
- **Weitere Coins (ETH/USDT, SOL/USDT, LTC/USDT, …)**  
  - Gleiche Auflösung (5-Minuten) und Zeitraum wie BTC.  
  - Quelle: Binance Spot über CSV-Dumps oder CCXT.  
  - Einsatz: Cross-Market Confirmation (Signalverstärkung oder -filterung).  

- **1-Minuten-Daten (BTC/USDT + ETH/USDT + SOL/USDT)**  
  - Quelle: Binance API oder Dumps.  
  - Höhere Auflösung → präzisere Features (z. B. Volumen-Spikes, kurzfristige Trends).  
  - Datenmenge: ca. 5× größer als 5m-Daten.  
  - Einsatz: Intraday-Analysen, ML-Features mit höherer Genauigkeit.  

---

### 8.3 Hochauflösende Daten (Phase 3 – langfristig)
- **Binance Futures-Daten**  
  - Enthalten: `open, high, low, close, volume, taker_buy_volume`.  
  - Vorteil: Trennung aggressiver Käufer/Verkäufer → detaillierte Orderflow-Features.  
  - Einsatz: ML-Features wie „wer dominiert gerade den Markt (Buyer vs. Seller)?“.  

- **Tick-Daten (Trades, Level 1)**  
  - Einzelne Trades (Preis, Volumen, Zeit).  
  - Datenmenge: sehr groß (100 GB+ pro Jahr).  
  - Einsatz: extrem feine ML-Features, präzise Volumenprofile.  

- **Orderbuchdaten (Level 2 / Level 3)**  
  - Enthalten: alle offenen Bid/Ask-Orders.  
  - Datenmenge: Terabyte-Bereich.  
  - Einsatz: nur für High-Frequency-Trading oder sehr tiefe ML-Experimente.  
  - Für das aktuelle Projekt **optional**, nur sinnvoll auf Workstation oder in der Cloud.  

---

### 8.4 Roadmap
- **Phase 1 (jetzt):** BTC/USDT 5m → Deep-Dive-Analysen und Basis-ML vorbereiten.  
- **Phase 2 (mittelfristig):** ETH/USDT & SOL/USDT (5m), plus 1m-Daten für BTC/ETH/SOL.  
- **Phase 3 (langfristig):** Futures-Volumen, Tick-/Orderbuchdaten, sobald Workstation & Speicher vorbereitet sind.  

---

### 8.5 Fazit
Die Datenbasis ist **schrittweise erweiterbar**:  
- Von einfachen 5m-Daten (jetzt)  
- Über 1m-Daten und Multi-Coin (mittelfristig)  
- Bis hin zu hochauflösenden Tick- und Orderbuchdaten (langfristig).  

Damit ist sichergestellt, dass die Analysen sowohl kurzfristig handhabbar als auch langfristig auf **höchstem Niveau erweiterbar** bleiben.


### 8.6 Datenqualität & Versionierung

#### Datenqualität-Checks
- **Fehlende Kerzen:** Prüfen, ob jede Zeiteinheit (5m, 1m) lückenlos vorhanden ist.  
- **Unplausible Werte:** Filter gegen Spikes (z. B. Preisabweichung > 20 % innerhalb einer Kerze).  
- **Volumen-Konsistenz:** Sicherstellen, dass Volumen nicht dauerhaft 0 oder unrealistisch hoch ist.  
- **Zeitzonen-Standardisierung:** Alle Timestamps in UTC speichern, um Konflikte bei Analysen zu vermeiden.  

#### Automatisiertes Laden & Aktualisieren
- **CCXT-Schnittstelle:** für den Abruf neuer OHLCV-Daten von Binance oder anderen Börsen.  
- **Batch-Downloader:** Automatisiertes Laden historischer Daten (z. B. 1m, 5m) mit Wiederaufnahme bei Abbrüchen.  
- **Synchronisierung mehrerer Coins:** BTC, ETH, SOL müssen **zeitlich exakt aligned** sein, bevor Cross-Market-Analysen möglich sind.  

#### Versionierung der Daten
- **CSV-Versionierung:** Jede neue Datenbasis erhält einen Zeitstempel (`price_data_5m_BTC_2025-09-04.csv`).  
- **Hash-Prüfung:** optional MD5/SHA256-Hash der CSV-Datei speichern → Manipulationen/Fehler sofort erkennbar.  
- **Git-LFS (Large File Storage):** für große CSV-Dateien nutzbar, um Versionierung über GitHub sicherzustellen.  
- **Backup-Regel:** Original-Rohdaten nie überschreiben, sondern nur neue Versionen anlegen.  

#### Ziel
- Sicherstellen, dass die Datenbasis **vollständig, korrekt und reproduzierbar** bleibt.  
- Vermeidung von Analysefehlern durch Datenlücken oder Inkonsistenzen.  
- Garantie, dass jede Analyse auf einer **definierten und versionierten Datenbasis** beruht.


### 8.7 Speicherplanung

#### Lokale Speicherung
- **Workstation:**  
  - 2 TB Samsung 990 Pro NVMe (primäre Daten & Backtests).  
  - 4 TB WD Black SN850X NVMe (Archiv, ältere Runs).  
- **Organisation:**  
  - Klare Ordnerstruktur (`data/raw`, `data/processed`, `results/backtests`).  
  - Zeitstempel in Dateinamen, keine Überschreibung.  

#### Externe Speicherung
- **Backups:** regelmäßige Sicherung auf externen SSDs/HDDs.  
- **Cloud (optional):** S3 oder Google Drive für Redundanz.  

#### Performance-Strategien
- **Chunking:** sehr große CSVs (z. B. 1m-Daten) in Quartals- oder Jahresdateien splitten.  
- **Kompression:** Parquet/Feather-Formate nutzen, um Speicherbedarf & Ladezeiten zu reduzieren.  
- **Daten-Caching:** häufig genutzte Teilmengen (z. B. BTC 2017–2020) in separaten Dateien bereithalten.

#### Ziel
- Speicher jederzeit skalierbar und organisiert.  
- Keine Engpässe bei Langläufen durch Daten-Chaos.  
- Reibungslose Nutzung lokaler und externer Ressourcen.

---



### 9 Sicherheit, Überwachung, Logging & Backup-Mechanismen

**Ziel:**  
Stabilen und sicheren 24/7-Live-Betrieb gewährleisten, Datenverlust vermeiden und sämtliche Trades, Signale sowie Systemereignisse reproduzierbar nachvollziehen.

---

#### 9.1 Sicherheit
- Verwende separate **API-Keys** für Trading und Datenzugriff (nur minimale Berechtigungen).  
- Lagere **Secrets** in `.env` oder verschlüsselten Config-Dateien, niemals im Git-Repo.  
- Aktiviere **IP-Whitelist** und **2FA** bei allen Exchanges und Cloud-Accounts.  
- Nutze **Read-Only-Keys** für Backtests, Analyse- und Logging-Prozesse.  
- Implementiere Fail-Safe-Mechanismen:  
  - automatisches **Order-Cancel**, wenn Bot unerwartet stoppt.  
  - **Max-Loss-Limit** pro Tag/Woche als Notbremse.  

---

#### 9.2 Überwachung
- Integriere ein **Monitoring-Modul**, das regelmäßig prüft:
  - Bot-Status (laufend / stopped / error)  
  - API-Verfügbarkeit & Latenz  
  - Konto-Balance, offene Positionen  
  - CPU-, RAM- und Festplattenauslastung  
- Benachrichtigungen via **E-Mail, Telegram oder Discord-Webhook**, falls:
  - ein Modul abstürzt,
  - zu viele Fehlversuche auftreten,
  - ungewöhnlich hohe Latenzen auftreten.
- Optional: Dashboard mit Echtzeit-KPIs (ROI, Sharpe-Ratio, aktuelle Trades).

---

#### 9.3 Logging
- **Zentrale Logdateien** im JSON- oder CSV-Format:
  - `system_log.csv` → Start/Stop, Warnungen, Ausnahmen  
  - `trade_log.csv` → Zeitpunkt, Symbol, Richtung, Preis, Profit/Loss, Fees  
  - `signal_log.csv` → Indikatorwerte, Entscheidung, Gewichtung  
- Strukturierte Logs (z. B. `logging`-Modul in Python mit `RotatingFileHandler`).  
- Alle Logs enthalten Timestamp (UTC ISO-Format) + Modulkennung.  
- Optional: separate **error_log.csv** zur späteren Fehleranalyse.  

---

#### 9.4 Backup-Mechanismen
- **Automatische tägliche Backups** für:
  - Datenfeeds (`price_data_with_signals.csv`, Feature-Files)
  - Ergebnisse (`strategy_results.csv`, Trade-Logs)
  - Konfigurationen (`config.yaml`, `.env`)
- Versions-Schema: `YYYY-MM-DD_HH-MM_description.ext`  
- Speicherung auf getrenntem Laufwerk oder Cloud (z. B. `D:/sniper-backups/` oder S3).  
- Monatliche Voll-Backups aller relevanten Projektverzeichnisse (`data/`, `results/`, `scripts/`).  
- Optional: Git-Commit-Hook, der vor jedem Run automatisch ein Backup-Tag erzeugt.  

---

#### 9.5 Best Practice
- Jeder **Analyse- oder Live-Run** startet mit:
  - `backup_current_results()`
  - `init_logger(run_id)`
  - `verify_api_status()`
- Kein Run überschreibt existierende Dateien.  
- Alle Ergebnisse eindeutig identifizierbar über `run_id` und Timestamp.  
- Logs und Backups dienen zugleich als Grundlage für Audits und Machine-Learning-Datenaufbereitung.



---

## 10. Fazit

Dieses Dokument ist die **Master-Blaupause** des Sniper-Bot Projekts.  
Es bildet die Grundlage für alle aktuellen und zukünftigen Entwicklungen – von klassischen Filter-Strategien über Marktregime & Volumen bis hin zu Machine Learning und Live-Betrieb.  

---

### 10.1 Zentrale Prinzipien
- **Baukasten-System:** modular, flexibel, jederzeit erweiterbar.  
- **Selektivität:** ca. 200 Trades pro Jahr (±100) – Qualität vor Quantität.  
- **Backups & Versionierung:** jede Analyse wird reproduzierbar und nachvollziehbar gespeichert.  
- **Risikomanagement:** klare Regeln für Positionsgröße, Hebel, Stop-Loss und Drawdown-Kontrolle.  
- **Langläufe akzeptieren:** rechenintensive Analysen sind Teil des Prozesses.  

---

### 10.2 Erweiterte Schwerpunkte
- **Marktregime & Volumen:** zentrale Filter- und Bewertungsdimensionen.  
- **Multi-Coin-Analyse:** Cross-Market Confirmation als Signalverstärkung.  
- **Erweiterte Metriken:** Sharpe, Sortino, Calmar, Profit Factor, Omega, Ulcer, Skew/Kurtosis.  
- **Walk-Forward & Forward Testing:** robuste Strategien erkennen und Overfitting minimieren.  
- **Robustheitsprüfungen:** Stabilitätsmatrix, Out-of-Sample-Checks, Monte-Carlo & Bootstrap.  
- **Monitoring & Live-Schutz:** Alerts, Fallback-Strategien, Not-Aus-Logik.  
- **Datenqualität & Versionierung:** Vollständigkeit, Hash-Prüfungen, automatisiertes Laden.  

---

### 10.3 Endziel
Ein **vollständig adaptiver Trading-Bot**, der:  
1. **Marktregime erkennt** und Kapital dynamisch allokiert.  
2. **Volumenbewegungen als Signalverstärker** nutzt.  
3. **Cross-Market-Signale** (BTC + ETH + SOL …) einbindet.  
4. **Robust durch Walk-Forward & Forward Testing** validiert ist.  
5. **Im Live-Betrieb abgesichert** läuft (Monitoring, Fallback, Not-Aus).  
6. **Laufend verbessert** wird durch Machine Learning und Re-Optimierung.  

---

### 10.4 Fazit in einem Satz
Der Sniper-Bot ist kein starres System, sondern ein **modularer, adaptiver Baukasten**, der mit jedem Schritt präziser, robuster und intelligenter wird – bis hin zum vollständig autonomen, marktintelligenten Live-Bot.
 

