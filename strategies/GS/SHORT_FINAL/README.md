# Sniper-Bot — Gold-Standard SHORT FINAL

Status: FINAL / FROZEN
Datum: 2026-01-09

## Definition
Diese Datei ist die **autoritative SHORT-Endstrategie** des Gold-Standard-Pfads.
Sie wurde deterministisch aus dem vollständigen K3→K12 SHORT-Prozess erzeugt.

## Pipeline (verbindlich)
Seeds → Smoke → Analyse → Gate → Entscheidung → nächstes K

## Setup (fix)
- Engine: engine/simtraderGS.py (unverändert)
- Instrument: BTCUSDT
- Zeiteinheit: 1 Minute
- Price CSV:
  data/btcusdt_1m_2026-01-07/simtraderGS/
  btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv
- Analyse-Fenster:
  Rows: 200000
  Offsets: 0, 500000, 1000000, 1500000
- Fee (roundtrip): 0.0004
- Robustheitsmaß: roi_fee_p25 (entscheidend)

## Ergebnis
- K-Level: K12 (alle 12 Signale)
- Anzahl Strategien: 1
- Interpretation:
  Der SHORT-Endpunkt ist strukturell eindeutig.
  Einzel-ROI ist nachrangig gegenüber Robustheit über Offsets.

## Regeln
- Diese Datei ist **FROZEN**.
- Keine Änderungen, keine Gewichtungen, keine Experimente.
- Weitere Arbeiten nur in separaten, explizit benannten Pfaden.

