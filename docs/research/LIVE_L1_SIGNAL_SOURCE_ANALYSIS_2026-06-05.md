# LIVE L1 Signal Source Analysis - 2026-06-05

## Ziel

Validierung der geplanten Online-Signalberechnung fuer Live-L1.

## Ergebnis

Die Analyse hat gezeigt, dass mehrere unterschiedliche Signal-Systeme im Repository existieren.

### System A

Datei:

build_price_data_with_signals.py

Signalwerte:

0 / 1

Dieses System erzeugt einfache diskrete Signale.

Es ist NICHT die Quelle des aktuellen Live-L1 Datensatzes.

---

### System B

Datei:

scripts/post_gs_h3_build_eth_signals_regime_gs_compat.py

Signalwerte:

-1.0 bis +1.0

Die Signale werden ueber to_signal_score() erzeugt.

Dies ist das GS-kompatible Signalsystem.

---

### System C

Dateien:

live_l1/io/market.py
live_l1/core/feature_snapshot.py

Signalwerte:

Integer

Die eingelesenen Signalspalten werden ueber _to_int() verarbeitet.

Dadurch werden GS-Signale effektiv zu:

-1 / 0 / 1

konvertiert.

---

## Wichtige Erkenntnis

Der aktuelle Datensatz:

data/l1_full_run.csv

enthaelt:

-1 / 0 / 1

Signale.

Dies passt nicht zu build_price_data_with_signals.py.

Die aktuelle Live-L1 Pipeline basiert daher wahrscheinlich auf der GS-Signalkette und anschliessender Integer-Konvertierung.

---

## Test-Ergebnis

signal_builder.py Version 1:

Float-Score-Reproduktion

Nicht validiert.

signal_builder.py Version 2:

0/1-Reproduktion

Nicht validiert.

Beide Varianten reproduzieren data/l1_full_run.csv nicht ausreichend.

---

## Entscheidung

signal_builder.py wird vorerst nicht integriert.

Zuerst muss die exakte historische Quelle von data/l1_full_run.csv rekonstruiert werden.

Bis dahin bleibt:

CSV -> market.py -> feature_snapshot.py -> intent.py

Source of Truth.

