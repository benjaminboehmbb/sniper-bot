# SNIPER-BOT – FINAL BASELINE (LÜCKENLOS, KOMPAKT)

## Daten
- BTCUSDT, 1m
- 2017–2025
- ~4.37 Mio Ticks
- data/l1_full_run.csv

---

## Regeln
- 1 Änderung pro Run
- Full Reset vor jedem Run
- Bewertung ab 200k
- Code = Wahrheit
- Logs IMMER archivieren
- Diese Version wird NICHT mehr verändert

---

## Run-Hygiene

Vor jedem Run:
rm -f live_logs/trades_l1.jsonl
rm -f live_logs/trades_l1_auto_analysis.csv
rm -f live_logs/l1_paper.log
rm -f live_logs/intent_debug*.log
rm -f live_logs/market_offset_*.csv
rm -f live_state/*.json
rm -f live_state/*.jsonl

Nach jedem Run:
mkdir -p live_logs/archive
cp live_logs/trades_l1.jsonl live_logs/archive/<runname>.jsonl
cp live_logs/trades_l1_auto_analysis.csv live_logs/archive/<runname>.csv

---

## Strategie (FINAL)

### Entry
LONG:
- ma200 == 1
- mfi == 1

SHORT:
- ma200 == -1
- mfi == -1

### Score
- rsi + bollinger + stoch + cci

### ATR (entscheidender Fix)
NORMAL:
- 3x >= ±3

SCHLECHT:
- 3x >= ±4 (3 Kerzen)

### Exit (FINAL, fix)
- LONG: 1x <= -1
- SHORT: 2x >= +2

### Risk
- TP: 5%
- SL: 1.5%

### Gate
- 5 Verluste aus 10 Trades → 25 Entry-Block

---

## Problem (früher)

- funktioniert auf 200k
- bricht auf 500k+
- DD 30–40%

Ursache:
→ falsche Trades in schlechten Marktphasen  
→ zu hohe Trade-Frequenz  

---

## Wichtige Erkenntnis

NICHT Problem:
- Entry
- Exit
- Score

SONDERN:
→ Marktphasen-Erkennung

---

## Lösung (entscheidend)

- SL reduziert → weniger große Verluste
- Gate ergänzt → reaktive Kontrolle
- ATR-strict → präventiver Schutz

👉 ATR-strict ist der Haupt-Fix

---

## Ergebnisse

### 200k (alle Offsets)
- stabil
- hoher PF
- niedriger DD
- teils sehr selektiv

### 500k @1.5M
ALT:
- PF ~1.1
- DD ~35%

NEU:
- PF ~2.2
- DD ~5–6%
→ Durchbruch

### 3M @1M
- Return ~122%
- PF ~1.9
- DD ~13%
→ stabiler Langlauf

---

## Charakter der Strategie

- weniger Trades
- höhere Qualität
- stabile DD-Kontrolle
- passt Aktivität an Marktphase an

---

## Validierungs-Sequenz (fix)

1. 200k @1M
2. 200k @0
3. 200k @500k
4. 500k @1.5M
5. 1M @2.5M
6. 3M @0

---

## Status

- DD-Problem gelöst
- System robust
- Langläufe stabil
- deterministisch (G15 + Workstation identisch)

---

## Nächste Schritte

1. Validierung abschließen
2. Baseline einfrieren
3. Git commit + tag
4. danach Feintuning

---

## Kernerkenntnis

Problem:
→ schlechte Marktphasen

Lösung:
→ strengere Entry-Anforderung bei schlechtem ATR


## RUN – Loss-Cluster-Gate + SL 1.5% + ATR-strict – 3M @ Offset 0

### Setup
- Datenbasis: `data/l1_full_run.csv`
- Run-Länge: 3,000,000 Ticks
- Offset: 0
- Entry:
  - MA200 + MFI Filter
  - ATR normal: 3x >= +/-3
  - ATR schlecht: 3x >= +/-4
- Exit:
  - LONG: 1x <= -1
  - SHORT: 2x >= +2
- TP/SL:
  - TP: 5%
  - SL: 1.5%
- Zusatzlogik:
  - Loss-Cluster-Gate aktiv

---

### Ergebnis
| Kennzahl | Wert |
|---|---:|
| Startkapital | 10,000.00 |
| Endkapital | 16,292.14 |
| Gewinn | 6,292.14 |
| Return | 62.92% |
| Trades | 345 |
| Winrate | 69.28% |
| Profit Factor | 1.5888 |
| Avg PnL | 18.2381 |
| Avg Duration | 2,028.52 sec |
| Max Drawdown | 2,084.64 |
| Max Drawdown % | 13.09% |
| Sharpe-like | 2.5907 |

---

### Einordnung
Der wichtigste Langlauf ist bestanden.

- Return stark
- PF stabil positiv
- DD kontrolliert
- Trade-Anzahl ausreichend
- keine DD-Explosion
- keine Überfilterung

---

### Bewertung
- Risiko: kontrolliert
- Robustheit: bestätigt
- Profitabilität: stark
- Langlauf-Stabilität: bestanden

---

### Entscheidung
Die Strategie ist über 3M Ticks ab Offset 0 robust bestätigt.


## RUN – Loss-Cluster-Gate + SL 1.5% + ATR-strict – 1M @ Offset 2,500,000

### Setup
- Datenbasis: `data/l1_full_run.csv`
- Run-Länge: 1,000,000 Ticks
- Offset: 2,500,000
- Entry:
  - MA200 + MFI Filter
  - ATR normal: 3x >= +/-3
  - ATR schlecht: 3x >= +/-4
- Exit:
  - LONG: 1x <= -1
  - SHORT: 2x >= +2
- TP/SL:
  - TP: 5%
  - SL: 1.5%
- Zusatzlogik:
  - Loss-Cluster-Gate aktiv

---

### Ergebnis
| Kennzahl | Wert |
|---|---:|
| Startkapital | 10,000.00 |
| Endkapital | 12,381.48 |
| Gewinn | 2,381.48 |
| Return | 23.81% |
| Trades | 160 |
| Winrate | 69.37% |
| Profit Factor | 1.6578 |
| Avg PnL | 14.88 |
| Avg Duration | 1,897.12 sec |
| Max Drawdown | 1,024.49 |
| Max Drawdown % | 7.64% |
| Sharpe-like | 2.2619 |

---

### Einordnung
Finaler Validierungs-Run bestätigt das Gesamtbild:

- stabiler Profit Factor > 1.5
- moderater Drawdown < 10%
- konsistente Winrate ~69%
- ausreichende Trade-Frequenz
- keine DD-Cluster / keine Instabilität

---

### Bewertung
- Risiko: gut kontrolliert
- Stabilität: hoch
- Profitabilität: klar positiv
- Verhalten konsistent mit allen anderen Runs

---

### Gesamtfazit (ALLE RUNS)

- 200k: stabil
- 500k: Durchbruch
- 1M: bestätigt
- 3M: bestätigt

→ keine Fenster zeigen strukturelles Versagen

---

### Finale Entscheidung

Die Strategie ist vollständig validiert:

- DD-Problem gelöst
- robust über alle Marktphasen
- deterministisch bestätigt (G15 + Workstation)
- keine weitere Änderung notwendig

---

### Status

FINAL BASELINE ERREICHT










