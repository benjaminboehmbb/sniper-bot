# STEP 10A - LONG MOMENTUM FADE EXIT

## Ausgangslage

Der Full-Run STEP9A_FULL_43M zeigte insgesamt starke Robustheit:

- Return: 140.22%
- Profit Factor: 1.6859
- Max Drawdown: 15.56%
- Trades: 556
- Winrate: 69.96%

Die Regime- und Lifecycle-Analyse zeigte jedoch ein klares Restproblem:

- sehr starke Gruppe: lt_15m_long
- schwache Gruppe: 15m_to_1h_long

Interpretation:

Gute LONG-Trades funktionieren sehr schnell.
Langsame LONG-Trades verlieren oft Momentum und werden toxisch.

## Hypothese

Wenn ein LONG-Trade nach 15 Minuten noch nicht positiv ist, hat er sein Momentum wahrscheinlich verloren.

Daher soll dieser Trade frueher geschlossen werden, ohne profitable schnelle LONGs zu beeintraechtigen.

## Aenderung in live_l1/core/execution.py

Neue Konstante:

LONG_MOMENTUM_FADE_EXIT_SEC = 900.0

Neue Exit-Logik nur fuer LONG:

Wenn:
- Position LONG
- duration_sec >= 900
- unrealized_pnl_long <= 0.0

Dann:
- CLOSE_LONG
- exit_reason = LONG_MOMENTUM_FADE_EXIT

Unveraendert bleiben:

- LONG_TIME_STOP_SEC = 3600.0
- SHORT_TIME_STOP_SEC = 3600.0
- TP = 5%
- SL = 1.5%
- Entry-Logik
- SHORT-Logik
- Loss-Cluster-Gate

## Ziel des Tests

Pruefen, ob der Long-Momentum-Fade-Exit:

- 15m_to_1h_long-Verluste reduziert
- Drawdown senkt
- lt_15m_long-Staerke erhaelt
- Return nicht uebermaessig reduziert
- keine unerwuenschte Trade-Verzerrung erzeugt

## Testreihenfolge

Erster Test:

200k @ offset 1,000,000

Nur bei klarer Verbesserung weitere Validierung:

1. 200k @ offset 0
2. 200k @ offset 500,000
3. 500k @ offset 1,500,000
4. 1M @ offset 2,500,000
5. 3M / Full-Run nur falls vorher bestaetigt

## Bewertungslogik

STEP 10A ist nur erfolgreich, wenn:

- Profit Factor nicht sinkt
- Max Drawdown sinkt oder stabil bleibt
- Return nicht deutlich schlechter wird
- die Anzahl der Trades plausibel bleibt
- LONG_MOMENTUM_FADE_EXIT nicht zu viele gute LONGs abschneidet

## Status

Implementiert fuer ersten Mini-Test.
Noch nicht validiert.


