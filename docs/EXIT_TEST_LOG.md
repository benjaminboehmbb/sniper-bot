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


  
---

## RUN - STEP 5 LONG Time-Stop 60m - Validierungsstand

### Änderung
In `live_l1/core/execution.py` wurde ein LONG-only Time-Stop nach 60 Minuten ergänzt.

SHORT bleibt unverändert.

### Ergebnisse

| Run | Return | Trades | PF | DD | Bewertung |
|---|---:|---:|---:|---:|---|
| 200k @ 1,000,000 | 2.89% | 18 | 6.5189 | 0.37% | leicht besser |
| 200k @ 0 | 2.47% | 30 | 1.5543 | 1.86% | identisch |
| 200k @ 500,000 | 2.80% | 29 | 7.4537 | 0.33% | identisch |
| 500k @ 1,500,000 | 15.08% | 47 | 2.5785 | 5.15% | identisch |
| 1M @ 2,500,000 | 20.49% | 144 | 1.6102 | 7.84% | identisch |

### Bewertung
STEP 5 schadet in keinem getesteten Fenster.

Der Nutzen ist klein:
- leichte Verbesserung im 200k @ 1,000,000 Fenster
- sonst keine messbare Veränderung

### Entscheidung
STEP 5 bleibt aktiv.

### Zentrale Erkenntnis
Lange LONG-Trades können problematisch sein, treten aber zu selten auf, um alleine großen Einfluss auf das Gesamtsystem zu haben.

---

## RUN - STEP 6 LONG normal ATR Score >= 4 - FAIL

### Änderung
LONG bei normalem ATR verschärft:

- vorher: `3x score >= +3`
- neu: `3x score >= +4`

SHORT blieb unverändert.

STEP 5 blieb aktiv.

### Ergebnis 200k @ offset 1,000,000
- return_pct: 2.61%
- num_trades: 12
- winrate: 83.33%
- profit_factor: 18.4255
- max_drawdown_pct: 0.12%

### Ergebnis 200k @ offset 0
- return_pct: -0.28%
- num_trades: 13
- winrate: 61.54%
- profit_factor: 0.9040
- max_drawdown_pct: 1.87%

### Bewertung
Offset 1M verbessert sich stark:
- PF steigt massiv
- DD sinkt massiv

Aber:
- offset 0 bricht komplett

### Entscheidung
STEP 6 verworfen.

### Zentrale Erkenntnis
Globale LONG-Verschärfung ist nicht robust über verschiedene Marktphasen.

---

## RUN - STEP 7A SHORT-only Modelltest - FAIL als globale Variante

### Ziel
Prüfung eines reinen SHORT-Modells als mögliches Regime-Teilmodell.

### Änderung
LONG Entries deaktiviert.

SHORT unverändert:
- bad ATR SHORT: `3x score <= -4`
- normal ATR SHORT: `3x score <= -3`

STEP 5 blieb aktiv.

### Ergebnis 200k @ offset 1,000,000
- return_pct: 2.38%
- num_trades: 9
- winrate: 88.89%
- profit_factor: 77.0639
- max_drawdown_pct: 0.03%

### Ergebnis 200k @ offset 0
- return_pct: 0.09%
- num_trades: 11
- winrate: 54.55%
- profit_factor: 1.0294
- max_drawdown_pct: 2.53%

### Bewertung
Im schwachen Fenster extrem stark:
- extrem niedriger DD
- extrem hoher PF

Aber:
- nicht universell robust
- offset 0 deutlich schlechter als Baseline

### Entscheidung
STEP 7A verworfen als globale Strategie.

### Zentrale Erkenntnis
SHORT-only ist ein starkes Teilmodell für bestimmte Marktphasen, aber kein universeller Ersatz für das Gesamtmodell.

Das bestätigt:
- unterschiedliche Marktphasen benötigen unterschiedliche Modelle
- Regime-Switching ist der nächste logische Entwicklungsschritt

### Aktueller Stand
- `intent.py`: Baseline
- `execution.py`: STEP 5 aktiv


## STEP 7D - Offline Regime Mapping

Die Zuordnung von Trades zu Regimes soll bewusst nicht direkt in der Live-Execution erfolgen.

Grund:
- keine zusätzliche State-Komplexität
- keine versteckten Seiteneffekte
- keine Instabilität der Live-Engine

Stattdessen:

1. Regime werden pro Tick geloggt
2. Trades behalten normale Zeitstempel
3. analyse_regimes.py matched später:
   - entry_timestamp_utc
   - regime_snapshot timestamp_utc

Vorteile:
- deterministisch
- reproduzierbar
- einfacher debugbar
- keine Veränderung der Trading-Engine

Geplante spätere Erweiterung:
- nearest-regime matching
- rolling regime windows
- regime confidence scoring
- regime transition detection


## STEP 8B - LONG_TIME_STOP_SEC = 1800

Aenderung:
- LONG_TIME_STOP_SEC von 3600s auf 1800s reduziert
- SHORT unveraendert

Tests:
- 500k @ offset 1500000
- 1M @ offset 2500000

500k Ergebnis:
- Return: 14.05%
- PF: 2.40
- DD: 5.20%
- Trades: 47

Vergleich zur Baseline:
- leicht schlechter als 3600s
- aber noch relativ stabil

1M Ergebnis:
- Return: 19.01%
- PF: 1.545
- DD: 7.93%
- Trades: 144

Baseline 3600 Vergleich:
- Return vorher: 20.49%
- PF vorher: 1.610
- DD vorher: 7.84%

Interpretation:
- 1800s liefert keinen Vorteil gegenueber 3600s
- leichte Verschlechterung bei PF und Return
- keine Verbesserung beim Drawdown
- globale aggressive LONG-Verkuerzung nicht sinnvoll

Wichtige Erkenntnis:
- schnelle LONGS bleiben stark
- aber einige laengere Gewinner bleiben essenziell
- LONG-Struktur komplexer als initial angenommen

Schlussfolgerung:
- 1800s verworfen
- Rueckkehr zu 3600s Baseline


## STEP 10A - LONG MOMENTUM FADE EXIT - START

### Grundlage

Der 4.3M-Full-Run von STEP 9A war insgesamt stark, zeigte aber ein Restproblem bei 15m_to_1h_long-Trades.

### Hypothese

Gute LONGs funktionieren schnell.
Langsame LONGs verlieren Momentum.

### Neue Testlogik

In `live_l1/core/execution.py` wurde ergaenzt:

- LONG_MOMENTUM_FADE_EXIT_SEC = 900.0
- LONG wird nach 15 Minuten geschlossen, wenn unrealized PnL <= 0.0 ist
- exit_reason = LONG_MOMENTUM_FADE_EXIT

Unveraendert:

- LONG_TIME_STOP_SEC = 3600.0
- SHORT_TIME_STOP_SEC = 3600.0
- TP = 5%
- SL = 1.5%

### Erster Test

200k @ offset 1,000,000

### Status

Implementiert, Mini-Test laeuft bzw. wird als naechstes ausgewertet.


---

## STEP 11A - TRADE LIFECYCLE SNAPSHOT ANALYSIS - FULL 4.3M RUN

### Objective

Goal of STEP 11A was not strategy optimization itself, but collection of detailed lifecycle telemetry for long-running trades.

A new lifecycle snapshot logger was added to:

live_l1/core/loop.py

The logger writes periodic snapshots of open positions to:

live_logs/trade_lifecycle_snapshots.csv

Snapshots are recorded every 300 seconds once trade duration exceeds 900 seconds.

Collected fields include:

- side
- duration_sec
- unrealized_pnl
- current_score
- market_regime
- atr_quality
- ma200_signal
- atr_signal
- mfi_signal

### Full Run

Run configuration:

- Device: G15 / AR15
- Environment: WSL
- Dataset: data/l1_full_run.csv
- Full dataset run (~4.3M ticks)
- decision_tick_seconds = 0.0

### Final Result

- final_equity: 24022.01
- total_pnl: 14022.01
- return_pct: 140.22%
- num_trades: 556
- winrate: 69.96%
- profit_factor: 1.6859
- avg_pnl: 25.2194
- avg_duration_sec: 1642.01
- max_drawdown_abs: 2307.25
- max_drawdown_pct: 15.56%
- sharpe_like: 2.3841

### Lifecycle Snapshot Dataset

Generated file:

live_logs/archive/STEP11A_LIFECYCLE_FULL_43M_2026-05-16_22-12_lifecycle.csv

Rows collected:

- 1793 lifecycle snapshots

### Major Findings

Analysis focused on LONG trades in duration bucket:

15m_to_1h

Strong structural degradation was identified once LONG trades remained open for extended durations while market regime shifted into bear conditions.

Observed behavior:

- LONG trades >= 1500 sec became increasingly negative over time.
- Mean unrealized PnL deteriorated significantly with duration.
- LONG trades surviving into 2700-3600 sec windows were almost universally negative.
- Bear-regime persistence was a particularly strong signal.

Key result:

Condition:

- LONG
- duration >= 1500 sec
- unrealized_pnl <= 0
- market_regime == bear
- previous snapshot also bear

Produced:

- 159 negative lifecycle snapshots
- 62 affected trades
- virtually zero false positives
- no meaningful recovery behavior observed afterward

Average unrealized PnL under this condition:

approximately -182.6

Maximum observed value:

-0.23

This strongly suggests that prolonged LONG trades trapped in persistent bear regimes almost never recover meaningfully.

### STEP 11B Hypothesis

New candidate exit logic identified:

Exit LONG if:

- duration >= 1500 sec
- unrealized_pnl <= 0
- current_regime == bear
- previous_regime == bear

This differs fundamentally from STEP 10A:

- not a pure timer
- not a blind momentum fade
- regime-aware
- persistence-aware
- strongly data-backed from lifecycle telemetry

### STEP 11B Implementation

STEP 11B was implemented safely in:

live_l1/core/loop.py

NOT in execution.py.

Reason:

execution.py has no access to regime context.

Implementation details:

- current and previous regime labels tracked
- force exit triggers SELL intent while LONG is open
- exit reason overwritten to:

STEP11B_LONG_BEAR_REGIME_EXIT

### Current Status

STEP11B implementation completed.

Next step:

Controlled validation run:

- 200k ticks
- offset 1,000,000
- decision_tick_seconds = 0.0

before any larger validation.


## STEP 11B - LONG BEAR REGIME EXIT - 200k @ offset 0

### Setup

- Device: G15 / AR15
- Environment: WSL
- Market data: data/l1_full_run.csv
- Run length: 200,000 ticks
- Offset: 0
- decision_tick_seconds: 0.0

### Change

STEP11B was active in `live_l1/core/loop.py`.

Exit hypothesis:

- LONG position open
- duration >= 1500 sec
- unrealized_pnl <= 0.0
- current market_regime == bear
- previous market_regime == bear

Then force LONG close via SELL intent.

### Result

- final_equity: 10009.08
- total_pnl: 9.08
- return_pct: 0.09%
- num_trades: 30
- winrate: 63.33%
- profit_factor: 1.0158
- avg_pnl: 0.3027
- avg_duration_sec: 1420.00
- max_drawdown_abs: 225.64
- max_drawdown_pct: 2.23%
- sharpe_like: -0.0252

### STEP11B Trigger Check

Checked `live_logs/trades_l1.jsonl` for:

STEP11B_LONG_BEAR_REGIME_EXIT

Result:

- count: 0

### Evaluation

STEP11B did not trigger in this run.

Therefore, the weak result is not caused by STEP11B. The 200k @ offset 0 window remains structurally weak under the current STEP9A/STEP11B logic.

### Decision

No rejection of STEP11B based on this run.

Continue validation with:

- 200k @ offset 500,000


## STEP 11B - LONG BEAR REGIME EXIT - 200k @ offset 500,000

### Setup

- Device: G15 / AR15
- Environment: WSL
- Market data: data/l1_full_run.csv
- Run length: 200,000 ticks
- Offset: 500,000
- decision_tick_seconds: 0.0

### Change

STEP11B was active in `live_l1/core/loop.py`.

Exit hypothesis:

- LONG position open
- duration >= 1500 sec
- unrealized_pnl <= 0.0
- current market_regime == bear
- previous market_regime == bear

Then force LONG close via SELL intent.

### Result

- final_equity: 10123.24
- total_pnl: 123.24
- return_pct: 1.23%
- num_trades: 16
- winrate: 62.50%
- profit_factor: 4.7357
- avg_pnl: 7.7025
- avg_duration_sec: 1728.75
- max_drawdown_abs: 21.97
- max_drawdown_pct: 0.22%
- sharpe_like: 2.0973

### Evaluation

The run is clearly positive and stable.

Compared with the weak offset 0 result, STEP11B does not show broad instability. Drawdown remains very low, profit factor is strong, and trade count remains selective.

### Current Validation State

- 200k @ offset 1,000,000: strong improvement / 1 STEP11B trigger
- 200k @ offset 0: weak window, but STEP11B trigger count = 0
- 200k @ offset 500,000: positive and stable

### Decision

STEP11B remains a valid candidate.

Next validation step:

- 500k @ offset 1,500,000


## STEP 11B - LONG BEAR REGIME EXIT - 500k @ offset 1,500,000

### Setup

- Device: G15 / AR15
- Environment: WSL
- Market data: data/l1_full_run.csv
- Run length: 500,000 ticks
- Offset: 1,500,000
- decision_tick_seconds: 0.0

### Change

STEP11B active in `live_l1/core/loop.py`.

Exit hypothesis:

- LONG position open
- duration >= 1500 sec
- unrealized_pnl <= 0.0
- current market_regime == bear
- previous market_regime == bear

Then force LONG close via SELL intent.

### Result

- final_equity: 11267.16
- total_pnl: 1267.16
- return_pct: 12.67%
- num_trades: 46
- winrate: 65.22%
- profit_factor: 1.9771
- avg_pnl: 27.5470
- avg_duration_sec: 1480.43
- max_drawdown_abs: 440.04
- max_drawdown_pct: 4.24%
- sharpe_like: 2.0015

### Evaluation

STEP11B remains stable on the historically important 500k @ offset 1.5M window.

The average duration of 1480.43 sec is close to the STEP11B 1500 sec threshold, which supports the lifecycle hypothesis that late degrading LONG trades are being controlled earlier.

The result shows:

- positive return
- controlled drawdown
- acceptable trade count
- no obvious overfiltering
- no strategy collapse

### Current Validation State

- 200k @ offset 1,000,000: strong result, 1 STEP11B trigger
- 200k @ offset 0: weak window, but STEP11B trigger count = 0
- 200k @ offset 500,000: stable positive result
- 500k @ offset 1,500,000: stable positive result

### Decision

STEP11B remains a valid candidate.

Next validation step:

- 1M @ offset 2,500,000









---

## STEP 10A - LONG MOMENTUM FADE EXIT - 200k @ offset 1,000,000

### Setup

- Device: G15 / AR15
- Environment: WSL
- Market data: data/l1_full_run.csv
- Run length: 200,000 ticks
- Offset: 1,000,000

### Change

Added LONG momentum fade exit:

- LONG_MOMENTUM_FADE_EXIT_SEC = 900.0
- If LONG duration >= 900 sec and unrealized PnL <= 0.0:
  - close LONG
  - exit_reason = LONG_MOMENTUM_FADE_EXIT

Unchanged:

- LONG_TIME_STOP_SEC = 3600.0
- SHORT_TIME_STOP_SEC = 3600.0
- TP = 5%
- SL = 1.5%

### Result

- final_equity: 10144.00
- total_pnl: 144.00
- return_pct: 1.44%
- num_trades: 13
- winrate: 61.54%
- profit_factor: 4.9989
- avg_pnl: 11.0769
- avg_duration_sec: 1929.23
- max_drawdown_abs: 20.52
- max_drawdown_pct: 0.20%
- sharpe_like: 2.2491

### Comparison to STEP 9A baseline on same window

STEP 9A baseline:

- return_pct: approx. 2.88%
- profit_factor: approx. 6.42
- max_drawdown_pct: approx. 0.37%
- num_trades: 18

STEP 10A:

- return_pct: 1.44%
- profit_factor: 4.9989
- max_drawdown_pct: 0.20%
- num_trades: 13

### Evaluation

STEP 10A reduced drawdown, but also reduced return, profit factor, and trade count.

The hypothesis was directionally useful for risk reduction, but the rule is too restrictive or removes profitable recovery behavior.

### Decision

STEP 10A is rejected for now.

No further validation runs with this rule.

Return to STEP 9A execution baseline.
## STEP 10A - LONG MOMENTUM FADE EXIT - 200k @ offset 1,000,000

### Setup

- Device: G15 / AR15
- Environment: WSL
- Market data: data/l1_full_run.csv
- Run length: 200,000 ticks
- Offset: 1,000,000

### Change

Added LONG momentum fade exit:

- LONG_MOMENTUM_FADE_EXIT_SEC = 900.0
- If LONG duration >= 900 sec and unrealized PnL <= 0.0:
  - close LONG
  - exit_reason = LONG_MOMENTUM_FADE_EXIT

Unchanged:

- LONG_TIME_STOP_SEC = 3600.0
- SHORT_TIME_STOP_SEC = 3600.0
- TP = 5%
- SL = 1.5%

### Result

- final_equity: 10144.00
- total_pnl: 144.00
- return_pct: 1.44%
- num_trades: 13
- winrate: 61.54%
- profit_factor: 4.9989
- avg_pnl: 11.0769
- avg_duration_sec: 1929.23
- max_drawdown_abs: 20.52
- max_drawdown_pct: 0.20%
- sharpe_like: 2.2491

### Comparison to STEP 9A baseline on same window

STEP 9A baseline:

- return_pct: approx. 2.88%
- profit_factor: approx. 6.42
- max_drawdown_pct: approx. 0.37%
- num_trades: 18

STEP 10A:

- return_pct: 1.44%
- profit_factor: 4.9989
- max_drawdown_pct: 0.20%
- num_trades: 13

### Evaluation

STEP 10A reduced drawdown, but also reduced return, profit factor, and trade count.

The hypothesis was directionally useful for risk reduction, but the rule is too restrictive or removes profitable recovery behavior.

### Decision

STEP 10A is rejected for now.

No further validation runs with this rule.

Return to STEP 9A execution baseline.
## STEP 10A - LONG MOMENTUM FADE EXIT - 200k @ offset 1,000,000

### Setup

- Device: G15 / AR15
- Environment: WSL
- Market data: data/l1_full_run.csv
- Run length: 200,000 ticks
- Offset: 1,000,000

### Change

Added LONG momentum fade exit:

- LONG_MOMENTUM_FADE_EXIT_SEC = 900.0
- If LONG duration >= 900 sec and unrealized PnL <= 0.0:
  - close LONG
  - exit_reason = LONG_MOMENTUM_FADE_EXIT

Unchanged:

- LONG_TIME_STOP_SEC = 3600.0
- SHORT_TIME_STOP_SEC = 3600.0
- TP = 5%
- SL = 1.5%

### Result

- final_equity: 10144.00
- total_pnl: 144.00
- return_pct: 1.44%
- num_trades: 13
- winrate: 61.54%
- profit_factor: 4.9989
- avg_pnl: 11.0769
- avg_duration_sec: 1929.23
- max_drawdown_abs: 20.52
- max_drawdown_pct: 0.20%
- sharpe_like: 2.2491

### Comparison to STEP 9A baseline on same window

STEP 9A baseline:

- return_pct: approx. 2.88%
- profit_factor: approx. 6.42
- max_drawdown_pct: approx. 0.37%
- num_trades: 18

STEP 10A:

- return_pct: 1.44%
- profit_factor: 4.9989
- max_drawdown_pct: 0.20%
- num_trades: 13

### Evaluation

STEP 10A reduced drawdown, but also reduced return, profit factor, and trade count.

The hypothesis was directionally useful for risk reduction, but the rule is too restrictive or removes profitable recovery behavior.

### Decision

STEP 10A is rejected for now.

No further validation runs with this rule.

Return to STEP 9A execution baseline.



## STEP11A Research Transition Note

STEP11A began as an exit validation and lifecycle telemetry experiment.

However, the research evolved far beyond classical exit testing and led to the discovery of:
- dynamic trade health structures
- persistence asymmetry
- nonlinear recovery behavior
- momentum-driven recovery dynamics
- probabilistic recovery modeling

The research increasingly indicated that:
- markets behave as nonlinear probabilistic state systems
rather than:
- static linear signal systems.

As a result, STEP11A became the foundation for a broader state dynamics research framework.

See:

docs/STATE_DYNAMICS_RESEARCH.md


