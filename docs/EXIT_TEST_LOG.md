# EXIT TEST LOG

## REGELN (VERBINDLICH)

* Nur 1 Logik- oder Parameteraenderung pro Run
* Jeder relevante Run wird dokumentiert
* 10k Runs sind nur Orientierung und nicht Bewertungsgrundlage
* Bewertung erfolgt ausschliesslich ueber >= 200k Runs

### Verbindliche Run-Hygiene

Vor jedem Validierungsrun muessen zwingend bereinigt werden:

* live_state/*.json
* live_state/*.jsonl
* live_logs/l1_paper.log
* live_logs/trades_l1.jsonl
* live_logs/trades_l1_auto_analysis.csv

---

## FORMAT

TP | SL | Ticks | Zusatz | Profit | PF | DD | Trades | Bewertung

---

## EXIT BASELINE TESTS

# TP=2%, SL=1%

0.02 | 0.01 | 10000  | baseline | +???     | ???    | ???    | ???  | short run, nicht bewerten
0.02 | 0.01 | 200000 | baseline | +???     | ???    | ???    | ???  | instabil, PF gefallen

# TP=3%, SL=1.5%

0.03 | 0.015 | 10000  | baseline | +???     | ???    | ???    | ???  | short run, nicht bewerten
0.03 | 0.015 | 200000 | baseline | +???     | ???    | ???    | ???  | keine Verbesserung

# TP=5%, SL=2% (finales Exit-Setup)

0.05 | 0.02 | 200000 | baseline | +30274 | 1.2968 | 0.1619 | 1592 | bestes stabiles Exit-Setup

---

## CRITICAL FIXES

### POSITION HANDOFF FIX (2026-04-10)

Problem:

* `intent.py` erhielt kein `current_position`

Folge:

* System lief effektiv immer im Zustand FLAT
* Exit-Logik war methodisch ungueltig

Fix:

* Position wird korrekt aus state uebergeben

Konsequenz:

* Alle vorherigen Runs dieser Phase sind ungueltig

---

### RUN HYGIENE FIX (2026-04-10)

Problem:

* Trade-Logs wurden nicht geloescht → kumulierte Auswertung

Fix:

* Logs muessen vor JEDEM Run geleert werden

---

### FULL STATE RESET FIX (2026-04-11)

Problem:

* `live_state` wurde nicht geloescht → nicht reproduzierbare Runs

Fix:

* Vollstaendiger Reset (Logs + State) ist verpflichtend

---

## EXIT LOGIC TEST

### EXIT HOLDING TEST (FAILED)

Aenderung:

* LONG Exit: 2x → 3x
* SHORT Exit: 1x → 2x

Ergebnis:

* Profit ↓
* PF ↓
* DD ↑

Schlussfolgerung:

* Schnelles Exit-Timing ist essenziell
* Exit bleibt unveraendert

---

## ENTRY OPTIMIZATION

### PHASE 1 – ENTRY HARDENING

3x >= 3 → 3x >= 4
→ Qualitaet ↑, aber zu wenig Trades

---

### PHASE 2 – ENTRY FREQUENCY INCREASE (BEST HISTORICAL RUN – INVALID)

Aenderung:

* confirmation_bars: 3 → 2
* threshold unveraendert (±4)

Ergebnis:

* final_equity: 12084.01
* profit_factor: 1.5838
* DD: 0.0279
* trades: 324

Status:

* NICHT reproduzierbar → verworfen

---

### PHASE 3 – OVER-HARDENING (FAILED)

2x >= 5

Ergebnis:

* Profit negativ
* PF < 1
* DD hoch

Schluss:

* Edge kollabiert bei zu strenger Selektion

---

### 3x>=4 DEGRADATION RUN

Ergebnis:

* schlechter als 2x>=4
* weniger Trades
* schlechter PF

→ verworfen

---

## BASELINE REPRO PHASE (FINAL)

Datum: 2026-04-12

### Vollstaendiges Setup

Intent-Logik:

FLAT Entry:

* confirmation_bars_entry = 2
* entry_score_threshold_long = +4
* entry_score_threshold_short = -4
* trendfilter_long = ma200_signal == +1
* trendfilter_short = ma200_signal == -1

Exit:

* long_exit_confirmation_bars = 2
* long_exit_threshold = -2
* short_exit_confirmation_bars = 1
* short_exit_threshold = +2

Execution:

* take_profit_pct = 0.05
* stop_loss_pct = 0.02

Run:

* ticks = 200000
* decision_tick_seconds = 0.001

---

### Ergebnisse (reproduzierbar)

Run 1:

* final_equity: 10605.62
* total_pnl: 605.62
* return_pct: 0.0606
* num_trades: 270
* winrate: 0.6963
* profit_factor: 1.0718
* avg_pnl: 2.2430
* max_drawdown_pct: 0.1716

Run 2:

* identisch (bitgenau)

---

### Bewertung

* System ist jetzt **deterministisch reproduzierbar**
* Edge vorhanden, aber schwach
* PF zu niedrig
* DD zu hoch
* Payoff ineffizient

---

### Finale Schlussfolgerung

* Historischer Best-Run ist ungueltig
* Neue Baseline ist realistisch und belastbar
* System handelt zu viele schwache Trades

---

### Aktuelle Baseline (verbindlich)

* final_equity ~10605
* profit_factor ~1.07
* max_drawdown_pct ~0.17
* trades ~270

---

## STATUS

Systemzustand:

* reproduzierbar: JA
* stabil: JA
* profitabel: leicht
* optimierungsbereit: JA

---

## NAECHSTER SCHRITT

Ziel:

* Qualitaet der Trades erhoehen
* Drawdown reduzieren
* PF verbessern

Ansatz:

* Entry-Filter verbessern (nicht Frequenz erhoehen)

Beispiel:

* Threshold-Test (>=5)
* oder Signalqualitaetsfilter

---

## KERNAUSSAGE

System ist jetzt methodisch korrekt aufgebaut.
Optimierung kann ab hier kontrolliert und valide erfolgen.



## ENTRY STATE - 2x>=4 (VALID RUN)

Datum: 2026-04-12

### Setup

Intent (exakt implementiert):

FLAT:
- BUY: ma200_signal == +1 AND 2x score >= +4
- SELL: ma200_signal == -1 AND 2x score <= -4

LONG:
- SELL: 2x score <= -2

SHORT:
- BUY: 1x score >= +2

Execution:
- TP = 5%
- SL = 2%

Run:
- ticks = 200000
- decision_tick_seconds = 0.001

if pos == "FLAT":
    ma200_sig = int(features.signal("ma200_signal"))

    if ma200_sig == 1 and _last_n_all_ge(2, 4):
        intent = "BUY"
    elif ma200_sig == -1 and _last_n_all_le(2, -4):
        intent = "SELL"

elif pos == "LONG":
    if _last_n_all_le(2, -2):
        intent = "SELL"

elif pos == "SHORT":
    if _last_n_all_ge(1, 2):
        intent = "BUY"
---

### Ergebnis

- final_equity: 10549.68
- total_pnl: 549.68
- return_pct: 0.0550
- num_trades: 198
- winrate: 0.6818
- profit_factor: 1.0798
- avg_pnl: 2.7762
- avg_duration_sec: 2327.88
- max_drawdown_abs: 1806.51
- max_drawdown_pct: 0.1477
- sharpe_like: 2.0143

---

### Bewertung

- Profit moderat, aber ineffizient
- PF zu niedrig → Edge schwach
- DD zu hoch im Verhältnis zum Profit
- avg_pnl sehr niedrig → viele schwache Trades
- Trade-Frequenz zu hoch für vorhandene Signalqualität

---

### Interpretation

- Lockeres Entry (2x>=4) erzeugt viele Low-Quality Trades
- Edge wird verwässert
- System verliert Selektivität

---

### Schlussfolgerung

Entry ist zu aggressiv.

---

### Entscheidung

- Setup verwerfen
- Rückkehr zu 3x>=4 als nächste valide Testbasis


Setup

Entry: 2x >= ±4 + ma200 + RSI-Filter
Exit:
LONG: 2x <= -2
SHORT: 1x >= +2
TP/SL: 5% / 2%
Run:
ticks: 200000
decision_tick_seconds: 0.001

Ergebnis

final_equity: 10549.68
total_pnl: 549.68
return_pct: 0.0550
num_trades: 198
winrate: 0.6818
profit_factor: 1.0798
avg_pnl: 2.7762
max_drawdown_pct: 0.1477
ANALYSE
identisch zur Baseline → RSI hat 0 Effekt
PF bleibt schwach → Edge unverändert schlecht
DD bleibt hoch → schlechte Trades bleiben drin


Setup

Entry: 2x >= ±4 + ma200 + MFI-Filter
Exit:
LONG: 2x <= -2
SHORT: 1x >= +2
TP/SL: 5% / 2%
Run:
ticks: 200000
decision_tick_seconds: 0.001

Ergebnis

final_equity: 11536.82
total_pnl: 1536.82
return_pct: 0.1537
num_trades: 182
winrate: 0.7033
profit_factor: 1.3119
avg_pnl: 8.4441
max_drawdown_pct: 0.0854
ANALYSE
PF deutlich ↑ (1.08 → 1.31)
DD stark ↓ (14.7% → 8.5%)
avg_pnl stark ↑ → bessere Trade-Qualität
Trades leicht ↓ → schlechte Trades entfernt
SCHLUSSFOLGERUNG

→ MFI filtert erfolgreich Low-Quality Trades

ENTSCHEIDUNG

→ übernehmen (neue Baseline)


Setup

Entry: 2x >= ±4 + ma200 + RSI AND MFI
Exit:
LONG: 2x <= -2
SHORT: 1x >= +2
TP/SL: 5% / 2%
Run:
ticks: 200000
decision_tick_seconds: 0.001

Ergebnis

final_equity: 11400.87
total_pnl: 1400.87
return_pct: 0.1401
num_trades: 109
winrate: 0.6789
profit_factor: 1.4166
avg_pnl: 12.8520
max_drawdown_pct: 0.0601
ANALYSE
PF ↑ (1.31 → 1.42)
DD ↓ (8.5% → 6.0%)
avg_pnl ↑ stark → sehr gute Trade-Qualität
Trades ↓ stark → klare Filterung
SCHLUSSFOLGERUNG

→ RSI + MFI verbessert Qualität weiter
→ weniger, aber deutlich bessere Trades

ENTSCHEIDUNG

→ übernehmen (neue beste Variante)


Setup

Entry: 2x >= ±4 + ma200 + RSI AND MFI
Exit:
LONG: 1x <= -2 (neu)
SHORT: 1x >= +2
TP/SL: 5% / 2%
Run:
ticks: 200000
decision_tick_seconds: 0.001

Ergebnis

final_equity: 11723.76
total_pnl: 1723.76
return_pct: 0.1724
num_trades: 109
winrate: 0.7064
profit_factor: 1.5967
avg_pnl: 15.8143
max_drawdown_pct: 0.0619
ANALYSE
PF ↑ (1.42 → 1.60)
Profit ↑
avg_pnl ↑ → bessere Exits
DD stabil niedrig (~6%)
Trades gleich → Qualität gesteigert ohne Frequenzverlust
SCHLUSSFOLGERUNG

→ schneller LONG-Exit verbessert System klar
→ Gewinne werden effizienter gesichert


Setup

Entry: 2x >= ±4 + ma200 + RSI AND MFI
Exit:
LONG: 1x <= -2
SHORT: 2x >= +2
TP/SL: 5% / 2%
Run:
ticks: 200000
decision_tick_seconds: 0.001

Ergebnis

final_equity: 11973.88
total_pnl: 1973.88
return_pct: 0.1974
num_trades: 109
winrate: 0.6972
profit_factor: 1.6323
avg_pnl: 18.1090
avg_duration_sec: 2125.32
max_drawdown_abs: 769.20
max_drawdown_pct: 0.0604
sharpe_like: 2.5336

Bewertung

Profit ↑
PF ↑
DD leicht ↓
avg_pnl ↑
Trades gleich

Schlussfolgerung

langsamerer SHORT-Exit verbessert das System
aktuelle beste Variante bisher


### TP HIT CHECK

Auswertung der exit_reason-Verteilung:
- CLOSE_LONG: 61
- CLOSE_SHORT: 36
- SL_LONG: 6
- SL_SHORT: 6
- TP_LONG: 0
- TP_SHORT: 0

Schlussfolgerung:
Der Take-Profit wurde im aktuellen Setup ueberhaupt nicht erreicht.
Eine Aenderung von TP 5% auf 6% konnte deshalb keinen Einfluss auf das Ergebnis haben.

Entscheidung:
TP ist aktuell kein wirksamer Optimierungshebel.
Weitere TP-Tests werden vorerst ausgesetzt.


Setup

Entry: 2x >= ±4 + ma200 + RSI AND MFI
Exit:
LONG: 1x <= -1 (neu)
SHORT: 2x >= +2
TP/SL: 5% / 2%
Run:
ticks: 200000
decision_tick_seconds: 0.001

Ergebnis

final_equity: 12204.83
total_pnl: 2204.83
return_pct: 0.2205
num_trades: 110
winrate: 0.6909
profit_factor: 1.8546
avg_pnl: 20.0439
avg_duration_sec: 1572.55
max_drawdown_abs: 696.17
max_drawdown_pct: 0.0541
sharpe_like: 2.6989

Bewertung

Profit ↑
PF ↑ stark
DD ↓
avg_pnl ↑
Trades praktisch gleich

Schlussfolgerung

schnellerer LONG-Exit verbessert das System klar
aktueller Best-Stand bisher


### EXIT REASON CHECK - BEST STATE

Auswertung:
- CLOSE_LONG: 64
- CLOSE_SHORT: 36
- SL_LONG: 4
- SL_SHORT: 6
- TP_LONG: 0
- TP_SHORT: 0

Schlussfolgerung:
Das System ist klar signal-exit-getrieben.
LONG-Exits sind der groessere Hebel als SHORT-Exits.
Der Wechsel auf LONG exit = 1x <= -1 war sinnvoll und bleibt bestehen.
TP ist weiterhin kein wirksamer Hebel.