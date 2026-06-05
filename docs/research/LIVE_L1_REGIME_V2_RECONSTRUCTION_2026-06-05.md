# LIVE L1 Regime V2 Reconstruction - 2026-06-05

## Befund

Die bisherige P1C-Implementierung bildet nur regime_v1 nach.

Das reicht fuer Live-L1 nicht aus.

## Echte rekonstruierte Pipeline

regime_v1
-> build_regime_v2_from_v1.py
-> regime_v2
-> gs_build_asymmetric_gate.py
-> allow_long / allow_short

## Regime v2 Logik

Quelle:

tools/build_regime_v2_from_v1.py

Kernprinzip:

- Input: regime_v1 in {-1, 0, +1}
- Output: regime_v2 in {-1, 0, +1}
- Neuer Zustand wird erst akzeptiert, wenn er mindestens min_state_bars stabil anliegt
- Default/rekonstruierter Parameter: min_state_bars = 720
- Optional: no_direct_flip

## Gate Logik

Quelle:

tools/gs_build_asymmetric_gate.py

allow_long:

regime_v2 == +1

allow_short:

regime_v2 == -1

side(0):

blockiert long und short

## Entscheidung

regime_builder.py allein ist nicht ausreichend.

Notwendig ist ein neuer Baustein:

live_l1/core/regime_v2_builder.py

Dieser muss die v2-Stabilisierung aus tools/build_regime_v2_from_v1.py exakt nachbilden.

Danach muss gate_builder.py auf regime_v2 statt regime_v1 ausgerichtet werden.

## Status

P1C alt:

regime_v1 only

P1C neu erforderlich:

regime_v1 + regime_v2

P1D alt:

Gate aus regime_v1 + adx

P1D neu erforderlich:

Gate aus regime_v2

## Naechster Schritt

regime_v2_builder.py implementieren.

Danach CSV-vs-Online-Test erneut ausfuehren.

