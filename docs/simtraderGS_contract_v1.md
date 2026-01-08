# simtraderGS Contract v1 (Goldstandard)

Status: ACTIVE (v1)
Scope: Evaluation-Engine fuer Backtests (LONG/SHORT) mit diskreten Signal-Spalten.
Non-Scope: Daten-Build, Signal-Build, Regime-Labeling, Strategie-Generation, Result-Aggregation.

## 1) Zweck und Ziel
`engine/simtraderGS.py` ist die referenzierte, stabile Evaluations-Engine fuer alle K-Level Analysen.
Ziel ist Reproduzierbarkeit, deterministische Resultate und konsistente Kennzahlen.

- Einheitliche Auswertung fuer LONG und SHORT.
- Klare, dokumentierte Parameter.
- Keine impliziten Daten-Manipulationen.
- Performance: Signal-Caching pro Worker ist erlaubt, aber ohne semantische Aenderungen.

## 2) Public API (verbindlich)
### 2.1 Hauptfunktion
`evaluate_strategy(price_df, comb, direction) -> dict`

**Parameter**
- `price_df` : pandas DataFrame (Inputdaten)
- `comb`     : Strategie-Kombination (dict oder String-Dict)
- `direction`: "long" oder "short"

**Rueckgabe (Minimum Felder)**
Das Ergebnis-Dict MUSS mindestens diese Keys enthalten:
- `roi`        : float  (Summe der Trade-Returns; fee-frei)
- `roi_fee`    : float  (roi nach Fees; Definition siehe Abschnitt 6)
- `num_trades` : int
- `winrate`    : float  (Anteil positiver Trades, 0..1)
- `sharpe`     : float  (siehe Abschnitt 7)
- `avg_trade`  : float  (roi / num_trades, falls num_trades>0 sonst 0)
Optional zusaetzlich:
- `pnl_sum` (gleich roi), `avg_trade_fee` (roi_fee / num_trades), Exit-Counter, Diagnostics.

### 2.2 Determinismus
Bei identischen Inputs (price_df Inhalt, comb, direction, Parameter) MUSS die Ausgabe deterministisch sein.

## 3) Inputdaten: Pflichtspalten und Formate
### 3.1 Pflichtspalten
`price_df` MUSS enthalten:
- `close` : float

Signals:
- Mindestens die benoetigten `*_signal` Spalten fuer die in `comb` referenzierten Keys.
- Erwartet werden diskrete Werte in {-1, 0, +1}.
- Wenn Werte nicht diskret sind, darf simtraderGS sie intern auf -1/0/1 mappen:
  - >0 -> +1, <0 -> -1, sonst 0.

### 3.2 Erlaubte Zusatzspalten
- `timestamp_utc` (optional; wird fuer Core-Logik nicht benoetigt)
- Weitere Features (werden ignoriert)

## 4) Strategie-Definition (comb)
### 4.1 Erlaubte Formen
- Dict: `{"rsi": 1.0, "macd": 0.5, "ma200": 1.0}`
- Dict mit Spaltennamen: `{"rsi_signal": 1.0, ...}`
- String-Dict (JSON- oder Python-dict-String) ist optional, wenn Parser vorhanden ist.

### 4.2 Mapping-Regel
Es existiert ein KEYMAP:
- z.B. "rsi" -> "rsi_signal", "macd" -> "macd_signal", ...
Wenn Key nicht in KEYMAP ist, wird er als Spaltenname interpretiert.

### 4.3 Score-Definition
Pro Zeile i:
score[i] = Sum_j ( weight_j * signal_j[i] )

Signal_j[i] ist -1/0/+1.

## 5) Trade-Logik (Semantik)
### 5.1 Gemeinsame Parameter
- `enter_z`  : float  (Entry-Schwelle)
- `exit_z`   : float  (Exit-Schwelle)
- `take_profit_pct` : float (TP in Return-Einheiten, z.B. 0.04)
- `stop_loss_pct`   : float (SL in Return-Einheiten, z.B. 0.02)
- `max_hold_bars`   : int   (maximale Haltedauer in Bars; 1m Bars => 1440 = 1 Tag)

### 5.2 Entry-Regel
Ein Trade wird EROEFFNET an Index i, wenn:
- `score[i] > enter_z`
- Es wird nicht parallel ein zweiter Trade gehalten (single-position engine).

### 5.3 Exit-Regeln (Reihenfolge ist verbindlich)
Wenn Trade bei Index i eroefnet wurde, pruefe j = i+1 .. i+max_hold_bars:

Berechne Return r(j):

LONG:
  r = (close[j] - close[i]) / close[i]
SHORT:
  r = (close[i] - close[j]) / close[i]

Exit-Trigger in dieser Reihenfolge:
1) Take Profit: r >= take_profit_pct
2) Stop Loss  : r <= -stop_loss_pct
3) Score Exit : score[j] < exit_z
4) Max Hold   : wenn j erreicht (letzter erlaubter Bar)

Der Trade schliesst am ersten j, der die Bedingungen erfuellt.
Wenn kein Trigger bis max_hold greift, schliesst der Trade am letzten erlaubten Bar.

### 5.4 Trade-Return
- Der Trade-Return ist r zum Exit-Zeitpunkt (fee-frei).
- `roi` ist die Summe aller Trade-Returns.

### 5.5 Winrate
- Ein Trade gilt als Gewinn, wenn r > 0.
- winrate = wins / num_trades (falls num_trades>0 sonst 0)

## 6) Fees (v1 minimal)
### 6.1 Definition
Fee ist ein roundtrip fee pro Trade (Entry+Exit), als Anteil (z.B. 0.0004 = 4bp).

- `roi_fee` = Sum( r_k - fee_roundtrip ) ueber alle Trades k

Hinweis:
- Fee wird pro Trade einmal abgezogen (nicht pro Bar).
- Wenn fee_roundtrip=0, dann gilt roi_fee == roi.

### 6.2 avg_trade_fee (optional)
- avg_trade_fee = roi_fee / num_trades (falls num_trades>0 sonst 0)

## 7) Sharpe (v1)
Sharpe basiert auf Trade-Returns (fee-frei oder fee-bereinigt ist optional, Standard: fee-frei):
- Wenn num_trades < 2 => sharpe = 0
- sharpe = mean(returns) / std(returns)
- Bei std <= 1e-12 => sharpe = 0

## 8) Regime (AUSSERHALB simtraderGS)
Regime-Labels und Richtungs-Gating sind NICHT Bestandteil von `simtraderGS.py`.

Regime v1 (MA200 slope) wird extern gebaut und als Gate verwendet:
- allow_long  = (regime == bull)
- allow_short = (regime == bear)
- side => beides verboten

SimtraderGS selber bleibt unveraendert; Gating passiert im Caller (Analyze-Skripte / Tools).

## 9) Data Foundation (CSV Pfade)
Prebuilt CSVs werden durch Tools erstellt, nicht durch simtraderGS:
- Price CSV (GS 2017-2024): 
  data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2024_GS_WITH_SIGNALS.csv
- Price CSV (GS+Forward 2017-2025):
  data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS.csv
- Optional mit Regime v1:
  ..._REGIMEV1.csv

simtraderGS liest standardmaessig KEINE CSV selbst fuer Analysen (Caller stellt price_df).
Ein optionaler CSV-Loader ist erlaubt, aber darf die Semantik nicht veraendern.

## 10) Invarianten / Assertions (Tests muessen das pruefen)
- 0 <= winrate <= 1
- num_trades ist int >= 0
- roi, roi_fee, sharpe sind finite floats (nan/inf => 0)
- Bei fee_roundtrip > 0: roi_fee <= roi (wenn num_trades>0)
- Determinismus: gleiche Inputs => gleiche Outputs
- DIAGNOSTICS (tools/gs_short_diagnostics.py): DIAG vs BASE match muss True sein

## 11) Change Policy (Freeze-Ziel)
Ziel: In den naechsten Tagen/Wochen eine stabile v1 einfrieren.

Aenderungen an simtraderGS sind nur erlaubt, wenn:
1) Ein dokumentierter Bug vorliegt oder ein klarer Spezifikationspunkt ergaenzt wird,
2) Die Testsuite erweitert wird (Regression),
3) Output-Contract nicht unbemerkt bricht (oder bewusst als v2 versioniert wird).
