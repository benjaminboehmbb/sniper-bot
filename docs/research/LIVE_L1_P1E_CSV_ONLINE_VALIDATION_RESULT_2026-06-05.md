# LIVE L1 P1E CSV-vs-Online Validation Result - 2026-06-05

## Ziel

Validierung der neuen Online Builder gegen die aktuell verwendete CSV-Pipeline.

Geprueft wurden:

- signal_builder.py
- regime_builder.py
- gate_builder.py

gegen:

data/l1_full_run.csv

## Ergebnis

P1E ist fehlgeschlagen.

Die Online Builder reproduzieren data/l1_full_run.csv nicht ausreichend.

## Mismatch-Ergebnis

rows_checked:

200

window_rows:

2500

Signal-Mismatches:

rsi_signal: 39 / 200 = 19.50 %

macd_signal: 76 / 200 = 38.00 %

bollinger_signal: 21 / 200 = 10.50 %

ma200_signal: 200 / 200 = 100.00 %

stoch_signal: 133 / 200 = 66.50 %

atr_signal: 200 / 200 = 100.00 %

ema50_signal: 200 / 200 = 100.00 %

adx_signal: 142 / 200 = 71.00 %

cci_signal: 59 / 200 = 29.50 %

mfi_signal: 42 / 200 = 21.00 %

obv_signal: 200 / 200 = 100.00 %

roc_signal: 196 / 200 = 98.00 %

Regime/Gate-Mismatches:

regime_v1: 156 / 200 = 78.00 %

allow_long: 106 / 200 = 53.00 %

allow_short: 84 / 200 = 42.00 %

## Interpretation

Der Test zeigt einen klaren Source-of-Truth-Konflikt.

Die aktuell implementierten Online Builder basieren auf der GS-kompatiblen Signalquelle:

scripts/post_gs_h3_build_eth_signals_regime_gs_compat.py

Die aktuell verwendete CSV:

data/l1_full_run.csv

wurde jedoch offenbar nicht exakt mit dieser Pipeline erzeugt oder enthaelt eine spaetere/andere Transformationslogik.

## Entscheidung

Keine Integration in loop.py.

P1E blockiert die Integration der Online Builder.

Die Builder bleiben als experimentelle Basis vorhanden, duerfen aber nicht produktiv verwendet werden, solange kein erfolgreicher CSV-vs-Online-Test vorliegt.

## Naechster sinnvoller Schritt

Die exakte Erzeugung von data/l1_full_run.csv muss rekonstruiert werden.

Ohne diese Source of Truth ist eine robuste Online-Signal-Integration nicht moeglich.

## Status

P1A: PASS

P1B: PASS, aber nicht validiert gegen aktuelle CSV

P1C: PASS, aber nicht validiert gegen aktuelle CSV

P1D: PASS, aber nicht validiert gegen aktuelle CSV

P1E: FAIL

