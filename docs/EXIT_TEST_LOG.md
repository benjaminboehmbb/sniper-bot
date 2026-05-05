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



## RUN - SCORE 4 ONLY TEST - 200k @ offset 1,000,000

### Ziel
Pruefung, ob eine einfache Entry-Verschaerfung auf Score 4 only die finale Baseline verbessert.

### Aenderung
Testvariante in `live_l1/core/intent.py`:

- Normal ATR LONG: 3x score >= +3 -> 3x score >= +4
- Normal ATR SHORT: 3x score <= -3 -> 3x score <= -4

Bad ATR war bereits strikt und blieb unveraendert:

- Bad ATR LONG: 3x score >= +4
- Bad ATR SHORT: 3x score <= -4

### Setup
- Geraet: Workstation
- Environment: WSL
- Marktdatei: `data/l1_full_run.csv`
- Run: 200k ticks @ offset 1,000,000
- Startkapital: 10000.0
- Fee roundtrip: 0.0004
- TP: 5%
- SL: 1.5%
- Loss-Cluster-Gate: 5 Verluste aus 10 Trades, Pause 35 Entry-Blocks

### Ergebnis Score 4 only
- final_equity: 12152.09
- total_pnl: 2152.09
- return_pct: 21.52%
- num_trades: 299
- winrate: 68.56%
- profit_factor: 1.2094
- avg_pnl: 7.1976
- avg_duration_sec: 1994.05
- max_drawdown_abs: 3140.75
- max_drawdown_pct: 20.77%
- sharpe_like: 2.0167

### Vergleich zur finalen Baseline 200k @ offset 1,000,000
Baseline:
- return_pct: 2.88%
- num_trades: 18
- winrate: 83.33%
- profit_factor: 6.4185
- max_drawdown_pct: 0.37%

Score 4 only:
- return_pct: 21.52%
- num_trades: 299
- winrate: 68.56%
- profit_factor: 1.2094
- max_drawdown_pct: 20.77%

### Bewertung
Die Variante erzeugt deutlich mehr Return, aber auf Kosten der Strategiequalitaet.

Problem:
- Trade-Anzahl explodiert von 18 auf 299.
- Profit Factor faellt massiv von 6.4185 auf 1.2094.
- Max Drawdown steigt von 0.37% auf 20.77%.
- Damit verliert die Variante den Sniper-Charakter und wird zu riskant.

### Entscheidung
Score 4 only ist verworfen.

Die finale Baseline bleibt unveraendert:

- Bad ATR LONG: 3x score >= +4
- Normal ATR LONG: 3x score >= +3
- Bad ATR SHORT: 3x score <= -4
- Normal ATR SHORT: 3x score <= -3

### Archivierte Dateien
- `live_logs/archive/trades_score4only_FAIL_200k_offset1000000_2026-05-05.jsonl`
- `live_logs/archive/analysis_score4only_FAIL_200k_offset1000000_2026-05-05.csv`

### Naechster Schritt
Keine weitere einfache Entry-Verschaerfung testen.

Stattdessen gezielt STEP 2 pruefen:
- nicht pauschal Score 4 only
- sondern gezielte Fehlerbloecke aus der Regime-Analyse adressieren
- insbesondere Score -3, lange Trades und SL-Cluster


## RUN - STEP 2 (Score -3 vollständig entfernt) - 200k @ offset 1,000,000

### Ziel
Gezieltes Entfernen des identifizierten Fehlerblocks:
- Score -3 (negativer PF, Hauptverlusttreiber)

Ansatz:
- Nur Trades mit Score ±4 erlauben
- Score ±3 komplett eliminieren

### Änderung
In `live_l1/core/intent.py`:

Normal ATR wurde faktisch deaktiviert:
- LONG: 3x score >= +3 -> entfernt
- SHORT: 3x score <= -3 -> entfernt

Aktiv bleibt nur:
- LONG: 3x score >= +4
- SHORT: 3x score <= -4

### Setup
- Gerät: Workstation
- Environment: WSL
- Marktdatei: `data/l1_full_run.csv`
- Run: 200k ticks @ offset 1,000,000
- Startkapital: 10000.0
- TP: 5%
- SL: 1.5%
- Loss-Cluster-Gate: unverändert

### Ergebnis
- final_equity: 10123.39
- total_pnl: 123.39
- return_pct: 1.23%
- num_trades: 6
- winrate: 83.33%
- profit_factor: 11.4215
- avg_pnl: 20.5650
- avg_duration_sec: 2330.00
- max_drawdown_abs: 11.84
- max_drawdown_pct: 0.12%

### Bewertung
Erwartung:
- Eliminierung der Verlustquelle (Score -3)
- Verbesserung von PF und DD

Ergebnis:
- PF und DD stark verbessert
- aber Aktivität kollabiert (18 -> 6 Trades)
- Return stark reduziert (2.88% -> 1.23%)

### Interpretation
Das vollständige Entfernen von Score ±3 ist zu aggressiv:
- reduziert zwar Risiko
- zerstört aber die Handelsfrequenz
- verhindert ausreichend Kapitalrotation

Die Strategie verliert dadurch ihren praktischen Nutzen.

### Entscheidung
STEP 2 wird verworfen.

Die finale Baseline bleibt unverändert.

### Zentrale Erkenntnis
Das Problem liegt nicht im Score -3 allein, sondern in der Kombination:

- Score -3
- ATR-Zustand
- Trade-Dauer

Ein isoliertes Entfernen ist nicht ausreichend sinnvoll.

### Nächster Schritt
Gezielte Filterung statt harter Eliminierung:

- Score -3 nur unter bestimmten Bedingungen blockieren
- insbesondere abhängig von ATR (good_atr vs bad_atr)

→ Vorbereitung für STEP 3


## RUN - STEP 3 (SHORT normal ATR Score -4) - 200k @ offset 1,000,000

### Ziel
Gezielte Filterung des schwachen Fehlerblocks aus der Regime-Analyse:

- `short_score_-3`
- Score -3 war im 3M-Run negativ und wurde als potenzieller Verlusttreiber identifiziert.

### Änderung
In `live_l1/core/intent.py`:

SHORT Entry bei normalem ATR wurde verschärft:

- vorher: `3x score <= -3`
- neu: `3x score <= -4`

LONG Entry blieb unverändert:

- bad ATR LONG: `3x score >= +4`
- normal ATR LONG: `3x score >= +3`

SHORT bad ATR blieb unverändert:

- bad ATR SHORT: `3x score <= -4`

### Setup
- Geraet: Workstation
- Environment: WSL
- Marktdatei: `data/l1_full_run.csv`
- Run: 200k ticks @ offset 1,000,000
- Startkapital: 10000.0
- TP: 5%
- SL: 1.5%
- Loss-Cluster-Gate: unveraendert

### Ergebnis STEP 3
- final_equity: 10151.01
- total_pnl: 151.01
- return_pct: 1.51%
- num_trades: 12
- winrate: 83.33%
- profit_factor: 4.0136
- avg_pnl: 12.5842
- avg_duration_sec: 1930.00
- max_drawdown_abs: 38.27
- max_drawdown_pct: 0.38%
- sharpe_like: 1.9053

### Vergleich zur Baseline 200k @ offset 1,000,000
Baseline:
- return_pct: 2.88%
- num_trades: 18
- winrate: 83.33%
- profit_factor: 6.4185
- max_drawdown_pct: 0.37%

STEP 3:
- return_pct: 1.51%
- num_trades: 12
- winrate: 83.33%
- profit_factor: 4.0136
- max_drawdown_pct: 0.38%

### Bewertung
STEP 3 ist nicht besser als die Baseline.

Negativ:
- Return sinkt von 2.88% auf 1.51%.
- Trade-Anzahl sinkt von 18 auf 12.
- Profit Factor faellt von 6.4185 auf 4.0136.
- Drawdown verbessert sich nicht.

### Entscheidung
STEP 3 wird verworfen.

Die finale Baseline bleibt besser und wird wiederhergestellt:

- bad ATR LONG: `3x score >= +4`
- normal ATR LONG: `3x score >= +3`
- bad ATR SHORT: `3x score <= -4`
- normal ATR SHORT: `3x score <= -3`

### Zentrale Erkenntnis
Das einfache Entfernen von `short_score_-3` verbessert das System nicht.

Der Fehlerblock aus dem 3M-Run ist wahrscheinlich nicht allein durch Entry-Score loesbar, sondern entsteht im Zusammenspiel aus:

- Entry-Score
- Trade-Dauer
- Stop-Loss-Treffern
- Marktphase nach Entry

### Naechster Schritt
Keine weitere pauschale Entry-Verschaerfung.

Naechster sinnvoller Test:
- Exit-/Time-Filter pruefen
- insbesondere problematische lange Trades:
  - `1h_to_4h`
  - long/short getrennt
  - SL-Cluster getrennt analysieren


  






