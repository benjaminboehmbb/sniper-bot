# LIVE L1 Online Builders Architecture - 2026-06-05

## Ziel

Aktuell liest Live-L1 fertige Signal-, Regime- und Gate-Spalten aus CSV.

Ziel ist, diese Werte spaeter live aus OHLCV-Daten zu berechnen.

Aktuell:

CSV -> build_feature_snapshot -> intent.py -> intent_fusion.py -> execution.py

Ziel:

Live OHLCV -> signal_builder.py -> regime_builder.py -> gate_builder.py -> build_feature_snapshot -> intent.py -> intent_fusion.py -> execution.py

## Neue Zielmodule

### 1. live_l1/core/signal_builder.py

Aufgabe:

Berechnet online dieselben Signalspalten, die aktuell aus CSV gelesen werden.

Muss ausgeben:

- rsi_signal
- bollinger_signal
- stoch_signal
- cci_signal
- ma200_signal
- mfi_signal
- atr_signal
- macd_signal
- ema50_signal
- adx_signal
- obv_signal
- roc_signal

Wichtig fuer aktuelle Intent-Logik:

Score:

rsi_signal + bollinger_signal + stoch_signal + cci_signal

Entry-Gates:

ma200_signal
mfi_signal
atr_signal

### 2. live_l1/core/regime_builder.py

Aufgabe:

Berechnet online regime_v1.

Bestaetigte Ziel-Logik:

bull:
close > ma200 and ma200_slope_1440 > 0

bear:
close < ma200 and ma200_slope_1440 < 0

side:
sonst

Ausgabe:

regime_v1 = 1 bei bull
regime_v1 = 0 bei side
regime_v1 = -1 bei bear

### 3. live_l1/core/gate_builder.py

Aufgabe:

Berechnet online allow_long und allow_short.

Bestaetigte Ziel-Logik:

allow_long:
regime_v1 >= 0 and adx >= 15

allow_short:
regime_v1 == -1 and adx >= 20

## Strikte Abgrenzung

Diese Module duerfen keine Trades ausfuehren.

Sie duerfen nur Datenfelder berechnen.

Trading-Entscheidungen bleiben in:

- intent.py
- intent_fusion.py
- execution.py

## Mini-Test-Anforderung vor Implementierung

Vor jeder Live-Integration muss ein CSV-Vergleichstest gebaut werden:

Input:
bestehende CSV mit historischen fertigen Spalten

Test:
Online Builder berechnet dieselben Werte aus OHLCV nach

Vergleich:
alte CSV-Spalten vs. neu berechnete Builder-Spalten

Erlaubt:
kleine Differenzen nur bei Floating-Indikatoren nach dokumentierter Toleranz

Nicht erlaubt:
stille Logikabweichung bei Entry-Gates, Regime oder Intent-relevanten Signalen

## Naechster Schritt

Noch kein Produktionscode.

Als naechstes zuerst Teststruktur definieren:

tests/live_l1/test_online_builders_against_csv.py

Danach erst signal_builder.py implementieren.
