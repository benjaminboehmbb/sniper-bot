# LIVE L1 P1 Online Readiness Plan - 2026-06-05

## Ziel

P1 schliesst den groessten verbleibenden Live-Readiness-Gap:

Aktuell arbeitet Live-L1 im Paper-Betrieb mit fertigen CSV-Spalten.

Ziel ist ein spaeterer Online-Pfad, der Signal-, Regime- und Gate-Werte live aus Marktdaten berechnet.

## Ausgangslage

Aktueller Pfad:

CSV -> market.py -> feature_snapshot.py -> intent.py -> intent_fusion.py -> execution.py

Zielpfad:

Live OHLCV -> signal_builder.py -> regime_builder.py -> gate_builder.py -> feature_snapshot.py -> intent.py -> intent_fusion.py -> execution.py

## Kritische Erkenntnis

Im Repository existieren mehrere Signalwelten:

1. Alte 0/1-Signale
2. GS-kompatible Float-Signale von -1.0 bis +1.0
3. Live-L1 Integer-Signale -1 / 0 / +1

Deshalb darf signal_builder.py nicht blind aus einer alten Datei rekonstruiert werden.

## Source-of-Truth-Entscheidung

Fuer Live-L1 Online Readiness gilt:

GS-kompatible Signalpipeline
-> anschliessende Integer-Konvertierung wie market.py / feature_snapshot.py
-> intent.py erhaelt -1 / 0 / +1

## P1 Teilmodule

### P1A Online Signal Source Definition

Dokumentiert die korrekte Signalquelle und verhindert erneute Verwechslung zwischen 0/1, Float und Integer-Signalen.

### P1B signal_builder.py

Berechnet online die 12 Signalspalten:

- rsi_signal
- macd_signal
- bollinger_signal
- ma200_signal
- stoch_signal
- atr_signal
- ema50_signal
- adx_signal
- cci_signal
- mfi_signal
- obv_signal
- roc_signal

Output muss Live-L1-kompatibel sein:

-1 / 0 / +1

### P1C regime_builder.py

Berechnet online regime_v1.

Bestaetigte Ziel-Logik:

bull:
close > ma200 and ma200_slope_1440 > 0

bear:
close < ma200 and ma200_slope_1440 < 0

side:
sonst

Output:

1 = bull
0 = side
-1 = bear

### P1D gate_builder.py

Berechnet online:

allow_long
allow_short

Bestaetigte Logik:

allow_long:
regime_v1 >= 0 and adx >= 15

allow_short:
regime_v1 == -1 and adx >= 20

### P1E CSV-vs-Online Mini-Test

Vor jeder Integration muss ein Vergleichstest gegen eine bekannte CSV erfolgen.

Testziel:

Online Builder erzeugen aus OHLCV dieselben Werte wie die aktuell verwendete CSV-Pipeline.

Keine Integration in loop.py, solange dieser Test nicht bestanden ist.

## Strikte Regeln

- Keine direkte Integration in loop.py vor erfolgreichem Mini-Test
- Keine Trading-Logik aendern
- Keine Execution-Logik aendern
- Keine parallelen Umbauten
- Code bleibt Source of Truth
- Bei Abweichungen stoppen und Ursache dokumentieren

## Aktueller Status

P1 ist gestartet.

Naechster Schritt:

P1A Source-of-Truth finalisieren und danach signal_builder.py neu aufbauen.

