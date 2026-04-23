# EXIT TEST LOG

## REGELN

* nur 1 Aenderung pro Run
* jeder relevante Run wird dokumentiert
* Bewertung nur auf Runs >= 200000 ticks
* Full Reset vor jedem Run:

  * `live_state/*.json`
  * `live_state/*.jsonl`
  * `live_logs/l1_paper.log`
  * `live_logs/trades_l1.jsonl`
  * `live_logs/trades_l1_auto_analysis.csv`

---

## EXIT BASELINE

TP=5%, SL=2% (final)

`0.05 | 0.02 | 200000 | baseline | +30274 | PF 1.30 | DD 0.16 | 1592 Trades`

-> bestes stabiles Exit-Setup

---

## KRITISCHE FIXES

### POSITION HANDOFF FIX (2026-04-10)

* vorher: Position wurde immer als FLAT behandelt
* Folge: Exit-Logik war ungueltig
* jetzt: Position wird korrekt uebergeben
* alle frueheren Runs davor sind ungueltig

### RUN HYGIENE FIX

* Logs wurden vorher nicht sauber geloescht
* Folge: verfälschte Auswertung

### FULL RESET FIX (2026-04-11)

* State wurde nicht geloescht
* Folge: Runs waren nicht sauber reproduzierbar

---

## BASELINE (REPRODUZIERBAR)

**Datum:** 2026-04-12

**Setup**

* Entry: 2x >= +-4 + ma200
* Exit:

  * LONG: 2x <= -2
  * SHORT: 1x >= +2
* TP/SL: 5% / 2%
* ticks: 200000

**Ergebnis**

* final_equity: ~10605
* PF: ~1.07
* DD: ~0.17
* Trades: ~270

**Einordnung**

* reproduzierbar
* aber schwach

---

## FILTER-ENTWICKLUNG

### 2x >= +-4 roh

* zu viele Trades
* zu niedrige Qualitaet

### RSI Filter

* kein sinnvoller Effekt

### MFI Filter

* PF besser
* DD niedriger
* avg_pnl besser
* schlechte Trades werden entfernt

### RSI + MFI

* weniger Trades
* deutlich bessere Qualitaet
* neuer Zwischenstandard

---

## EXIT-OPTIMIERUNG

### LONG Exit beschleunigt

* von `2x <= -2`
* auf `1x <= -2`
* Ergebnis: PF und Profit steigen

### SHORT Exit verzoegert

* von `1x >= +2`
* auf `2x >= +2`
* Ergebnis: PF steigt weiter

### Finaler Exit

* LONG: `1x <= -1`
* SHORT: `2x >= +2`

-> beste Exit-Kombination

---

## STAND: RSI + MFI

**Setup**

* Entry: 2x >= +-4 + ma200 + RSI + MFI
* Exit:

  * LONG: 1x <= -1
  * SHORT: 2x >= +2
* TP/SL: 5% / 2%
* ticks: 200000

**Ergebnis**

* final_equity: ~12204
* return: ~22%
* trades: ~110
* winrate: ~0.69
* profit_factor: ~1.85
* max_dd: ~0.054
* avg_pnl: ~20

**Einordnung**

* profitabel
* gute Qualitaet
* aber Robustheit noch ungeprueft

---

## OFFSET-TEST: RSI + MFI

### OFFSET 500000

**Setup**

* Entry: 2x >= +-4 + ma200 + RSI + MFI
* Exit:

  * LONG: 1x <= -1
  * SHORT: 2x >= +2
* TP/SL: 5% / 2%
* ticks: 200000
* offset: 500000

**Ergebnis**

* final_equity: 10788.02
* total_pnl: 788.02
* return_pct: 0.0788
* num_trades: 78
* winrate: 0.8462
* profit_factor: 7.9922
* avg_pnl: 10.1028
* avg_duration_sec: 1911.54
* max_drawdown_abs: 34.15
* max_drawdown_pct: 0.0033
* sharpe_like: 5.1568

**Einordnung**

* extrem selektiv
* sehr hohe Trade-Qualitaet
* aber klares Regime-Verhalten
* nicht robust genug

### OFFSET 1000000

**Setup**

* unveraendert

**Ergebnis**

* final_equity: 10679.23
* total_pnl: 679.23
* return_pct: 0.0679
* num_trades: 56
* winrate: 0.7679
* profit_factor: 2.6782
* avg_pnl: 12.1291
* avg_duration_sec: 1775.36
* max_drawdown_abs: 188.68
* max_drawdown_pct: 0.0175
* sharpe_like: 2.5121

**Einordnung**

* noch weniger Trades
* PF faellt stark
* Verhalten nicht konsistent
* klare Regime-Abhaengigkeit

**Entscheidung**

* RSI + MFI nicht robust genug
* Entry muss angepasst werden

---

## OR-VARIANTE

**Entry**

* ma200 bleibt
* RSI oder MFI statt RSI und MFI
* Schwelle bleibt 2x >= +-4

**Ergebnis**

* Profit stark hoeher
* Trades stark hoeher
* PF sinkt auf 1.47
* DD steigt auf fast 10%

**Einordnung**

* mehr Quantitaet
* weniger Qualitaet
* kein neuer Hauptstandard

**Entscheidung**

* nicht uebernehmen

---

## MFI-ONLY MIT 2x >= +-4

### OFFSET 0

**Setup**

* Entry: 2x >= +-4 + ma200 + MFI
* Exit:

  * LONG: 1x <= -1
  * SHORT: 2x >= +2
* TP/SL: 5% / 2%
* ticks: 200000
* offset: 0

**Ergebnis**

* final_equity: 12618.25
* total_pnl: 2618.25
* return_pct: 0.2618
* num_trades: 183
* winrate: 0.6995
* profit_factor: 1.6853
* avg_pnl: 14.3074
* avg_duration_sec: 1669.18
* max_drawdown_abs: 1112.11
* max_drawdown_pct: 0.0812
* sharpe_like: 2.9001

**Einordnung**

* sinnvoller Mittelweg
* besser als OR
* robuster Kandidat

### OFFSET 500000

**Ergebnis**

* final_equity: 11020.62
* total_pnl: 1020.62
* return_pct: 0.1021
* num_trades: 121
* winrate: 0.8347
* profit_factor: 5.1527
* avg_pnl: 8.4349
* avg_duration_sec: 1771.24
* max_drawdown_abs: 86.92
* max_drawdown_pct: 0.0078
* sharpe_like: 4.7368

**Einordnung**

* deutlich robuster
* aber noch nicht final bestaetigt

### OFFSET 1000000

**Ergebnis**

* final_equity: 10536.10
* total_pnl: 536.10
* return_pct: 0.0536
* num_trades: 103
* winrate: 0.6893
* profit_factor: 1.5096
* avg_pnl: 5.2049
* avg_duration_sec: 1871.07
* max_drawdown_abs: 246.42
* max_drawdown_pct: 0.0244
* sharpe_like: 1.5356

**Einordnung**

* wieder deutliche Schwankung
* nicht robust genug

**Entscheidung**

* Schwelle lockern von `2x >= +-4` auf `2x >= +-3`

---

## MFI-ONLY MIT 2x >= +-3

### OFFSET 0

**Setup**

* Entry: 2x >= +-3 + ma200 + MFI
* Exit:

  * LONG: 1x <= -1
  * SHORT: 2x >= +2
* TP/SL: 5% / 2%
* ticks: 200000
* offset: 0

**Ergebnis**

* final_equity: 16570.87
* total_pnl: 6570.87
* return_pct: 0.6571
* num_trades: 481
* winrate: 0.7152
* profit_factor: 1.6152
* avg_pnl: 13.6609
* avg_duration_sec: 1610.52
* max_drawdown_abs: 1469.06
* max_drawdown_pct: 0.0820
* sharpe_like: 4.6900

**Einordnung**

* deutlich stabiler als 2x >= +-4
* kein Trade-Kollaps
* neuer Hauptkandidat

### OFFSET 500000

**Ergebnis**

* final_equity: 11338.36
* total_pnl: 1338.36
* return_pct: 0.1338
* num_trades: 373
* winrate: 0.7051
* profit_factor: 1.7096
* avg_pnl: 3.5881
* avg_duration_sec: 1898.93
* max_drawdown_abs: 231.33
* max_drawdown_pct: 0.0216
* sharpe_like: 2.9146

**Einordnung**

* Trades bleiben hoch
* PF stabil
* DD niedrig
* klar robuster als fruehere Varianten

### OFFSET 1000000

**Ergebnis**

* final_equity: 11548.33
* total_pnl: 1548.33
* return_pct: 0.1548
* num_trades: 308
* winrate: 0.7435
* profit_factor: 1.6594
* avg_pnl: 5.0270
* avg_duration_sec: 1825.52
* max_drawdown_abs: 254.34
* max_drawdown_pct: 0.0248
* sharpe_like: 3.0527

**Einordnung**

* Aktivitaet bleibt stabil
* PF bleibt stabil
* DD bleibt niedrig
* Performance schwankt, aber bleibt positiv

**Schlussfolgerung**

* `2x >= +-3 + ma200 + MFI` ist robuste Basisstrategie
* PF stabil ueber Offsets
* keine extreme Regime-Abhaengigkeit mehr
* Basis fuer groeßere Fenster freigegeben

---

## FENSTERTESTS

### Geplante Fenster

* 500k -> offset 100000
* 1M -> offset 600000
* 3M -> offset 1300000

### Datensatz

* `l1_full_run.csv`
* Groesse: 4.374 Mio Zeilen

---

## 500k WINDOW TEST

**Setup**

* Entry: 2x >= +-3 + ma200 + MFI
* Exit:

  * LONG: 1x <= -1
  * SHORT: 2x >= +2
* TP/SL: 5% / 2%
* ticks: 500000
* offset: 100000

**Ergebnis**

* final_equity: 18001.92
* total_pnl: 8001.92
* return_pct: 0.8002
* num_trades: 982
* winrate: 0.6935
* profit_factor: 1.4617
* avg_pnl: 8.1486
* avg_duration_sec: 1882.12
* max_drawdown_abs: 2057.16
* max_drawdown_pct: 0.1359
* sharpe_like: 3.9878

**Einordnung**

* sehr hoher Profit
* aber zu viele Trades
* PF unter Zielbereich
* DD deutlich zu hoch
* System wird im groesseren Fenster zu aggressiv

**Entscheidung**

* noch keine Aenderung
* naechster Schritt: 1M Window Test

---

## AKTUELLER STAND

**Aktive Logik**

* Entry: `2x >= +-3 + ma200 + MFI`
* Exit:

  * LONG: `1x <= -1`
  * SHORT: `2x >= +2`
* TP/SL: `5% / 2%`

**Status**

* auf 200k robust bestaetigt
* auf 500k profitabel, aber zu aggressiv
* 1M Test laeuft / folgt


## PHASE: >=4 + ma200 + MFI

200k (offset 0)
return: 26.2% | trades: 183 | PF: 1.69 | DD: 8.1%
→ guter Qualitätskandidat

1M Window
return: 23.7% | trades: 483 | PF: 1.58 | DD: 9.3%
→ stabil, aber leicht verwässert

200k (offset 500k)
return: 10.2% | trades: 121 | PF: 5.15 | DD: 0.8%
→ extrem selektiv, regimeabhängig

200k (offset 1M)
return: 5.4% | trades: 103 | PF: 1.51 | DD: 2.4%
→ zu schwach → nicht robust

→ Entscheidung: Anpassung notwendig

---

## PHASE: 3x >=4 (mehr Bestätigung)

1M Window
return: 11.2% | trades: 158 | PF: 2.15 | DD: 2.6%
→ hohe Qualität, aber zu wenig Profit

200k (offset 0, LONG Exit 2x <= -1)
return: 26.8% | trades: 90 | PF: 2.68 | DD: 3.6%
→ sehr starke Qualität

200k (offset 500k)
return: 4.9% | trades: 41 | PF: 10.99 | DD: ~0%
→ viel zu selektiv

200k (offset 1M)
return: 0.9% | trades: 37 | PF: 1.21 | DD: 2.5%
→ Edge bricht komplett

→ Entscheidung: verwerfen (nicht robust)

---

## PHASE: asymmetrisch (LONG 2x / SHORT 3x)

200k (offset 0)
return: 17.5% | trades: 130 | PF: 1.51 | DD: 7.0%
→ mittelmäßig

→ Entscheidung: nicht ausreichend

---

## PHASE: LONG 2x >=4 / SHORT 3x <= -4

200k (offset 0)
return: 27.7% | trades: 90 | PF: 2.54 | DD: 4.1%
→ starker Qualitätskandidat

500k Window
return: 27.1% | trades: 258 | PF: 1.45 | DD: 4.6%
→ Aktivität ok, PF zu schwach

→ Entscheidung: nicht final

---

## PHASE: SCORE-FIX (MFI entfernt aus Score)

200k (offset 0)
return: 6.3% | trades: 64 | PF: 1.31 | DD: 4.9%

→ Ergebnis:
- Trades kollabieren
- PF schwach
- Setup zu restriktiv

→ Schluss:
kein Kandidat

→ Entscheidung:
Entry lockern auf 2x >= ±3


---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------

RUN – 200k (OFFSET 0)
(Score ohne MFI, Entry 2x >= ±3 + ma200 + MFI)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: rsi + bollinger + stoch + cci
Exit: LONG 2x <= -1 | SHORT 2x >= +2
TP/SL: 5% / 2%

Run
ticks: 200000
offset: 0
decision_tick_seconds: 0.001
fee_roundtrip: 0.0004

Ergebnis
final_equity: 14338.22
total_pnl: 4338.22
return_pct: 0.4338
num_trades: 226
winrate: 0.7124
profit_factor: 1.7523
avg_pnl: 19.1957
max_drawdown_pct: 0.0483
sharpe_like: 3.0507

Einordnung
Sehr gute Balance aus Aktivität und Qualität.
Trades im Zielbereich, PF im Zielbereich, DD niedrig.
Deutliche Verbesserung gegenüber >=4 Variante.

Schlussfolgerung
Erster valider Kandidat nach Score-Fix.
Setup zeigt saubere Performance unter Baseline-Bedingungen.

Entscheidung
Setup beibehalten.
→ nächster Schritt: Offset-Validierung (500k, 1M)


RUN – 200k (OFFSET 500k)
(Score ohne MFI, Entry 2x >= ±3 + ma200 + MFI)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: rsi + bollinger + stoch + cci
Exit: LONG 2x <= -1 | SHORT 2x >= +2
TP/SL: 5% / 2%

Run
ticks: 200000
offset: 500000
decision_tick_seconds: 0.001
fee_roundtrip: 0.0004

Ergebnis
final_equity: 11505.32
total_pnl: 1505.32
return_pct: 0.1505
num_trades: 176
winrate: 0.7443
profit_factor: 4.0178
avg_pnl: 8.5530
max_drawdown_pct: 0.0074
sharpe_like: 5.2624

Einordnung
Sehr hohe Trade-Qualität bei gleichzeitig ausreichender Aktivität.
PF extrem stark, DD minimal, Winrate hoch.
Trades weiterhin im Zielbereich.

Vergleich zu Offset 0
Trades leicht reduziert (226 → 176)
PF stark verbessert (1.75 → 4.02)
DD massiv reduziert (~4.8% → ~0.7%)

Interpretation
Setup zeigt in diesem Marktfenster sehr selektives und qualitativ hochwertiges Verhalten.
Deutliche Verbesserung der Edge ohne Kollaps der Trade-Frequenz.

Schlussfolgerung
Strategie bestätigt sich im zweiten Marktfenster.
Kein Hinweis auf Instabilität – im Gegenteil: Qualität steigt deutlich.

Entscheidung
Setup unverändert beibehalten.
→ nächster Schritt: Offset 1M zur finalen Robustheitsprüfung


RUN – 200k (OFFSET 1M)
(Score ohne MFI, Entry 2x >= ±3 + ma200 + MFI)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: rsi + bollinger + stoch + cci
Exit: LONG 2x <= -1 | SHORT 2x >= +2
TP/SL: 5% / 2%

Run
ticks: 200000
offset: 1000000
decision_tick_seconds: 0.001
fee_roundtrip: 0.0004

Ergebnis
final_equity: 10868.44
total_pnl: 868.44
return_pct: 0.0868
num_trades: 145
winrate: 0.7241
profit_factor: 1.6434
avg_pnl: 5.9892
avg_duration_sec: 2212.97
max_drawdown_abs: 353.31
max_drawdown_pct: 0.0347
sharpe_like: 2.1988

Einordnung
Trades bleiben im akzeptablen Bereich.
PF bleibt im Zielbereich.
DD bleibt niedrig und kontrolliert.
Kein Einbruch der Performance im spaeteren Marktfenster.

Vergleich
vs Offset 0:
- PF leicht niedriger (1.75 -> 1.64)
- Trades niedriger (226 -> 145)
- DD weiterhin niedrig

vs Offset 500k:
- PF deutlich niedriger (4.02 -> 1.64)
- DD weiter niedrig
- Aktivitaet bleibt erhalten

Interpretation
Das Setup zeigt ueber alle drei getesteten Offsets konsistentes Verhalten.
Die Strategie bleibt profitabel, kontrolliert und ohne Regime-Kollaps.

Schlussfolgerung
2x >= ±3 + ma200 + MFI mit Score ohne MFI und Exit
LONG 2x <= -1
SHORT 2x >= +2
ist aktuell der neue Hauptkandidat.

Entscheidung
Setup als robuste Basis bestaetigt.
jetzt: LONG 1x <= -1


RUN – 200k (OFFSET 0)
(Entry 2x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 53.34%
trades: 227
PF: 2.0991
DD: 4.57%
avg_pnl: 23.50

Einordnung
Deutliche Verbesserung:
- PF stark gestiegen (1.75 → 2.10)
- avg_pnl deutlich höher
- DD stabil
- Trades unverändert gut

Schlussfolgerung
LONG 1x <= -1 ist klar besser als 2x <= -1.

Entscheidung
Neuer Kandidat:
Entry 2x >= ±3 + ma200 + MFI
Exit LONG 1x <= -1 | SHORT 2x >= +2

→ nächster Schritt: Offset 500k


RUN – 200k (OFFSET 500k)
(Entry 2x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 14.49%
trades: 176
PF: 4.0437
DD: 0.75%
avg_pnl: 8.23

Einordnung
- PF extrem stark
- DD minimal
- Trades stabil im Zielbereich
- hohe Trade-Qualität

Vergleich zu Offset 0
- PF stark höher (2.10 → 4.04)
- DD massiv niedriger (4.6% → 0.7%)
- Trades leicht geringer, aber stabil

Schlussfolgerung
Setup bestätigt sich im zweiten Offset und zeigt sehr hohe Qualität.

Entscheidung
Setup beibehalten.
→ nächster Schritt: Offset 1M


RUN – 200k (OFFSET 1M)
(Entry 2x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 8.36%
trades: 145
PF: 1.6514
DD: 2.31%
avg_pnl: 5.76

Einordnung
- Trades stabil
- PF im Zielbereich
- DD niedrig
- keine Einbrüche

Vergleich
vs Offset 0:
PF leicht niedriger (2.10 → 1.65), aber stabil

vs Offset 500k:
PF deutlich niedriger (4.04 → 1.65), aber weiterhin solide

Schlussfolgerung
Setup ist über alle Offsets stabil und robust.

Entscheidung
Neuer Hauptkandidat bestätigt:
Entry 2x >= ±3 + ma200 + MFI
Exit LONG 1x <= -1 | SHORT 2x >= +2


RUN – 500k (OFFSET 100k)
(Entry 2x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 69.22%
trades: 469
PF: 1.8907
DD: 5.71%
avg_pnl: 14.76

Einordnung
- PF stark
- DD klar kontrolliert
- avg_pnl stark
- Aktivität hoch, aber noch sauber

Vergleich
vs alter 500k-Run:
PF klar besser
DD deutlich besser
Qualität insgesamt höher

Schlussfolgerung
Der neue Hauptkandidat bestätigt sich auch im 500k-Fenster.
Das Setup bleibt profitabel, kontrolliert und qualitativ stark.

Entscheidung
Setup beibehalten.
→ nächster Schritt: 1M Window


RUN – 1M (OFFSET 600k)
(Entry 2x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 41.14%
trades: 744
PF: 1.6206
DD: 7.58%
avg_pnl: 5.53

Einordnung
- PF im Zielbereich
- DD unter Kontrolle
- hohe Aktivität, aber stabil
- keine Instabilität über großes Fenster

Vergleich
vs 500k:
PF etwas niedriger (1.89 → 1.62)
DD etwas höher (5.7% → 7.6%)
→ erwartbar bei größerem Fenster

Schlussfolgerung
Setup bleibt auch auf 1M stabil und profitabel.

Entscheidung
Hauptkandidat bestätigt.

→ nächster Schritt: 3M Run


RUN – 3M (OFFSET 1M)
(Entry 2x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 2x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 411.30%
trades: 2708
PF: 1.3220
DD: 22.21%
avg_pnl: 15.19

Einordnung
- Profit extrem hoch
- PF klar zu niedrig
- DD viel zu hoch
- Aktivität zu hoch

Schlussfolgerung
Auf 3M kippt das Setup wieder in Richtung Masse statt Qualität.
Der Hauptkandidat ist damit auf Langfenster nicht sauber genug.

Entscheidung
In der aktuellen Form nicht final.
Nächster Schritt: Entry leicht strenger machen, Exit unverändert lassen.


RUN – 200k (OFFSET 0)
(Entry 3x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 3x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 49.83%
trades: 126
PF: 2.9349
DD: 3.95%
avg_pnl: 39.55

Einordnung

deutlich weniger Trades als zuvor
PF sehr stark
DD sehr niedrig
avg_pnl stark gestiegen
klare Qualitätssteigerung

Schlussfolgerung
Die Entry-Verschärfung wirkt wie gewünscht.
Schwache Signale werden effektiv gefiltert, Trades sind selektiver und profitabler.

Entscheidung
Setup lokal stark verbessert, aber noch nicht validiert.
Nächster Schritt: Test auf anderer Marktphase (200k @ 500k Offset).


RUN – 200k (OFFSET 500k)
(Entry 3x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 3x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 5.83%
trades: 81
PF: 3.4697
DD: 0.78%
avg_pnl: 7.20

Einordnung

sehr wenige Trades
extrem niedriger Drawdown
PF sehr hoch
avg_pnl deutlich niedriger als bei Offset 0
Gesamtprofit gering

Schlussfolgerung
Das Setup ist hier extrem selektiv und stabil, aber generiert zu wenig verwertbare Bewegung.
Performance stark abhängig von Marktphase.

Entscheidung
Entry aktuell zu restriktiv für bestimmte Phasen.
Nächster Schritt: weiterer Cross-Phase-Test (200k @ 1M Offset).


RUN – 200k (OFFSET 1M)
(Entry 3x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 3x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 5.34%
trades: 75
PF: 1.7780
DD: 1.94%
avg_pnl: 7.12

Einordnung

sehr wenige Trades
PF deutlich schwächer als bei anderen Offsets
DD weiterhin niedrig
avg_pnl niedrig
Performance insgesamt schwach

Schlussfolgerung
Das Setup verliert in dieser Marktphase klar an Qualität.
Die starke Selektivität führt hier zu wenig verwertbaren Trades bei gleichzeitig sinkender Effizienz.

Entscheidung
Entry in aktueller Form nicht robust genug über mehrere Marktphasen.
Nächster Schritt: Test auf größerem Fenster (500k @ 1.5M Offset) zur Bestätigung. -in meinem fall mache ich direkt 1mio über nacht als nächstes mit offset 2.5mio


RUN – 1M (OFFSET 600k)
(Entry 3x >= ±3 + ma200 + MFI, LONG Exit 1x <= -1)

Setup
Entry: 3x >= ±3 + ma200 + MFI
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 33.99%
trades: 558
PF: 1.2023
DD: 16.84%
avg_pnl: 6.09

Einordnung

Trades steigen wieder stark an
PF deutlich zu niedrig
DD hoch
avg_pnl niedrig
Qualität klar schlechter als in 200k Runs

Schlussfolgerung
Mit wachsender Datenmenge verliert das Setup erneut an Effizienz.
Intent.py verändert.

RUN – 200k (OFFSET 0)
(Entry 2x >= ±3 + ma200 + MFI + ADX, LONG Exit 1x <= -1)

Setup
Entry: 2x >= ±3 + ma200 + MFI + ADX
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 28.38%
trades: 113
PF: 2.5920
DD: 3.70%
avg_pnl: 25.11

Einordnung

deutlich reduzierte Trades
PF klar stark
DD niedrig
avg_pnl gut
qualitative Verbesserung sichtbar

Schlussfolgerung
Der zusaetzliche ADX-Filter verbessert die Entry-Qualitaet im ersten Testfenster deutlich.
Das Setup wirkt selektiv, kontrolliert und profitabel.

Entscheidung
Kandidat bleibt im Rennen, aber noch nicht robust bestaetigt.
Naechster Schritt: 200k @ 500k Offset.


RUN – 200k (OFFSET 500k)
(Entry 2x >= ±3 + ma200 + MFI + ADX, LONG Exit 1x <= -1)

Setup
Entry: 2x >= ±3 + ma200 + MFI + ADX
Score: ohne MFI
Exit: LONG 1x <= -1 | SHORT 2x >= +2

Ergebnis
return: 5.98%
trades: 74
PF: 7.8745
DD: 0.32%
avg_pnl: 8.08

Einordnung

sehr wenige Trades
extrem niedriger Drawdown
PF extrem hoch
avg_pnl moderat
Gesamtprofit gering

Schlussfolgerung
Der ADX-Filter macht das System in dieser Marktphase sehr selektiv und stabil, reduziert aber die Handelsaktivität stark.
Deutliches Regime-Verhalten bleibt bestehen.

Entscheidung
Kandidat zeigt hohe Qualität, aber mögliche Überfilterung.
Nächster Schritt: 200k @ 1M Offset zur finalen Cross-Phase-Bewertung.


